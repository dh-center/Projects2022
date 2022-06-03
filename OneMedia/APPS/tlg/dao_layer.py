import random
import time
import traceback

import asyncpg
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from APPS.logger import log
from APPS.stat_monitoring import stat, Source, EventName, log_exception
from PROPERTIES.DB_PROPERTY import DB_PROPERTIES

PG_ASYNC_POOL: asyncpg.pool.Pool = None

log("DAO IS IMPORTED!")


async def setup_pg_connection_pool() -> asyncpg.pool.Pool:
    global PG_ASYNC_POOL
    if not PG_ASYNC_POOL:
        PG_ASYNC_POOL = await asyncpg.create_pool(
            database=DB_PROPERTIES.database, user=DB_PROPERTIES.user, password=DB_PROPERTIES.password,
            host=DB_PROPERTIES.host, min_size=1, max_size=10, max_inactive_connection_lifetime=30
        )
    return PG_ASYNC_POOL


pool = ThreadedConnectionPool(
    user=DB_PROPERTIES.user,
    password=DB_PROPERTIES.password,
    host=DB_PROPERTIES.host,
    port=DB_PROPERTIES.port,
    database=DB_PROPERTIES.database,
    maxconn=DB_PROPERTIES.connections,
    minconn=1
)

connections_used = 0


def with_postgres_cursor(f):
    def wrapper(*args, **kwargs):
        global connections_used
        connection = pool.getconn()
        connections_used += 1
        log(f"PostgreSQL connection is taken from the pool! connections_used: {connections_used}")

        cursor = None
        try:
            cursor = connection.cursor()
            f.connection = connection
            f.cursor = cursor
            return f(cursor, *args, **kwargs)
        except (Exception, psycopg2.Error) as error:
            stack_trace = traceback.format_exc()
            log("Error while connecting to PostgreSQL " + str(error) + "\n" + str(stack_trace))
        finally:
            connections_used -= 1
            try:
                cursor.close()
                connection.commit()

            except Exception as closeE:
                log("Cannot close cursor or commit connection: " + str(closeE))
            pool.putconn(connection)
            log(f"PostgreSQL connection is returned to the pool! connections_used: {connections_used}")

    return wrapper


@with_postgres_cursor
def retrieve_all_channels(cursor):
    while True:
        try:
            cursor.execute("SELECT * from ono_anchors;")
            result = list(cursor.fetchall())
            random.shuffle(result)
            return result
        except Exception as exp:
            log_exception(
                source=Source.TLG, channel_name="OneMedia:TLG:ALL_CHANNELS", event_name=EventName.DB_EXCEPTION,
                msg="retrieve_all_channels exception", exp=exp
            )
        time.sleep(3)


async def async_retrieve_all_channels(pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    connection: asyncpg.connection
    async with pool.acquire() as connection:
        found = await connection.fetch("SELECT * from ono_anchors;", )
    return found


async def async_retrieve_all_messages_with_channel(pool: asyncpg.pool.Pool):
    connection: asyncpg.connection
    async with pool.acquire() as connection:
        found = await connection.fetch(
            "SELECT content, channel_name, message_id from message where publish_date > now() - interval '1 month';",
        )
    return found


async def async_retrieve_all_channels_for_user(user_id, pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    connection: asyncpg.connection
    async with pool.acquire() as connection:
        found = await connection.fetch(
            "SELECT channel_id FROM user_channel WHERE user_id = $1;", user_id
        )
    return found


async def async_retrieve_all_users_notifies(pool: asyncpg.pool.Pool):
    connection: asyncpg.connection
    async with pool.acquire() as connection:
        found = await connection.fetch(
            "SELECT USER_ID, GLOBALLY, QUERY_TEXT FROM USER_NOTIFY;",
        )
    return found


@with_postgres_cursor
def initialise_anchor(cursor, channel_id, message, anchor):
    channel_name = message.chat.username
    channel_title = message.chat.title
    channel_type = message.chat.__class__.__name__
    cursor.execute("UPDATE ono_anchors SET chanel_name = %s,"
                   " channel_display_name = %s,"
                   " channel_type = %s,"
                   " last_message_id = %s"
                   " WHERE channel_id = %s;", (channel_name, channel_title, channel_type, anchor, channel_id))


@with_postgres_cursor
def initialise_anchor_by_channel_name(cursor, channel_name, message, anchor):
    channel_id = message.chat.id
    channel_title = message.chat.title
    channel_type = message.chat.__class__.__name__
    cursor.execute("UPDATE ono_anchors SET channel_id = %s,"
                   " channel_display_name = %s,"
                   " channel_type = %s,"
                   " last_message_id = %s"
                   " WHERE chanel_name = %s;", (channel_id, channel_title, channel_type, anchor, channel_name))
    return str(channel_id)


@with_postgres_cursor
def update_anchor_attributes(cursor, channel_id, channel_name, channel_title, channel_type):
    try:
        cursor.execute(
            "UPDATE ono_anchors SET chanel_name = %s,"
            " channel_display_name = %s,"
            " channel_type = %s "
            " WHERE channel_id = %s;",
            (channel_name, channel_title, channel_type, channel_id))
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log_exception(
            source=Source.TLG, channel_name=f"OneMedia:TLG:{channel_name}", event_name=EventName.DB_EXCEPTION,
            msg=f"Msg : update_anchor_attributes method exception {exp} {tb}", exp=exp
        )
        return False
    return True


@with_postgres_cursor
def update_anchor_attributes_subscribers(cursor, channel_id, channel_name, subscribers, system_mark="INIT"):
    try:
        cursor.execute(
            "UPDATE ono_anchors SET SUBSCRIBERS = %s, SUBSCRIBERS_UPDATE_TIME = NOW(), SYSTEM_MARK = %s"
            " WHERE channel_id = %s;",
            (subscribers, system_mark, channel_id))
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log_exception(
            source=Source.TLG, channel_name=f"OneMedia:TLG:{channel_name}", event_name=EventName.DB_EXCEPTION,
            msg=f"Msg : update_anchor_attributes method exception {exp} {tb}", exp=exp
        )
        return False
    return True


@with_postgres_cursor
def add_anchor(cursor, channel_name, channel_id, channel_title, channel_type):
    cursor.execute("INSERT INTO ono_anchors(CHANEL_NAME, CHANNEL_ID, CHANNEL_DISPLAY_NAME, CHANNEL_TYPE) "
                   "VALUES (%s, %s, %s, %s);"
                   , (channel_name, channel_id, channel_title, channel_type))


@with_postgres_cursor
def add_anchor_empty(cursor, channel_name):
    cursor.execute("INSERT INTO ono_anchors(CHANEL_NAME) VALUES (%s);", (channel_name,))


@with_postgres_cursor
def add_anchor_forwarded(cursor, channel_id, channel_name, channel_display_name, anchor):
    try:
        if (channel_name is None or len(channel_name) == 0) or (channel_id is None):
            log(f"Bad Channel for forward : {channel_name} {channel_id}")
            return False

        cursor.execute(
            "INSERT INTO ono_anchors(CHANEL_NAME, CHANNEL_ID, LAST_MESSAGE_ID, CHANNEL_DISPLAY_NAME, CHANNEL_TYPE, SYSTEM_MARK) "
            "VALUES (%s, %s, %s, %s, %s, %s);"
            , (channel_name, channel_id, max(1, anchor - 20), channel_display_name, "Channel", "FORWARDED"))
    except Exception as exp:
        exp_string = str(exp).lower()
        if "duplicate key value violates unique constraint" in exp_string or "already exists" in exp_string:
            log(f"Duplicate channel forwarded : {channel_name}")
            return True, "DUPLICATED"
        log(f"Error in channel : {channel_name} , {exp_string}")
        return False, "ERROR"
    return True, "OK"


async def async_add_user_channel_row(channel_id, user_id, pool: asyncpg.pool.Pool = None):
    if not pool:
        pool = await setup_pg_connection_pool()
    connection: asyncpg.connection
    try:
        result = []
        connection: asyncpg.connection
        async with pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM user_channel WHERE CHANNEL_ID = $1 AND USER_ID = $2;", channel_id, user_id
            )

        if len(result) == 0:
            async with pool.acquire() as connection:
                await connection.execute(
                    "INSERT INTO user_channel(CHANNEL_ID, USER_ID) VALUES ($1, $2);", channel_id, user_id
                )
        else:
            log(f"CHANNEL: {channel_id}, USER_ID: {channel_id} already existed! (SKIPPED)")
    except Exception as exp:
        tb = "".join(traceback.TracebackException.from_exception(exp).format())
        log_exception(
            source=Source.TLG, channel_name="OneMedia:TLG:ALL", event_name=EventName.DB_EXCEPTION,
            msg=f"Msg : async_add_user_channel_row() method exception {exp} {tb}", exp=exp
        )


@with_postgres_cursor
def delete_user_channel_row(cursor, channel, user_id):
    cursor.execute("delete from user_channel where chanel_name = '{}' and user_id = '{}';".format(channel, user_id))


def insert_message_tg_without_transaction_tg(channel_name, channel_id, channel_display_text, messages, anchor):
    saved = 0
    attempts_count = 3

    # insert messages
    for message in messages:
        used_attempts = 0
        for attempt in range(attempts_count):
            result, message = insert_single_message_tg(channel_name, channel_id, channel_display_text, message)
            if result:
                break
            used_attempts += 1
            time.sleep(1)
        # return as there is a gap
        if used_attempts == attempts_count:
            return False
        saved += 1
    # move anchor
    if update_anchor_tg(channel_id, channel_name, anchor):
        stat(source=Source.TLG, channel_name=channel_name, event_name=EventName.SAVE_NEWS, count=saved)
        return True
    return False


@with_postgres_cursor
def update_anchor_tg(cursor, channel_id, channel_name, anchor):
    try:
        cursor.execute(
            "UPDATE ono_anchors SET last_message_id = %s, system_mark = '' WHERE channel_id = %s;", (anchor, channel_id)
        )
    except Exception as e:
        log_exception(
            source=Source.TLG, channel_name=channel_name, event_name=EventName.DB_EXCEPTION,
            msg="UPDATE OF ANCHOR HAS FALLEN!", exp=e
        )
        return False
    return True


@with_postgres_cursor
def insert_single_message_tg(cursor, channel_name, channel_id, channel_display_text, message):
    log(f">>> Chat {channel_name}, text: {'<line>'.join(message.text.splitlines()) if message.text else str(message.text)}")
    if not message.text or message.text.isspace():
        log(f">>> EMPTY TEXT channel_name: {channel_name}, channel_id: {channel_id}, message_id: {message.id}<<<")
        return True, "OK"
    try:
        forward_channel_id = ""
        forward_message_id = ""
        if message.forward is not None:
            forward_message_id = message.forward.channel_post
            forward_channel_id = clean_chat_id(message.forward.chat_id)
        cursor.execute(
            """
                INSERT INTO MESSAGE(
                    MESSAGE_ID, CHANNEL_ID, CHANNEL_NAME,
                    CHANNEL_TITLE, SENDER_USERNAME, SENDER_ID,
                    PUBLISH_DATE, CONTENT, SOURCE_ID, FORWARD_CHANNEL_ID, FORWARD_MESSAGE_ID
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (message.id, channel_id, channel_name,
             channel_display_text, message.sender.username,
             message.sender.id,
             message.date, message.text, "TG", forward_channel_id, forward_message_id)
        )
    except Exception as exp:
        exp_string = str(exp).lower()
        if "duplicate key value violates unique constraint" in exp_string or "already exists" in exp_string:
            success = True
            log_exception(
                source=Source.TLG, channel_name=channel_name, event_name=EventName.DB_EXCEPTION,
                msg="tlg extractor message already existed (SKIPPED)", exp=exp
            )
            return True, "DUPLICATED"
        log_exception(
            source=Source.TLG, channel_name=channel_name, event_name=EventName.DB_EXCEPTION,
            msg="UNKNOWN_ERROR", exp=exp
        )
        return False, "UNKNOWN_ERROR"
    return True, "OK"


@with_postgres_cursor
def retrieve_all_messages(cursor, channel_id):
    cursor.execute("SELECT * FROM MESSAGE WHERE CHANNEL_ID = %s", (channel_id,))
    return list(cursor.fetchall())


# it has -100<chat_id> format
def clean_chat_id(chat_id):
    chat_id = str(chat_id)
    if chat_id.startswith("-100"):
        return chat_id[4:]
    return chat_id
