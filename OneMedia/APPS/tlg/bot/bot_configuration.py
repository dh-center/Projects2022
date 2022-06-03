import telethon

from PROPERTIES.TLG_BOT_PROPERTIES import BOT_PROPERTIES, PROPERTIES

BOT: telethon.client.telegramclient.TelegramClient = \
    PROPERTIES.client_bot.start(bot_token=BOT_PROPERTIES.token)
