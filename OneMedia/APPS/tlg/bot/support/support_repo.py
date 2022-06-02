import asyncio
import json
from enum import Enum, unique
from typing import List

import asyncpg

from APPS.overall_utils import auto_str
from APPS.tlg.dao_layer import setup_pg_connection_pool


@unique
class SupportType(str, Enum):
    SUPPORT = "SUPPORT"
    ADD_CHANNEL = "ADD_CHANNEL"


@auto_str
class SupportQuery:
    def __init__(self, support_type: SupportType, data):
        self.support_type = support_type
        self.data = data

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2, ensure_ascii=False)

    @staticmethod
    def from_json(meta: str):
        return SupportQuery(**json.loads(meta))


@auto_str
class SupportRequest:
    def __init__(self, user_id: int, support_query: SupportQuery, uid=None):
        self.uid: int = uid
        self.user_id: int = user_id
        self.support_query: SupportQuery = support_query
        if isinstance(support_query, str):
            self.meta: SupportQuery = SupportQuery.from_json(support_query)

    async def save(self):
        self.uid = await save_support_request(self)


async def get_support_request_by_uid(uid: int) -> SupportRequest:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchrow(
            """
            select uid, user_id, support_query from user_support_request
            where uid = $1
            """, uid
        )
        if found:
            return SupportRequest(**found)


async def get_user_support_requests(user_id: int) -> List[SupportRequest]:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """
            select uid, user_id, support_query from user_support_request
            where user_id = $1
            """, user_id
        )
        if found:
            return [SupportRequest(**record) for record in found]


async def save_support_request(support_request: SupportRequest) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        if not support_request.uid:
            return await connection.fetchval(
                """
                insert into user_support_request(user_id, support_query)
                values  ($1, $2) returning uid
                """, support_request.user_id, support_request.support_query.to_json()
            )
        else:
            return await connection.fetchval(
                """
                update user_support_request
                set support_query = $2
                where uid = $1
                returning uid
                """, support_request.uid, support_request.support_query.to_json()
            )


async def test():
    support_request = SupportRequest(
        user_id=111,
        support_query=SupportQuery(
            support_type=SupportType.SUPPORT,
            data="some data"
        )
    )
    res = await support_request.save()
    support_request.support_query = SupportQuery(
        support_type=SupportType.ADD_CHANNEL,
        data="some data 2"
    )
    res = await support_request.save()
    res = await get_user_support_requests(111)
    res = await get_support_request_by_uid(support_request.uid)
    print(res)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(test())
