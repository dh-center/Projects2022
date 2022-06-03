import datetime
import traceback
from typing import List

import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from APPS.logger import log
from APPS.stat_monitoring import Source, EventName, log_exception
from PROPERTIES.DB_PROPERTY import DB_PROPERTIES

pool = ThreadedConnectionPool(
    user=DB_PROPERTIES.user,
    password=DB_PROPERTIES.password,
    host=DB_PROPERTIES.host,
    port=DB_PROPERTIES.port,
    database=DB_PROPERTIES.database,
    maxconn=DB_PROPERTIES.connections,
    minconn=1
)


def with_postgres_cursor(f):
    def wrapper(*args, **kwargs):
        connection = pool.getconn()
        cursor = None
        try:
            cursor = connection.cursor()
            f.connection = connection
            f.cursor = cursor
            return f(cursor, *args, **kwargs)
        except (Exception, psycopg2.Error) as error:
            stack_trace = traceback.format_exc()
            log("Error while connecting to PostgreSQL" + str(error) + "\nSTACK_TRACE:\n" + str(stack_trace))
        finally:
            if connection:
                cursor.close()
                connection.commit()
                pool.putconn(connection)
                log("PostgreSQL connection is returned to the pool!")

    return wrapper


@with_postgres_cursor
def get_all_anchors(cursor):
    try:
        cursor.execute(
            "SELECT channel_name, channel_id, screen_name, last_message_id, participants, last_time_updated_info, is_group"
            " from VK_MESSAGE_ANCHORS;"
        )
        return list(cursor.fetchall())
    except Exception as exp:
        log_exception(
            source=Source.VK, channel_name="OneMedia:VK:ALL", event_name=EventName.DB_EXCEPTION, exp=exp,
            msg="get_all_anchors() exception"
        )
        return False


@with_postgres_cursor
def get_message_by_ids(cursor, message_id, channel_id):
    cursor.execute("SELECT * from VK_MESSAGE WHERE MESSAGE_ID=%s AND OWNER_ID=%s;", (message_id, "-" + str(channel_id)))
    return list(cursor.fetchall())


@with_postgres_cursor
def insert_vk_message(
        cursor, message_id, owner_id, from_id, message_content, publish_date, photos: List[str], channel_name
) -> bool:
    try:
        cursor.execute(
            "INSERT INTO VK_MESSAGE(MESSAGE_ID, OWNER_ID, FROM_ID, MESSAGE_CONTENT, PUBLISH_DATE, meta_image) "
            "VALUES (%s,%s,%s,%s,%s, %s);",
            (message_id, owner_id, from_id, message_content, publish_date, ','.join(photos) if photos else None))
        return True
    except Exception as exp:
        log_exception(
            source=Source.VK, channel_name=channel_name, event_name=EventName.DB_EXCEPTION, exp=exp,
            msg="insert_vk_message() exception"
        )
        return False


@with_postgres_cursor
def insert_vk_message_anchor(cursor, channel_id, channel_name, screen_name, participants, is_group):
    cursor.execute(
        "INSERT INTO VK_MESSAGE_ANCHORS(CHANNEL_ID, CHANNEL_NAME, SCREEN_NAME, participants, last_time_updated_info, is_group) "
        "VALUES (%s,%s,%s,%s,%s,%s);",
        (channel_id, channel_name, screen_name, participants, datetime.datetime.now(), is_group)
    )


def insert_vk_message_anchor_group(channel_id, channel_name, screen_name, participants):
    insert_vk_message_anchor(channel_id, channel_name, screen_name, participants, True)


def insert_vk_message_anchor_user(channel_id, channel_name, screen_name, participants):
    insert_vk_message_anchor(channel_id, channel_name, screen_name, participants, False)


@with_postgres_cursor
def update_vk_message_anchor(cursor, channel_id, channel_name, screen_name, participants):
    cursor.execute(
        "UPDATE VK_MESSAGE_ANCHORS "
        "SET CHANNEL_NAME=%s, SCREEN_NAME=%s, participants=%s, last_time_updated_info=%s "
        "WHERE CHANNEL_ID=%s;",
        (channel_name, screen_name, participants, datetime.datetime.now(), channel_id)
    )


@with_postgres_cursor
def update_vk_anchor(cursor, message_id, channel_id, channel_name):
    try:
        cursor.execute(
            "UPDATE VK_MESSAGE_ANCHORS SET LAST_MESSAGE_ID = %s WHERE CHANNEL_ID = %s;",
            (message_id, channel_id)
        )
        return True
    except Exception as exp:
        log_exception(
            source=Source.VK, channel_name=channel_name, event_name=EventName.DB_EXCEPTION, exp=exp,
            msg="update_vk_anchor() exception"
        )
        return False
