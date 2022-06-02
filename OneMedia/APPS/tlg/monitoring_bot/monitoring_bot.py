import asyncio
import inspect
import io
import os
import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Union

import psutil
from telethon import events

from APPS.logger import log
from APPS.search_utils import get_search_alive_status
from APPS.stat_monitoring import async_get_hour_stat, EventName, Source, log_exception_without_stat, async_get_day_stat, \
    async_get_month_stat, async_get_overall_stat_tlg, async_get_overall_stat_web, async_get_alive_stat, AppName, \
    async_get_ten_minutes_stat, async_get_overall_stat_vk, async_get_db_file_size_info, async_get_db_connections_count
from APPS.tlg.emoji_bot import EMOJI
from PROPERTIES.TLG_MONITORING_BOT_PROPERTIES import PROPERTIES, MONITORING_BOT_PROPERTIES

loop = asyncio.get_event_loop()
monitoring_bot = PROPERTIES.client_bot.start(bot_token=MONITORING_BOT_PROPERTIES.token)

IS_FIRST_START: bool = True

BYTES_IN_GB: int = 2 ** 30


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(start|help)'))
async def send_welcome(event):
    global IS_FIRST_START
    flag: bool = False
    if IS_FIRST_START:
        IS_FIRST_START = False
        log(f"First start")
        flag = True
    await event.reply(inspect.cleandoc(
        ("3 * Hours (Daily stats) updates to chat initialized.\n" if flag else "") +
        """
            /10minutes - получить 10 minutes status
            /hourly - получить hour status
            /daily - получить daily status
            /monthly - получить month status
            /overall - получить полный статус
            /alive_status - получить статус по сервисам
            /index_alive_status - получить статус по индексу
        """
    ))
    if flag:
        await send_stat_for_3_hours()


@dataclass
class StatRecord:
    source: str
    channel_name: str
    event_name: str
    sum: int


def get_stats_from_db_records(records):
    return [StatRecord(
        source=record['source'],
        channel_name=record['channel_name'],
        event_name=record['event_name'],
        sum=record['sum']
    ) for record in records]


EXCEPTION_EVENTS: List[str] = [
    EventName.PARSING_EXCEPTION.name, EventName.CONNECTION_EXCEPTION.name, EventName.DB_EXCEPTION.name,
    EventName.EXCEPTION.name
]


def split_by_event_name(stats: List[StatRecord]) -> Dict[str, List[StatRecord]]:
    stats_save_events = [stat for stat in stats if stat.event_name == EventName.SAVE_NEWS.name]
    stats_db_exceptions = [stat for stat in stats if stat.event_name == EventName.DB_EXCEPTION.name]
    stats_connection_exceptions = [stat for stat in stats if stat.event_name == EventName.CONNECTION_EXCEPTION.name]
    stats_parsing_exceptions = [stat for stat in stats if stat.event_name == EventName.PARSING_EXCEPTION.name]
    stats_exceptions = [stat for stat in stats if stat.event_name == EventName.EXCEPTION.name]

    stats_save_events.sort(key=lambda s: -s.sum)
    stats_db_exceptions.sort(key=lambda s: -s.sum)
    stats_connection_exceptions.sort(key=lambda s: -s.sum)
    stats_parsing_exceptions.sort(key=lambda s: -s.sum)
    stats_exceptions.sort(key=lambda s: -s.sum)

    return {
        EventName.SAVE_NEWS.name: stats_save_events,
        EventName.DB_EXCEPTION.name: stats_db_exceptions,
        EventName.CONNECTION_EXCEPTION.name: stats_connection_exceptions,
        EventName.PARSING_EXCEPTION.name: stats_parsing_exceptions,
        EventName.EXCEPTION.name: stats_exceptions,
    }


def get_emoji_per_source(source: str):
    return {
        Source.WEB.name: EMOJI.EARTH,
        Source.TLG.name: EMOJI.EMAIL,
        Source.VK.name: EMOJI.WEB,
    }[source]


def get_stat_reply(stats) -> str:
    stats = get_stats_from_db_records(stats)
    reply = ""

    saved_news_show_count = 20
    for source in [Source.WEB.name, Source.TLG.name, Source.VK.name]:
        current_stats = [stat for stat in stats if stat.source == source]
        current_stats_splitted = split_by_event_name(current_stats)
        reply += f"\n\n**----- {get_emoji_per_source(source)} {source}: -----**\n"
        # SAVE NEWS
        saved_news = current_stats_splitted[EventName.SAVE_NEWS.name]
        saved_total = sum(stat.sum for stat in saved_news)
        reply += f"**{EMOJI.NEWS_PAPER} SAVED NEWS :** {saved_total}"
        if saved_total:
            reply += '\n' + "\n".join([
                f"{ind}. {stat.channel_name} : {stat.sum}" for ind, stat in
                enumerate(saved_news[:saved_news_show_count], start=1)
            ])
        if len(saved_news) > saved_news_show_count:
            reply += f"\n and {len(saved_news) - saved_news_show_count} channels with {sum(stat.sum for stat in saved_news[saved_news_show_count:])} messages\n"

        # EXCEPTIONS
        exceptions_total = sum(
            sum(stat.sum for stat in current_stats_splitted[exp_type]) for exp_type in EXCEPTION_EVENTS)
        reply += f"\n\n**{EMOJI.EXCLAMATIONS} EXCEPTIONS :** {exceptions_total}"

        exceptions_show_count = 15
        for exceptions_type in EXCEPTION_EVENTS:
            cur_exceptions = current_stats_splitted[exceptions_type]
            exception_total = sum(stat.sum for stat in cur_exceptions)
            if exception_total:
                reply += f"\n{EMOJI.BANG} **{exceptions_type.upper()} :** {exception_total}"
                reply += '\n' + "\n".join([
                    f"{ind}. {stat.channel_name} : {stat.sum}" for ind, stat in
                    enumerate(cur_exceptions[:exceptions_show_count], start=1)
                ])
                if len(cur_exceptions) > exceptions_show_count:
                    reply += f"\n and {len(cur_exceptions) - exceptions_show_count} channels with " \
                             f"{sum(stat.sum for stat in cur_exceptions[exceptions_show_count:])} exceptions\n"

    return reply


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(hourly)'))
async def hourly(event):
    try:
        reply = f"{EMOJI.POINT_RIGHT} **HOURLY STAT :**"
        hour_stats = await async_get_hour_stat()
        reply += get_stat_reply(hour_stats)

        await event.reply(inspect.cleandoc(reply))
    except Exception as exp:
        log_exception_without_stat(f"hourly exp", exp)


@dataclass
class AliveRecord:
    app_name: str
    update_time: datetime
    msg: str


def get_alive_stats_from_db_records(records) -> List[AliveRecord]:
    return [AliveRecord(
        app_name=record['app_name'],
        update_time=record['update_time'],
        msg=record['msg'],
    ) for record in records]


def get_alive_stat_reply(alive_stat, db_file_stat, db_connections_stat) -> str:
    reply = ""
    reply += f"\n**CPU Usage :** {psutil.cpu_percent()} %"

    virtual_memory = psutil.virtual_memory()
    ram_usage_percent = virtual_memory.percent
    total_ram_in_gb = virtual_memory.total / (1024 * 1024 * 1024)
    reply += f"\n**RAM Usage : ** {total_ram_in_gb * (ram_usage_percent / 100):.2f} GB ({ram_usage_percent} % of total {total_ram_in_gb :.2f} GB)"

    overall_connections, set_app_name_connections = db_connections_stat
    reply += f"\n\n**DB File size : ** {db_file_stat['db_size']}"
    reply += f"\n**DB Backup : ** {DB_BACKUP_CHECK}"
    reply += f"\n**DB Overall Connections : ** {overall_connections}"
    reply += f"\n**DB 'set application_name' Connections : ** {set_app_name_connections}"

    hdd = psutil.disk_usage('/')
    reply += f"\n\n**Disk Total : ** {(hdd.total / BYTES_IN_GB):.2f} GB"
    reply += f"\n**Disk Free : ** {(hdd.free / BYTES_IN_GB):.2f} GB ({(100.0 - hdd.percent):.2f} %)"
    reply += f"\n**Disk Used : ** {(hdd.used / BYTES_IN_GB):.2f} GB ({hdd.percent:.2f} %)\n"

    alive_stat: List[AliveRecord] = get_alive_stats_from_db_records(alive_stat)
    alive_stat: Dict[str, AliveRecord] = {stat.app_name: stat for stat in alive_stat}

    now = datetime.now()
    for ind, app_name in enumerate([AppName.WEB_CRAWLER.name, AppName.VK_EXTRACTOR.name, AppName.TLG_EXTRACTOR.name],
                                   start=1):
        stat: AliveRecord = alive_stat[app_name]
        was_alive_seconds_ago = (now - stat.update_time).total_seconds()
        was_alive_in_minutes = was_alive_seconds_ago / 60
        reply += f"\n{ind}. **{app_name}** : was alive {was_alive_in_minutes:.2f} minutes ago (seconds {int(was_alive_seconds_ago)})"
        status = f"{EMOJI.HEART} Alive"
        if was_alive_seconds_ago > 17 * 60:
            status = f"{EMOJI.SCULL} Dead"
        reply += f"\nStatus: {status}"
        reply += f"\nLeft message : {stat.msg}\n"
    return reply


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(10minutes)'))
async def ten_minutes(event):
    try:
        reply = f"{EMOJI.POINT_RIGHT} **10 MINUTES STAT:**"
        ten_minutes_stat = await async_get_ten_minutes_stat()
        reply += get_stat_reply(ten_minutes_stat)

        await event.reply(inspect.cleandoc(reply)[:4096])
    except Exception as exp:
        log_exception_without_stat(f"tem_minutes exp", exp)


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(daily)'))
async def daily(event):
    try:
        reply = f"{EMOJI.POINT_RIGHT} **DAILY STAT:**"
        day_stats = await async_get_day_stat()
        reply += get_stat_reply(day_stats)

        await event.reply(inspect.cleandoc(reply)[:4096])
    except Exception as exp:
        log_exception_without_stat(f"daily exp", exp)


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(monthly)'))
async def monthly(event):
    try:
        reply = f"{EMOJI.POINT_RIGHT} **MONTHLY STAT:**"
        month_stats = await async_get_month_stat()
        reply += get_stat_reply(month_stats)

        await event.reply(inspect.cleandoc(reply)[:4096])
    except Exception as exp:
        log_exception_without_stat(f"monthly exp", exp)


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(overall)'))
async def overall(event):
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

        file = io.BytesIO(inspect.cleandoc(reply).encode('utf-8'))
        file.name = f'overall_report_{datetime.now()}.md'
        await event.reply(
            message="Overall report",
            file=file
        )

        # await event.reply()
        # step = 4090
        # whole_messages = ceil(len(reply) / step)
        # whole_reply = inspect.cleandoc(reply)
        # for i in range(1, whole_messages + 1):
        #     await event.reply(whole_reply[step * (i - 1): step * i])
    except Exception as exp:
        log_exception_without_stat(f"monthly exp", exp)


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(alive_status)'))
async def alive_status(event):
    try:
        reply = f"{EMOJI.HEART} **ALIVE STATUS:**\n"
        alive_stat = await async_get_alive_stat()
        db_file_stat = await async_get_db_file_size_info()
        db_connections_stat = await async_get_db_connections_count()
        reply += get_alive_stat_reply(alive_stat, db_file_stat[0], db_connections_stat)
        reply += "\n"
        await event.reply(inspect.cleandoc(reply))
    except Exception as exp:
        log_exception_without_stat(f"monthly exp", exp)


def get_search_alive_status_reply(alive_status: Union[Dict[str, Any], None]) -> str:
    reply = f"{EMOJI.HEART} **INDEX ALIVE STATUS:**\n"

    if not alive_status:
        reply += f"\n{EMOJI.FIRE}{EMOJI.FIRE}{EMOJI.FIRE} **Can not get alive status!!!"
        return reply

    if 'msg' in alive_status:
        reply += f"\n{EMOJI.FIRE}{EMOJI.FIRE}{EMOJI.FIRE} **Msg : ** {alive_status['msg']}"
        return reply

    reply += f"\n**Documents indexed : ** {alive_status['overallNumberOfDocuments']}"
    reply += f"\n**TELEGRAM Last uid : ** {alive_status['lastUidTlg']}"
    reply += f"\n**WEB Last uid : ** {alive_status['lastUidWeb']}"
    reply += f"\n**VK Last uid : ** {alive_status['lastUidVk']}"
    index_size_in_bytes = alive_status['indexSizeInBytes']
    reply += f"\n**Index size on Disk : ** {(index_size_in_bytes / BYTES_IN_GB):.2f} GB"
    return reply


@monitoring_bot.on(events.NewMessage(pattern='(#|/)(index_alive_status)'))
async def index_alive_status(event):
    try:
        alive_status = await get_search_alive_status()
        reply = get_search_alive_status_reply(alive_status)
        await event.reply(inspect.cleandoc(reply))
    except Exception as exp:
        log_exception_without_stat(f"index_alive_status exp", exp)


async def send_stat_for_3_hours():
    alive_status_reply = f"{EMOJI.HEART} **ALIVE STATUS:**\n"
    alive_stat = await async_get_alive_stat()
    db_file_stat = await async_get_db_file_size_info()
    db_connections_stat = await async_get_db_connections_count()
    alive_status_reply += get_alive_stat_reply(alive_stat, db_file_stat[0], db_connections_stat)

    index_alive_status = await get_search_alive_status()
    index_status_reply = get_search_alive_status_reply(index_alive_status)

    daily_reply = f"{EMOJI.POINT_RIGHT} **DAILY STAT:**"
    day_stat = await async_get_day_stat()
    daily_reply += get_stat_reply(day_stat)

    await monitoring_bot.send_message(MONITORING_BOT_PROPERTIES.chat_id, alive_status_reply[:4096])
    await monitoring_bot.send_message(MONITORING_BOT_PROPERTIES.chat_id, index_status_reply[:4096])
    await monitoring_bot.send_message(MONITORING_BOT_PROPERTIES.chat_id, daily_reply[:4096])


async def check_cpu_and_ram():
    while True:
        try:
            cpu_usage_percent = psutil.cpu_percent()
            virtual_memory = psutil.virtual_memory()
            ram_usage_percent = virtual_memory.percent

            ram_threshold = MONITORING_BOT_PROPERTIES.ram_warning_threshold
            cpu_threshold = MONITORING_BOT_PROPERTIES.cpu_warning_threshold
            if cpu_usage_percent > cpu_threshold or ram_usage_percent > ram_threshold:
                await asyncio.sleep(10)
                if cpu_usage_percent > cpu_threshold or ram_usage_percent > ram_threshold:
                    reply = f"{EMOJI.FIRE}{EMOJI.FIRE}{EMOJI.FIRE} **WARNING : CONSISTENT High CPU or RAM Usage!!!**\n"
                    reply += f"\n**CPU Usage :** {cpu_usage_percent} %"
                    total_ram_in_gb = virtual_memory.total / (1024 * 1024 * 1024)
                    reply += f"\n**RAM Usage : ** {total_ram_in_gb * (ram_usage_percent / 100):.2f} GB ({ram_usage_percent} % of total {total_ram_in_gb :.2f} GB)\n"
                    reply += f"\n{EMOJI.FIRE}{EMOJI.FIRE}{EMOJI.FIRE} **Check task manager!!!**"
                    await monitoring_bot.send_message(MONITORING_BOT_PROPERTIES.chat_id, reply)
                await asyncio.sleep(10)
            await asyncio.sleep(5)
        except Exception as exp:
            log_exception_without_stat(
                msg=f"check_cpu_and_ram() exception",
                exp=exp
            )


DB_BACKUP_CHECK: str = "NOT YET CHECKED!!!"


async def check_db_backup():
    global DB_BACKUP_CHECK
    while True:
        try:
            backup_file_path = pathlib.Path(os.path.join('db_backup', 'postgres-backup.sql.gz'))
            if not backup_file_path.exists():
                DB_BACKUP_CHECK = f"backup file {backup_file_path} not found!!! {EMOJI.FIRE}"
                await asyncio.sleep(5)
                continue
            stat = backup_file_path.stat()
            backup_filesize_mb = stat.st_size / (2 ** 20)

            modified = datetime.fromtimestamp(stat.st_mtime)
            now = datetime.now()

            backup_age_in_seconds = (now - modified).total_seconds()

            health_message = ""
            if backup_age_in_seconds > 60 * 60 * 24:  # greater than 24 hours
                health_message = f"(Too old file {EMOJI.FIRE})"

            DB_BACKUP_CHECK = f"Found backup file {backup_file_path}, size : {backup_filesize_mb:.2f} MB, " \
                              f"modified : {(backup_age_in_seconds / 60):.2f} minutes ago {health_message}"

            await asyncio.sleep(10)
        except Exception as exp:
            log_exception_without_stat(
                msg=f"check_db_backup() exception",
                exp=exp
            )


async def main():
    asyncio.create_task(check_cpu_and_ram())
    asyncio.create_task(check_db_backup())
    while monitoring_bot.is_connected():
        await asyncio.sleep(MONITORING_BOT_PROPERTIES.daily_stat_period)
        await send_stat_for_3_hours()


if __name__ == "__main__":
    with monitoring_bot:
        monitoring_bot.loop.run_until_complete(main())
