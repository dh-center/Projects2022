import datetime
import traceback
from enum import Enum

import asyncpg
from psycopg2.pool import ThreadedConnectionPool

from APPS.logger import log
from PROPERTIES.DB_PROPERTY import DB_PROPERTIES

PG_ASYNC_POOL: asyncpg.pool.Pool = None

log("STATS ARE IMPORTED!")


async def setup_pg_connection_pool() -> asyncpg.pool.Pool:
    global PG_ASYNC_POOL
    if not PG_ASYNC_POOL:
        PG_ASYNC_POOL = await asyncpg.create_pool(
            database=DB_PROPERTIES.database, user=DB_PROPERTIES.user, password=DB_PROPERTIES.password,
            host=DB_PROPERTIES.host
        )
    return PG_ASYNC_POOL


class Source(Enum):
    TLG = 1
    VK = 2
    WEB = 3


class EventName(Enum):
    SAVE_NEWS = 1
    PARSING_EXCEPTION = 2
    CONNECTION_EXCEPTION = 3
    DB_EXCEPTION = 4
    EXCEPTION = 5
    EXTRACT_EXCEPTION = 6
    DECODE_TEXT_EXCEPTION = 7


POOL = ThreadedConnectionPool(
    user=DB_PROPERTIES.user,
    password=DB_PROPERTIES.password,
    host=DB_PROPERTIES.host,
    port=DB_PROPERTIES.port,
    database=DB_PROPERTIES.database,
    maxconn=DB_PROPERTIES.connections,
    minconn=1
)


def log_errors(source: Source, channel_name: str, event_name: EventName, msg: str):
    log(f"Msg : {msg} {source.name}->{channel_name}->{event_name.name}")
    stat(source, channel_name, event_name)


def log_exception(source: Source, channel_name: str, event_name: EventName, msg: str, exp: Exception):
    tb = "".join(traceback.TracebackException.from_exception(exp).format())
    log(f"Msg : {msg} {source.name}->{channel_name}->{event_name.name} {exp} {tb}")
    stat(source, channel_name, event_name)


def log_exception_without_stat(msg: str, exp: Exception):
    tb = "".join(traceback.TracebackException.from_exception(exp).format())
    log(f"Exp : {msg} {exp} {tb}")


def log_exception_web(channel_name: str, event_name: EventName, msg: str, exp: Exception):
    log_exception(Source.WEB, channel_name, event_name, msg, exp)


async def async_log_exception(
        pool: asyncpg.pool.Pool, source: Source, channel_name: str, event_name: EventName, msg: str, exp: Exception
):
    tb = "".join(traceback.TracebackException.from_exception(exp).format())
    log(f"Msg : {msg} {source.name}->{channel_name}->{event_name.name} {exp} {tb}")
    await async_stat(pool, source, channel_name, event_name)


async def async_log_exception_connection(
        connection, source: Source, channel_name: str, event_name: EventName, msg: str, exp: Exception
):
    tb = "".join(traceback.TracebackException.from_exception(exp).format())
    log(f"Msg : {msg} {source.name}->{channel_name}->{event_name.name} {exp} {tb}")
    await async_stat_connection(connection, source, channel_name, event_name)


async def async_log_exception_web(
        pool: asyncpg.pool.Pool, channel_name: str, event_name: EventName, msg: str, exp: Exception
):
    await async_log_exception(pool, Source.WEB, channel_name, event_name, msg, exp)


async def async_log_exception_web_connection(
        connection, channel_name: str, event_name: EventName, msg: str, exp: Exception
):
    await async_log_exception_connection(connection, Source.WEB, channel_name, event_name, msg, exp)


def stat(source: Source, channel_name: str, event_name: EventName, count: int = 1):
    connection = None
    cursor = None
    try:
        connection = POOL.getconn()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO STAT (SOURCE, CHANNEL_NAME, EVENT_NAME, COUNT) VALUES (%s, %s, %s, %s)",
            (source.name, channel_name, event_name.name, count)
        )
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : stat() method exception {exp} {tb}")
    finally:
        if connection:
            connection.commit()
            cursor.close()
            POOL.putconn(connection)


async def async_stat(pool: asyncpg.pool.Pool, source: Source, channel_name: str, event_name: EventName, count: int = 1):
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO STAT (SOURCE, CHANNEL_NAME, EVENT_NAME, COUNT) VALUES ($1, $2, $3, $4)",
                source.name, channel_name, event_name.name, count
            )
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_stat() method exception {exp} {tb}")


async def async_stat_connection(connection, source: Source, channel_name: str, event_name: EventName, count: int = 1):
    try:
        await connection.execute(
            "INSERT INTO STAT (SOURCE, CHANNEL_NAME, EVENT_NAME, COUNT) VALUES ($1, $2, $3, $4)",
            source.name, channel_name, event_name.name, count
        )
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_stat() method exception {exp} {tb}")


async def async_get_period_stat(
        source: Source, channel_name: str, event_name: EventName, period: str, pool: asyncpg.pool.Pool = None,
) -> int:
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            cond_source = f"AND SOURCE = {source.name} " if source else ""
            cond_channel = f"AND CHANNEL_NAME = {channel_name} " if channel_name else ""
            cond_event_name = f"AND EVENT_NAME = {event_name.name} " if event_name else ""
            found = await connection.fetch(
                f"SELECT SOURCE, CHANNEL_NAME, EVENT_NAME, sum(STAT.COUNT) FROM STAT WHERE CREATED_TIME >= 'now'::timestamp - '{period}'::interval " +
                cond_source + cond_channel + cond_event_name +
                "GROUP BY SOURCE, CHANNEL_NAME, EVENT_NAME;",
            )
            if not found:
                return 0
        return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_get_{period}_stat() method exception {exp} {tb}")


async def async_get_month_stat(
        source: Source = None, channel_name: str = None, event_name: EventName = None, pool: asyncpg.pool.Pool = None
) -> int:
    return await async_get_period_stat(source, channel_name, event_name, period="1 month", pool=pool)


async def async_get_day_stat(
        source: Source = None, channel_name: str = None, event_name: EventName = None, pool: asyncpg.pool.Pool = None
) -> int:
    return await async_get_period_stat(source, channel_name, event_name, period="1 day", pool=pool)


async def async_get_hour_stat(
        source: Source = None, channel_name: str = None, event_name: EventName = None, pool: asyncpg.pool.Pool = None
) -> int:
    return await async_get_period_stat(source, channel_name, event_name, period="1 hour", pool=pool)


async def async_get_ten_minutes_stat(
        source: Source = None, channel_name: str = None, event_name: EventName = None, pool: asyncpg.pool.Pool = None
) -> int:
    return await async_get_period_stat(source, channel_name, event_name, period="10 minutes", pool=pool)


async def async_get_3hours_stat(
        source: Source = None, channel_name: str = None, event_name: EventName = None, pool: asyncpg.pool.Pool = None
) -> int:
    return await async_get_period_stat(source, channel_name, event_name, period="3 hours", pool=pool)


async def async_get_overall_stat_web(pool: asyncpg.pool.Pool = None) -> int:
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


async def async_get_overall_stat_tlg(pool: asyncpg.pool.Pool = None) -> int:
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


async def async_get_overall_stat_vk(pool: asyncpg.pool.Pool = None) -> int:
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


class AppName(Enum):
    TLG_EXTRACTOR = 1
    TLG_BOT = 2
    WEB_CRAWLER = 3
    VK_EXTRACTOR = 4


async def async_tell_i_am_alive(app_name: AppName, msg: str = "", pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            await connection.execute(
                f"UPDATE STAT_ALIVE SET update_time=$1, msg=$2 WHERE app_name = $3;",
                datetime.datetime.now(), msg, app_name.name
            )
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_tell_i_am_alive method exception {exp} {tb}")


async def async_tell_web_crawler_is_alive(msg: str = "", pool: asyncpg.pool.Pool = None):
    return await async_tell_i_am_alive(app_name=AppName.WEB_CRAWLER, msg=msg, pool=pool)


def tell_i_am_alive(app_name: AppName, msg: str = ""):
    connection = None
    cursor = None
    try:
        connection = POOL.getconn()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE STAT_ALIVE SET update_time=%s, msg=%s WHERE app_name = %s;",
            (datetime.datetime.now(), msg, app_name.name)
        )
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : stat() method exception {exp} {tb}")
    finally:
        if connection:
            connection.commit()
            cursor.close()
            POOL.putconn(connection)


def tell_extractor_is_alive(msg: str = ""):
    return tell_i_am_alive(app_name=AppName.TLG_EXTRACTOR, msg=msg)


def tell_vk_extractor_is_alive(msg: str = ""):
    return tell_i_am_alive(app_name=AppName.VK_EXTRACTOR, msg=msg)


def get_alive_stat(app_name: AppName):
    connection = None
    cursor = None
    try:
        connection = POOL.getconn()
        cursor = connection.cursor()
        cursor.execute("SELECT update_time, msg FROM stat_alive WHERE app_name = %s;", (app_name.name,))
        found = cursor.fetchone()
        return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : stat() method exception {exp} {tb}")
    finally:
        if connection:
            connection.commit()
            cursor.close()
            POOL.putconn(connection)


async def async_get_alive_stat(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            found = await connection.fetch("SELECT app_name, update_time, msg FROM stat_alive;")
            return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_tell_i_am_alive method exception {exp} {tb}")


async def async_get_db_file_size_info(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            found = await connection.fetch(
                "select pgd.datname AS db_name, pg_size_pretty(pg_database_size(pgd.datname)) as db_size "
                "from pg_database pgd "
                "where pgd.datname = 'postgres';"
            )
            return found
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_get_db_file_size_info method exception {exp} {tb}")


async def async_get_db_connections_count(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    try:
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            overall_connections = await connection.fetchval(
                "SELECT count(*) FROM pg_stat_activity"
            )
            set_application_name_connections = await connection.fetchval(
                """SELECT count(*) FROM pg_stat_activity
                where query like 'SET application_name %'"""
            )
            return overall_connections, set_application_name_connections
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log(f"Msg : async_get_db_connections_count method exception {exp} {tb}")
