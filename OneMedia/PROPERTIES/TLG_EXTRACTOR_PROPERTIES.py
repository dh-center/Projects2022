import os

from telethon import TelegramClient

from APPS.logger import LOGGER


class PROPERTIES:
    api_id = int(os.getenv('api_id', 123))
    api_hash = os.getenv('api_hash', "api_hash")
    client_extractor = TelegramClient('sessions/extractor_session', api_id, api_hash, base_logger=LOGGER)
    phone = os.getenv('api_phone', None)
    sleep_time_approaches = 5 * 60
    sleep_time_channel = 5
    wait_time_iter_messages = 3
