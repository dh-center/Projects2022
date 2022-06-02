import json

import asyncpg

from APPS.logger import log_exp
from APPS.overall_utils import auto_str
from APPS.tlg.dao_layer import setup_pg_connection_pool


@auto_str
class UserAction:
    def __init__(self, user_id: int, name: str, data=None, uid=None):
        if data is None:
            data = {}
        self.uid: int = uid
        self.user_id: int = user_id
        self.name: str = name
        self.data = data
        if isinstance(data, str):
            self.data: dict = json.loads(data)

    async def log(self):
        try:
            await self._save()
        except Exception as exp:
            log_exp("log_user_action exception", exp)

    async def _save(self):
        self.uid = await save_user_action(self)


async def save_user_action(user_action: UserAction) -> int:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        if not user_action.uid:
            return await connection.fetchval(
                """
                insert into user_action_log(user_id, name, data)
                values  ($1, $2, $3) returning uid
                """, user_action.user_id, user_action.name,
                json.dumps(user_action.data, default=lambda o: o.__dict__, sort_keys=True, indent=2, ensure_ascii=False)
            )
