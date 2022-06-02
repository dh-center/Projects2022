import os

from telethon import TelegramClient

from APPS.logger import LOGGER


class PROPERTIES:
    api_id = int(os.getenv('api_id', 123))
    api_hash = os.getenv('api_hash', "api_hash")
    client_bot = TelegramClient('bot_session_with_bot_as_user', api_id, api_hash, base_logger=LOGGER)


class MONITORING_BOT_PROPERTIES:
    token = os.getenv('monitoring_bot_token', 'token')
    daily_stat_period = 3 * 60 * 60  # 3 hours
    cpu_warning_threshold = 90
    ram_warning_threshold = 90
    chat_id = -1001279856546
