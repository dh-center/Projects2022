import asyncio
import inspect
import traceback
from typing import Tuple

import asyncpg

from APPS.logger import log
from APPS.stat_monitoring import log_exception_without_stat
from APPS.tlg.dao_layer import setup_pg_connection_pool
from APPS.tlg.emoji_bot import EMOJI

CHANNELS: Tuple[int, str] = None, None


async def get_channels_stat() -> Tuple[int, str]:
    return CHANNELS


async def set_channels():
    global CHANNELS
    try:
        overall_web = await async_get_overall_stat_web()
        overall_tlg = await async_get_overall_stat_tlg()
        overall_vk = await async_get_overall_stat_vk()

        total_web = sum(record['count'] for record in overall_web)
        total_tlg = sum(record['count'] for record in overall_tlg)
        total_vk = sum(record['count'] for record in overall_vk)

        reply = f"# {EMOJI.POINT_RIGHT} OVERALL STAT : {total_web + total_tlg}\n\n"

        reply += (
            "## Summary :\n"
            f"* **WEB** : saved_news : {total_web}, channels : {len(overall_web)} \n"
            f"* **VK** : saved_news : {total_vk}, channels : {len(overall_vk)} \n"
            f"* **TELEGRAM** : saved_news : {total_tlg}, channels : {len(overall_tlg)} \n\n\n"
        )

        reply += (
            "## Contents :\n"
            "* [**WEB**](#web_anchor) \n"
            "* [**VK**](#vk_anchor) \n"
            "* [**TELEGRAM**](#telegram_anchor)\n\n\n"
        )

        reply += f'## {EMOJI.EARTH} WEB : {total_web} <span id="web_anchor"><span>\n'
        overall_web = sorted(list(overall_web), key=lambda x: -x['count'])
        reply += "\n".join(
            f"{ind}. {channel_name} : {count}" for ind, (channel_name, count) in enumerate(overall_web, start=1)
        )

        reply += f'\n\n## {EMOJI.WEB} VK : {total_vk} <span id="vk_anchor"><span>\n'
        overall_vk = sorted(list(overall_vk), key=lambda x: -x['count'])
        reply += "\n".join(
            f"{ind}. {channel_name} : {count}" for ind, (channel_id, channel_name, count) in
            enumerate(overall_vk, start=1)
        )

        reply += f'\n\n## {EMOJI.EMAIL} TELEGRAM : {total_tlg} <span id="telegram_anchor"><span>\n'
        overall_tlg = sorted(list(overall_tlg), key=lambda x: -x['count'])
        reply += "\n".join(
            f"{ind}. {channel_name} : {count}" for ind, (channel_name, count) in enumerate(overall_tlg, start=1)
        )

        res = inspect.cleandoc(reply)
        overall_channels = len(overall_vk) + len(overall_tlg) + len(overall_web)
        CHANNELS = overall_channels, res
    except Exception as exp:
        log_exception_without_stat(f"monthly exp", exp)


async def async_get_overall_stat_web(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            found = await connection.fetch(
                f"select channel_name, count(*) as count from web_message wm "
                f"GROUP BY channel_name;"
            )
            if not found:
                return 0
        return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_get_overall_stat_web method exception {exp} {tb}")


async def async_get_overall_stat_tlg(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            found = await connection.fetch(
                f"select channel_name, count(*) as count from message m "
                f"GROUP BY channel_name;"
            )
            if not found:
                return 0
        return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_get_overall_stat_tlg method exception {exp} {tb}")


async def async_get_overall_stat_vk(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            found = await connection.fetch(
                f"select vkma.channel_id, min(vkma.screen_name) as channel_name, count(*) from vk_message vkm "
                f"JOIN vk_message_anchors vkma ON -vkm.owner_id = vkma.channel_id "
                f"GROUP BY vkma.channel_id;"
            )
            if not found:
                return 0
        return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_get_overall_stat_vk method exception {exp} {tb}")


async def reset_channels_task():
    while True:
        await set_channels()
        await asyncio.sleep(30)  # 30 seconds


asyncio.get_event_loop().create_task(reset_channels_task())
