import asyncio
from datetime import datetime
from typing import Dict, List, Union, Any

import asyncpg
from aiohttp import ClientSession
from telethon import Button

from APPS.logger import log_exp
from APPS.search_utils import search_by_terms, SEARCH_INDEX_URL, enrich_from_db
from APPS.search_utils import search_lucene_query
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.subscription.subscription_repo import UserQuery
from APPS.tlg.dao_layer import setup_pg_connection_pool
from APPS.tlg.jwt_provider import JWT_HEADER_NAME, get_jwt


async def search_simple_query(event, query=None):
    try:
        if not query:
            msg: str = event.message.message
            query = msg[msg.index("gsearch_simple_of") + len('#gsearch_simple_of'):].strip().lower()
        pool = await setup_pg_connection_pool()
        results = await search_lucene_query(
            pool=pool,
            query_str=query
        )
        if results is None:
            results = []
        for val in results:
            message = f"<b>source</b>    : {val['source']}" \
                      f"\n<b>channel_name</b>    : {val.get('channel_name', '')}:" \
                      f"\n<b>channel_title</b>    : {val.get('channel_title', '')}:" \
                      f"\n<b>channel_display_name</b>    : {val.get('channel_display_name', '')}:" \
                      f"\n<b>participants</b>     : {val.get('participants', None)}" \
                      f"\n<b>meta_image</b>     : {val.get('meta_image', None)}" \
                      f"\n<b>created_time</b>     : {datetime.utcfromtimestamp(val['created_time'] / 1000):%Y-%m-%d %H:%M} (UTC)" \
                      f"\n<b>score</b>     : {val['score']}" \
                      f"\n<b>uid</b>    : {val['uid']}" \
                      f"\n<b>content</b>    : {val['content']}"[:4090]
            await BOT.send_message(
                event.chat_id,
                message,
                parse_mode='html',
                buttons=Button.url("Открыть новость", url=val['link'])
            )
        overall = "\n".join(
            f"* **source**: {el['source']}, **uid**: {el['uid']}, **score**: {el['score']}" for el in results)
        await event.reply(f"Результаты ({len(results)} best hits) : \n{overall}")
    except Exception as exp:
        log_exp("gsearch exception", exp)


async def search_by_query(event, query):
    try:
        pool = await setup_pg_connection_pool()
        results = await search_query(
            pool=pool,
            user_query=query
        )
        if results is None:
            results = []
        for val in results:
            message = f"<b>source</b>    : {val['source']}" \
                      f"\n<b>channel_name</b>    : {val.get('channel_name', '')}:" \
                      f"\n<b>channel_title</b>    : {val.get('channel_title', '')}:" \
                      f"\n<b>channel_display_name</b>    : {val.get('channel_display_name', '')}:" \
                      f"\n<b>participants</b>     : {val.get('participants', None)}" \
                      f"\n<b>meta_image</b>     : {val.get('meta_image', None)}" \
                      f"\n<b>created_time</b>     : {datetime.utcfromtimestamp(val['created_time'] / 1000):%Y-%m-%d %H:%M} (UTC)" \
                      f"\n<b>score</b>     : {val['score']}" \
                      f"\n<b>uid</b>    : {val['uid']}" \
                      f"\n<b>content</b>    : {val['content']}"[:4090]
            await BOT.send_message(
                event.chat_id,
                message,
                parse_mode='html',
                buttons=Button.url("Открыть новость", url=val['link'])
            )
        overall = "\n".join(
            f"* **source**: {el['source']}, **uid**: {el['uid']}, **score**: {el['score']}" for el in results)
        await event.reply(f"Результаты ({len(results)} best hits) : \n{overall}")
    except Exception as exp:
        log_exp("gsearch exception", exp)


def to_list_of_terms(term):
    if isinstance(term, list):
        return term
    return [term]


async def search_query(
        pool: asyncpg.pool.Pool,
        user_query: UserQuery,
        number_of_best_hits: int = 20
) -> Union[List[Dict[str, Any]], None]:
    async with ClientSession() as session:
        try:
            query = {
                "number_of_best_hits": number_of_best_hits,
            }
            search_query = user_query.query
            if search_query.must_terms:
                query['contentDocTermsMust'] = [{"synonyms": to_list_of_terms(term)} for term in
                                                search_query.must_terms]
            if search_query.should_terms:
                query['contentDocTermsShould'] = [{"synonyms": to_list_of_terms(term)} for term in
                                                  search_query.should_terms]
            if search_query.excluded_terms:
                query['contentDocTermsExcluded'] = [{"synonyms": to_list_of_terms(term)} for term in
                                                    search_query.excluded_terms]

            if search_query.channels_included:
                query['channelNamesIncluded'] = [{"source": source, "channelName": channel_name} for
                                                 source, channel_name in search_query.channels_included]

            if search_query.channels_excluded:
                query['contentDocTermsExcluded'] = [{"source": source, "channelName": channel_name} for
                                                    source, channel_name in search_query.channels_excluded]
            if search_query.sources:
                query['sources'] = list(search_query.sources)

            response = await session.post(
                url=f"{SEARCH_INDEX_URL}/search",
                headers={JWT_HEADER_NAME: get_jwt("bot")},
                json=query
            )
            response.raise_for_status()
            json_dict = await response.json()
            enriched = await asyncio.gather(*[enrich_from_db(el, pool) for el in json_dict])
        except Exception as exp:
            log_exp("Search.get_alive_stat()", exp)
            return None
    return enriched


async def gsearch_all_of(event, terms=None):
    try:
        must_terms = terms
        if not terms:
            msg: str = event.message.message
            must_terms = msg[msg.index("gsearch_all_of") + len('#gsearch_all_of'):].strip().split(",")
        must_terms = [term.strip() for term in must_terms]
        pool = await setup_pg_connection_pool()
        results = await search_by_terms(
            pool=pool,
            must_terms=must_terms
        )
        if results is None:
            results = []
        for val in results:
            message = f"<b>source</b>    : {val['source']}" \
                      f"\n<b>channel_name</b>    : {val.get('channel_name', '')}:" \
                      f"\n<b>channel_title</b>    : {val.get('channel_title', '')}:" \
                      f"\n<b>channel_display_name</b>    : {val.get('channel_display_name', '')}:" \
                      f"\n<b>participants</b>     : {val.get('participants', None)}" \
                      f"\n<b>meta_image</b>     : {val.get('meta_image', None)}" \
                      f"\n<b>created_time</b>     : {datetime.utcfromtimestamp(val['created_time'] / 1000):%Y-%m-%d %H:%M} (UTC)" \
                      f"\n<b>score</b>     : {val['score']}" \
                      f"\n<b>uid</b>    : {val['uid']}" \
                      f"\n<b>content</b>    : {val['content']}"[:4090]
            await BOT.send_message(
                event.chat_id,
                message,
                parse_mode='html',
                buttons=Button.url("Открыть новость", url=val['link'])
            )
        overall = "\n".join(
            f"* **source**: {el['source']}, **uid**: {el['uid']}, **score**: {el['score']}" for el in results)
        await event.reply(f"Результаты ({len(results)} best hits) : \n{overall}")
    except Exception as exp:
        log_exp("gsearch exception", exp)


async def gsearch_any_of(event, terms=None):
    try:
        should_terms = terms
        if not terms:
            msg: str = event.message.message
            should_terms = msg[msg.index("gsearch_any_of") + len('#gsearch_any_of'):].strip().split(",")
        should_terms = [term.strip() for term in should_terms]
        pool = await setup_pg_connection_pool()
        results = await search_by_terms(
            pool=pool,
            should_terms=should_terms
        )
        for val in results:
            message = f"<b>source</b>    : {val['source']}" \
                      f"\n<b>channel_name</b>    : {val.get('channel_name', '')}:" \
                      f"\n<b>channel_title</b>    : {val.get('channel_title', '')}:" \
                      f"\n<b>channel_display_name</b>    : {val.get('channel_display_name', '')}:" \
                      f"\n<b>participants</b>     : {val.get('participants', None)}" \
                      f"\n<b>meta_image</b>     : {val.get('meta_image', None)}" \
                      f"\n<b>created_time</b>     : {datetime.utcfromtimestamp(val['created_time'] / 1000):%Y-%m-%d %H:%M} (UTC)" \
                      f"\n<b>score</b>     : {val['score']}" \
                      f"\n<b>uid</b>    : {val['uid']}" \
                      f"\n<b>content</b>    : {val['content']}"[:4090]
            await BOT.send_message(
                event.chat_id,
                message,
                parse_mode='html',
                buttons=Button.url("Открыть новость", url=val['link'])
            )
        overall = "\n".join(
            f"* **source**: {el['source']}, **uid**: {el['uid']}, **score**: {el['score']}" for el in results)
        await event.reply(f"Результаты ({len(results)} best hits) : \n{overall}")
    except Exception as exp:
        log_exp("gsearch exception", exp)
