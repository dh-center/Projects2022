import asyncio
import json
import os
import time
from asyncio import Task
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Union

import asyncpg
from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller

from APPS.logger import log
from APPS.stat_monitoring import async_tell_web_crawler_is_alive, EventName, async_log_exception_web
from APPS.web_crawler.utils.conn_utills import proxy_connector_params, tcp_connector_params, CLIENT_TIMEOUT
from APPS.web_crawler.utils.db_utils import setup_pg_connection_pool, WebMessageDB, get_unseen_anchors, save_to_db
from APPS.web_crawler.utils.html_xml_utils import decode_bytes_to_html, extract_update_start_link, extract_crawl_links, \
    enrich_data


@dataclass
class TaskState:
    task: Union[Task, None] = None
    start_time: int = 0


class BaseCrawler:

    def __init__(self, source_data: dict, proxy: ProxyConnector, tcp: TCPConnector):
        """Create crawler

        Keyword arguments:
        source_data -- required source data
        """
        self._name_ = source_data['name']
        self._crawl_data_ = source_data['crawl_data']
        self._update_period_ = source_data['crawl_data']['update_period']
        self._is_debug_ = source_data['crawl_data']['is_debug']
        self._requests_data_ = source_data['crawl_data']['requests_data']
        self._connector_ = proxy if source_data['crawl_data']['connector'] == 'SOCKS5' else tcp

    @property
    def name(self):
        return self._name_

    @property
    def crawl_data(self):
        return self._crawl_data_

    @property
    def update_period(self):
        return self._update_period_

    @property
    def is_debug(self):
        return self._is_debug_

    @property
    def requests_data(self):
        return self._requests_data_

    @property
    def connector(self):
        return self._connector_

    async def update_start_link(self, links_data: str, session: ClientSession):
        update_link = extract_update_start_link(links_data, self.requests_data['index'][3])
        async with session.request(method='GET',
                                   url=update_link,
                                   allow_redirects=self.requests_data['allow_redirects']) as response:
            response.raise_for_status()
            return await response.text()

    async def crawl(self, pool):
        """Crawl

        Keyword arguments:
        pool -- postgres connection pool
        """

        cookies = self.requests_data.get('cookies') if self.requests_data.get('cookies') else {}
        headers = self.requests_data['headers']
        headers['User-Agent'] = UserAgent().random

        async with ClientSession(
                connector=self.connector,
                headers=headers,
                cookies=cookies,
                connector_owner=False,
                timeout=CLIENT_TIMEOUT
        ) as session:
            try:
                async with session.request(
                        method='GET',
                        url=self.requests_data['start_link'],
                        allow_redirects=self.requests_data['allow_redirects'],
                ) as response:
                    response.raise_for_status()
                    try:
                        links_data = await response.text()
                    except UnicodeDecodeError as exp:
                        if self.crawl_data.get('decode'):
                            content_byte = await response.read()
                            links_data = decode_bytes_to_html(content_byte, self.crawl_data['decode'])
                        else:
                            await async_log_exception_web(
                                pool, self.name, EventName.DECODE_TEXT_EXCEPTION,
                                msg=f"Start link: {self.requests_data['start_link']}"
                                    f" decode exception",
                                exp=exp
                            )
                all_crawl_links = {}
                try:
                    if self.requests_data.get('update_start'):
                        links_data = await self.update_start_link(links_data, session)
                    extract_crawl_links(
                        type_page=self.requests_data['type'],
                        extract_page=links_data,
                        crawl_data=self.crawl_data,
                        index=self.requests_data['index'][:3],
                        all_crawl_links=all_crawl_links
                    )
                except Exception as exp:
                    await async_log_exception_web(
                        pool, self.name, EventName.EXTRACT_EXCEPTION,
                        msg=f"extract link exception", exp=exp
                    )

                unseen_anchors = await get_unseen_anchors(pool=pool, anchors=all_crawl_links.keys())
                all_news_data = {anchor: all_crawl_links[anchor] for anchor in unseen_anchors}

                found_news = {}
                for link, val in all_news_data.items():
                    if link.startswith(self.crawl_data.get('exception_links', 'None')):
                        continue
                    try:
                        async with session.request(
                                method='GET',
                                url=link,
                                headers=headers,
                                allow_redirects=self.requests_data['allow_redirects']
                        ) as response:
                            response.raise_for_status()
                            try:
                                val['html_page'] = await response.text()
                            except UnicodeDecodeError as exp:
                                if self.crawl_data.get('decode'):
                                    content_byte = await response.read()
                                    val['html_page'] = decode_bytes_to_html(content_byte, self.crawl_data['decode'])
                                else:
                                    await async_log_exception_web(pool, self.name, EventName.DECODE_TEXT_EXCEPTION,
                                                                  msg=f"decode exception: {link}", exp=exp)
                                    continue
                    except Exception as exp:
                        await async_log_exception_web(pool, self.name, EventName.CONNECTION_EXCEPTION,
                                                      msg=f"get text exception", exp=exp)
                        continue
                    try:
                        found_news[link] = val
                        enrich_data(page_data=val, crawl_data=self.crawl_data, channel_name=self.name, link=link)
                    except Exception as exp:
                        await async_log_exception_web(
                            pool, self.name, EventName.PARSING_EXCEPTION,
                            msg=f"parse exception",
                            exp=exp
                        )
                        continue

                # save_to_db(found_news)
                db_save_list = []
                for link, val in found_news.items():
                    db_save_list.append(
                        WebMessageDB(
                            META_IMAGE=val.get('meta_image', None),
                            LINK=link,
                            CHANNEL_NAME=self.name,
                            SENDER_NAME=val.get("author", ""),
                            PUBLISH_DATE=val.get('pubDate', str(datetime.now())),
                            CONTENT=val['content'],
                            HTML_PAGE=val.get('html_page', ""),
                            TITLE=val.get('title', "")
                        )
                    )
                await save_to_db(pool, db_save_list)

            except Exception as exp:
                await async_log_exception_web(pool, self.name, EventName.EXCEPTION, msg=f"Unknow exception", exp=exp)


CRAWLING_PERIOD_IN_SECONDS = 2


async def run_web_crawlers(active_crawlers: List):
    # setup Postgres connection pool
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()

    # get socks5/tcp connectors and connection pool
    proxy_connector = ProxyConnector.from_url('socks5://127.0.0.1:9050', **proxy_connector_params)
    tcp_connector = TCPConnector(**tcp_connector_params)

    # to keep crawling state
    crawling_state: Dict[BaseCrawler, TaskState] = {
        BaseCrawler(crawler, proxy=proxy_connector, tcp=tcp_connector): TaskState(task=None, start_time=0)
        for crawler in active_crawlers
    }

    # run crawling
    while True:

        # get tor connection
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="pass")
            controller.signal(Signal.NEWNYM)

        for crawler, state in crawling_state.items():
            await async_tell_web_crawler_is_alive(pool=pool, msg=f"Checking crawler : {crawler.name}")
            now = time.time()
            if not state.task or (state.task.done() and now - state.start_time > crawler.update_period):
                log(f"Create task {crawler.name}, prev run :{state.start_time}, now : {int(now)}")
                crawling_state[crawler] = TaskState(
                    task=asyncio.create_task(crawl_try(crawler=crawler, pool=pool)),
                    start_time=int(time.time())
                )
            await asyncio.sleep(CRAWLING_PERIOD_IN_SECONDS)

        await async_tell_web_crawler_is_alive(pool=pool, msg="Alive")


async def crawl_try(crawler: BaseCrawler, pool: asyncpg.pool.Pool):
    try:
        await asyncio.wait_for(crawler.crawl(pool=pool), 60 * 15)
    except Exception as exp:
        await async_log_exception_web(
            pool=pool,
            channel_name="OneMedia:WEB:ALL", event_name=EventName.EXCEPTION,
            msg="Exception on crawl invocation", exp=exp
        )


if __name__ == "__main__":

    # Run some one crawler
    # ACTIVE_CRAWLERS = []
    # with open('../data_for_crawling/Комсомольская правда. Липецк. Новости/Комсомольская правда. Липецк. Новости.json') as file:
    #     ACTIVE_CRAWLERS.append(json.load(file))

    # Run all crawlers
    ACTIVE_CRAWLERS = []
    for data in os.listdir('../data_for_crawling'):
        with open('../data_for_crawling/' + data + '/' + data + '.json') as file:
            ACTIVE_CRAWLERS.append(json.load(file))

    asyncio.run(run_web_crawlers(ACTIVE_CRAWLERS))
