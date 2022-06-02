import asyncio
import json
from typing import Dict, Any, Union, List

import asyncpg
from aiohttp import ClientSession

from APPS.logger import log_exp
from APPS.tlg.jwt_provider import JWT_HEADER_NAME, get_jwt
from PROPERTIES.DB_PROPERTY import DB_PROPERTIES
from PROPERTIES.SEARCH_PROPERTIES import SEARCH_PROPERTIES

SEARCH_INDEX_URL: str = f"http://{SEARCH_PROPERTIES.host}:{SEARCH_PROPERTIES.port}"


async def get_search_alive_status() -> Union[Dict[str, Any], None]:
    async with ClientSession() as session:
        try:
            response = await session.get(url=f"{SEARCH_INDEX_URL}/alive")
            response.raise_for_status()
            text = await response.text()
            json_dict = json.loads(text)
        except Exception as exp:
            log_exp("Search.get_alive_stat()", exp)
            return None
    return json_dict


async def search_by_terms(
        pool: asyncpg.pool.Pool,
        must_terms: Union[List[str], None] = None,
        should_terms: Union[List[str], None] = None,
        number_of_best_hits: int = 20
) -> Union[List[Dict[str, Any]], None]:
    async with ClientSession() as session:
        try:
            query = {
                "number_of_best_hits": number_of_best_hits
            }
            if must_terms:
                query['contentDocTermsMust'] = [{"synonyms": [term]} for term in must_terms]
            if should_terms:
                query['contentDocTermsShould'] = [{"synonyms": [term]} for term in should_terms]

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


async def search_lucene_query(
        pool: asyncpg.pool.Pool,
        query_str: str,
        number_of_best_hits: int = 20
) -> Union[List[Dict[str, Any]], None]:
    async with ClientSession() as session:
        try:
            query = {
                'contentLuceneQuery': query_str,
                "number_of_best_hits": number_of_best_hits
            }

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


def to_list_of_terms(term):
    if isinstance(term, list):
        return term
    return [term]


async def enrich_from_db(val: Dict[str, Any], pool: asyncpg.pool.Pool):
    uid = val['uid']
    source = val['source']
    async with pool.acquire() as connection:
        if source.lower() == 'tlg':
            result = await connection.fetchrow(
                "SELECT * FROM message WHERE uid = $1;", uid
            )
            val['content'] = result['content']
            val['meta_image'] = result.get('meta_image', None)
            val['link'] = fr"https://t.me/{result['channel_name']}/{result['message_id']}"
        elif source.lower() == 'web':
            result = await connection.fetchrow(
                "SELECT * FROM web_message WHERE uid = $1;", uid
            )
            val['content'] = result['content']
            val['meta_image'] = result.get('meta_image', None)
            val['link'] = result['link']
        elif source.lower() == 'vk':
            result = await connection.fetchrow(
                """
                    select vm.message_id,
                       vm.owner_id,
                       vm.from_id,
                       vm.message_content,
                       vm.publish_date,
                       vm.meta_image,
                       vm.uid,
                       vm.created_time,
                       vma.channel_name,
                       vma.channel_id,
                       vma.screen_name,
                       vma.participants
                from vk_message vm
                         join vk_message_anchors vma on -vma.channel_id = vm.owner_id
                where vm.uid = $1
                """, uid
            )
            val['content'] = result['message_content']
            val['meta_image'] = result.get('meta_image', None)
            val['link'] = fr"https://vk.com/{result['screen_name']}?w=wall{result['owner_id']}_{result['message_id']}"
    return val


async def main():
    alive_status = await get_search_alive_status()
    print(alive_status)
    pool = await asyncpg.create_pool(
        database=DB_PROPERTIES.database, user=DB_PROPERTIES.user, password=DB_PROPERTIES.password,
        host=DB_PROPERTIES.host
    )
    search_result = await search_by_terms(pool, ["итмо"], pool)
    print(search_result)


if __name__ == '__main__':
    asyncio.run(main())
