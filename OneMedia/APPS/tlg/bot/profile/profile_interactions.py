from telethon import events

from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.profile.profile_elements import get_profile_description


async def profile_main_menu_press_button(event: events.NewMessage.Event):
    await BOT.send_message(
        event.chat_id,
        message=await get_profile_description(event),
        # buttons=[
        #     Button.request_phone(text="Подтвердить телефон", resize=True, single_use=True)
        # ]
    )
    raise events.StopPropagation
