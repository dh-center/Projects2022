from dataclasses import dataclass
from datetime import datetime
from typing import List, Iterable

import asyncpg
import dateparser

from APPS.stat_monitoring import Source, EventName, async_log_exception_web_connection, \
    async_stat_connection
from APPS.web_crawler.utils.html_xml_utils import content_filter
from PROPERTIES.DB_PROPERTY import DB_PROPERTIES


async def setup_pg_connection_pool() -> asyncpg.pool.Pool:
    return await asyncpg.create_pool(
        max_size=15,
        database=DB_PROPERTIES.database, user=DB_PROPERTIES.user, password=DB_PROPERTIES.password,
        host=DB_PROPERTIES.host
    )


@dataclass
class WebMessageDB:
    LINK: str
    CHANNEL_NAME: str
    SENDER_NAME: str
    PUBLISH_DATE: str
    TITLE: str
    CONTENT: str
    HTML_PAGE: str
    META_IMAGE: str = None


# TODO optimize code here
async def get_unseen_anchors(pool: asyncpg.pool.Pool, anchors: Iterable[str]) -> \
        List[str]:
    res = []
    connection: asyncpg.connection
    async with pool.acquire() as connection:
        for anchor in anchors:
            found = await connection.fetchval(
                'SELECT count(anchor) FROM web_message_anchors WHERE anchor = $1;',
                anchor
            )
            if not found:
                res.append(anchor)
    return res


# TODO optimize add many at once
async def save_to_db(pool: asyncpg.pool.Pool, web_messages: List[WebMessageDB]):
    connection: asyncpg.connection
    if not web_messages:
        return
    saved = 0
    async with pool.acquire() as connection:
        for message in web_messages:
            try:
                async with connection.transaction():
                    # put news anchors
                    query = 'INSERT INTO WEB_MESSAGE_ANCHORS(ANCHOR, CHANNEL_NAME, CRAWL_DATE) ' \
                            'VALUES ($1, $2, current_timestamp);'
                    await connection.execute(query, message.LINK, message.CHANNEL_NAME)

                    # put news
                    query = 'INSERT INTO WEB_MESSAGE(LINK, CHANNEL_NAME, SENDER_NAME, PUBLISH_DATE, CONTENT, TITLE, HTML_PAGE, META_IMAGE) ' \
                            'VALUES ($1, $2, $3, $4, $5, $6, $7, $8);'
                    date_parsed = dateparser.parse(message.PUBLISH_DATE)
                    await connection.execute(
                        query,
                        message.LINK, message.CHANNEL_NAME, message.SENDER_NAME,
                        date_parsed if date_parsed else datetime.now(),
                        # TODO add later if needed message.HTML_PAGE
                        #  content_filter(message.CONTENT), message.TITLE, message.HTML_PAGE, message.META_IMAGE
                        content_filter(message.CONTENT), message.TITLE, '', message.META_IMAGE
                    )
                    saved += 1
            except Exception as exp:
                await async_log_exception_web_connection(
                    connection,
                    channel_name=message.CHANNEL_NAME,
                    event_name=EventName.DB_EXCEPTION,
                    msg="Exception on save to DB",
                    exp=exp
                )
        if saved:
            await async_stat_connection(
                connection, source=Source.WEB, channel_name=web_messages[0].CHANNEL_NAME, event_name=EventName.SAVE_NEWS,
                count=saved
            )
