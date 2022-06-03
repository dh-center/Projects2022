import asyncio
import datetime
import json
from typing import List, Union, Tuple, Generator, Set

import asyncpg
import dateparser

from APPS.entyties import ALL_SOURCES
from APPS.overall_utils import auto_str
from APPS.tlg.dao_layer import setup_pg_connection_pool


@auto_str
class NewsQuery:
    def __init__(
            self, must_terms=None, should_terms=None, excluded_terms=None, channels_included=None,
            channels_excluded=None, sources=None, **kwargs
    ):
        if sources is None:
            sources = []
        self.sources = sources
        if must_terms is None:
            must_terms = []
        if excluded_terms is None:
            excluded_terms = []
        if should_terms is None:
            should_terms = []
        if channels_included is None:
            channels_included = set()
        if channels_excluded is None:
            channels_excluded = set()
        self.must_terms: List[Union[str, List[str]]] = must_terms
        self.should_terms: List[Union[str, List[str]]] = should_terms
        self.excluded_terms: List[Union[str, List[str]]] = excluded_terms
        self.channels_included: Set[Tuple[str, str]] = set(tuple(el) for el in channels_included)
        self.channels_excluded: Set[Tuple[str, str]] = set(tuple(el) for el in channels_excluded)

    def get_channels_included_description(self):
        if not self.channels_included:
            return "ALL"
        return str([*self.channels_included])

    def get_channels_excluded_description(self):
        if not self.channels_excluded:
            return "ALL"
        return str([*self.channels_excluded])

    def get_sources(self):
        if not self.sources:
            return [*sorted(ALL_SOURCES)]
        else:
            return [*sorted(self.sources)]

    def get_sources_set(self):
        if not self.sources:
            return {*ALL_SOURCES}
        else:
            return {*self.sources}

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__ if not isinstance(o, set) else [*o],
            sort_keys=True, indent=2, ensure_ascii=False
        )

    @staticmethod
    def from_json(query: str):
        return NewsQuery(**json.loads(query))


@auto_str
class UserQuery:
    def __init__(
            self, user_id: int, name: str, query: NewsQuery, created_time=None, uid=None, **kwargs
    ):
        self.uid = uid
        self.created_time = created_time
        self.user_id: int = user_id
        self.name: str = name
        self.query = query
        if isinstance(created_time, str):
            self.created_time = dateparser.parse(self.created_time)
        if isinstance(query, str):
            self.query: NewsQuery = NewsQuery.from_json(query)
        if isinstance(query, dict):
            self.query: NewsQuery = NewsQuery(**query)

    def has_terms(self) -> bool:
        query = self.query
        return (len(query.must_terms) + len(query.should_terms)) > 0

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2, ensure_ascii=False)

    @staticmethod
    def from_json(query: str):
        loads = json.loads(query)
        if isinstance(loads, list): loads = loads[0]
        return UserQuery(**loads)

    async def save(self):
        self.uid, self.created_time = await save_user_query(self)

    async def exist(self) -> bool:
        if self.uid:
            return True
        return await user_query_exist(self)


@auto_str
class UserSubscription:
    def __init__(self, user_id: int, query: UserQuery, created_time=None, uid=None, **kwargs):
        self.uid: int = uid
        self.created_time: int = created_time
        self.user_id: int = user_id
        self.query: UserQuery = query
        if isinstance(query, str):
            self.query: UserQuery = UserQuery.from_json(query)

    async def save(self):
        self.uid = await save_subscription(self)


async def get_number_of_subscriptions_by_user(user_id: int) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchval("select count(*) from user_subscription where user_id = $1", user_id)
    return found


async def get_subscriptions_list(user_id: int) -> List[UserSubscription]:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """select us.*, json_agg(uq) as query
               from user_subscription us
                        join user_query uq on uq.uid = us.query_id
               where us.user_id = $1
               group by us.uid, uq.uid
               order by us.uid desc""", user_id
        )
    if found:
        return sorted((UserSubscription(**record) for record in found), reverse=True, key=lambda it: it.query.uid)
    else:
        return []


async def get_all_subscriptions_list() -> Generator[UserSubscription, None, None]:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """select us.*, json_agg(uq) as query
               from user_subscription us
                        join user_query uq on uq.uid = us.query_id
               group by us.uid, uq.uid
               order by us.uid desc"""
            # TODO add paging on generator limit 10 offset 0
        )
    if found:
        for record in found:
            yield UserSubscription(**record)


async def get_number_of_queries_by_user(user_id: int) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchval("select count(*) from user_query where user_id = $1", user_id)
    return found


async def get_queries_list(user_id: int) -> List[UserQuery]:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """select * from user_query
                where user_id = $1
                order by uid desc """, user_id
        )
    if found:
        return [UserQuery(**record) for record in found]
    else:
        return []


async def get_subscription(uid: int) -> UserSubscription:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchrow(
            """
            select us.*, json_agg(uq) as query
               from user_subscription us
                        join user_query uq on uq.uid = us.query_id
            where us.uid = $1
            group by us.uid, uq.uid
            """, uid
        )
        if found:
            return UserSubscription(**found)


async def delete_subscription(uid: int) -> bool:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchrow("delete from user_subscription where uid = $1 returning uid;", uid)
        if found:
            return True
        else:
            return False


async def delete_query(uid: int) -> bool:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetchrow("delete from user_query cascade where uid=$1 returning uid", uid)
        if found:
            return True
        else:
            return False


async def user_query_exist(query: UserQuery) -> bool:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        return await connection.fetchval(
            """
            select exists(select 1 from user_query where user_id=$1 and name=$2)
            """, query.user_id, query.name
        )


async def save_user_query(query: UserQuery) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        if not query.uid:
            return await connection.fetchrow(
                """
                insert into user_query(user_id, name, query) 
                values ($1, $2, $3) returning uid, created_time
                """, query.user_id, query.name, query.query.to_json()
            )
        else:
            return await connection.fetchrow(
                """
                update user_query
                set query = $3,
                name = $2
                where uid = $1
                returning uid, created_time
                """, query.uid, query.name, query.query.to_json()
            )


async def save_subscription(subscription: UserSubscription) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        if not subscription.uid:
            return await connection.fetchval(
                """
                insert into user_subscription(user_id, query_id) 
                values ($1, $2) returning uid
                """, subscription.user_id, subscription.query.uid
            )


async def test():
    query_list = await get_queries_list(1)
    user_query = UserQuery(
        user_id=1,
        name=f"test itmo {datetime.datetime.now()}",
        query=NewsQuery(must_terms=[["itmo", "итмо"], "университет"])
    )
    await user_query.save()
    subscription = UserSubscription(
        user_id=1,
        subscription_name="test",
        query=user_query
    )
    await subscription.save()
    # res = await subscription.save()
    # subscription.subscription_name = "test 2!!!"
    # res = await subscription.save()
    res = await get_subscriptions_list(1)
    res = await get_subscription(res[0].uid)
    print(res)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(test())
