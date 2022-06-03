import os

from telethon import TelegramClient

from APPS.logger import LOGGER


class PROPERTIES:
    api_id = int(os.getenv('api_id', 123))
    api_hash = os.getenv('api_hash', "api_hash")
    client_notifier = TelegramClient('client_notifier_bot', api_id, api_hash, base_logger=LOGGER)
    sleep_time_approaches = 15 * 60


class BOT_PROPERTIES:
    token = os.getenv('bot_token', 'token')
