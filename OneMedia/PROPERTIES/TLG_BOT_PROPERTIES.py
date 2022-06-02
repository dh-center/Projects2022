import os

from telethon import TelegramClient

from APPS.logger import LOGGER


class PROPERTIES:
    api_id = int(os.getenv('api_id', 123))
    api_hash = os.getenv('api_hash', "api_hash")
    client_account_manager = TelegramClient('sessions/client_account_manager', api_id, api_hash, base_logger=LOGGER)
    client_bot = TelegramClient('sessions/bot_session_with_bot_as_user', api_id, api_hash, base_logger=LOGGER)
    phone = os.getenv('api_phone', None)
    sleep_time_approaches = 10 * 60


class BOT_PROPERTIES:
    token = os.getenv('bot_token', 'token')
