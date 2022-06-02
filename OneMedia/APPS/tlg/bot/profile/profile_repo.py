import asyncio
import datetime
import json
from typing import Set

import asyncpg

from APPS.overall_utils import auto_str
from APPS.tlg.dao_layer import setup_pg_connection_pool


@auto_str
class UserMetaData:
    def __init__(self, last_recorded_activity: str = str(datetime.datetime.now()), enable_subscription: bool = True):
        self.enable_subscription = enable_subscription
        self.last_recorded_activity = last_recorded_activity

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2, ensure_ascii=False)

    @staticmethod
    def from_json(meta: str):
        return UserMetaData(**json.loads(meta))


@auto_str
class UserInfo:
    def __init__(self, user_id: int, name: str, meta: UserMetaData, phone: str = None, uid=None, login: str = None):
        self.uid: int = uid
        self.user_id: int = user_id
        self.name: str = name
        self.login: str = login
        self.phone: str = phone
        self.meta: UserMetaData = meta
        if isinstance(meta, str):
            self.meta: UserMetaData = UserMetaData.from_json(meta)

    async def save(self):
        self.uid = await save_user_info(self)


async def get_user_info_by_uid(uid: int) -> UserInfo:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchrow(
            """
            select uid, user_id, name, phone, meta from user_info
            where uid = $1
            """, uid
        )
        if found:
            return UserInfo(**found)


async def get_user_info_by_user_id(user_id: int) -> UserInfo:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchrow(
            """
            select uid, user_id, name, phone, meta, login from user_info
            where user_id = $1
            """, user_id
        )
        if found:
            return UserInfo(**found)


async def save_user_info(user_info: UserInfo) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        if not user_info.uid:
            return await connection.fetchval(
                """
                insert into user_info(user_id, name, phone, meta, login)
                values  ($1, $2, $3, $4, $5) returning uid
                """, user_info.user_id, user_info.name, user_info.phone, user_info.meta.to_json(), user_info.login
            )
        else:
            return await connection.fetchval(
                """
                update user_info
                set name = $2, phone = $3, meta = $4, login = $5
                where uid = $1
                returning uid
                """, user_info.uid, user_info.name, user_info.phone, user_info.meta.to_json(), user_info.login
            )


async def get_enabled_overall_subscriptions_user_set() -> Set[int]:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """
            select user_id
            from user_info
            where cast(user_info.meta ->> 'enable_subscription' as bool) = True
            """
        )
        return {int(record['user_id']) for record in found}


async def test():
    user_info = UserInfo(
        user_id=3,
        name="test",
        meta=UserMetaData(),
        login="test"
    )
    res = await user_info.save()
    user_info.name = "test 2!!!"
    user_info.login = "test 2!!!"
    res = await user_info.save()
    res = await get_user_info_by_uid(123213)
    print(res)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(test())
