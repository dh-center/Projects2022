import inspect

from APPS.tlg.emoji_bot import EMOJI

BUTTON_ADD_CHANNEL_TLG = "Добавить канал TLG"
BUTTON_ADD_CHANNEL_VK = "Добавить группу, юзера VK"
BUTTON_ADD_CHANNEL_WEB = "Добавить сайт WEB"

ACTION_BUTTON_ADD_CHANNEL_TLG = "ACTION_ADD_CHANNEL_TLG"
ACTION_BUTTON_ADD_CHANNEL_VK = "ACTION_ADD_CHANNEL_VK"
ACTION_BUTTON_ADD_CHANNEL_WEB = "ACTION_ADD_CHANNEL_WEB"
ACTION_BUTTON_ADD_CHANNEL = "ACTION_ADD_CHANNEL"


async def get_channels_description(overall_channels: int) -> str:
    intro = ""
    if overall_channels:
        intro = f"На данный момент мы наблюдаем за {overall_channels} источниками.\n"
    res = intro + f"""
Если вам необходимо добавить источник которого нету в нашем списке, то вы можете создать заявку на его добавление.

Заметьте что источники из **Telegram** и **VK** будут добавлены достаточно быстро, **WEB** источник будет добавлен спустя какое-то время.

{EMOJI.POINT_DOWN} Добавить источник {EMOJI.POINT_DOWN}"""

    return inspect.cleandoc(res)
