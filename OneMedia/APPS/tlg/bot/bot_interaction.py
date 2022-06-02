from typing import Dict, Callable, Coroutine

from telethon import events

from APPS.tlg.bot.about.about_interactions import about_main_menu_press_button
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.bot_elements import *
from APPS.tlg.bot.channels.channels_interactions import channels_main_menu_press_button
from APPS.tlg.bot.profile.profile_interactions import profile_main_menu_press_button
from APPS.tlg.bot.queries.queries_interactions import queries_main_menu_press_button
from APPS.tlg.bot.reports.reports_interactions import reports_main_menu_press_button
from APPS.tlg.bot.search.search_interactions import search_main_menu_press_button
from APPS.tlg.bot.subscription.subscription_interactions import subscription_main_menu_press_button

MAIN_MENU_HANDLERS: Dict[str, Callable[[events.NewMessage.Event], Coroutine]] = {
    BUTTON_SEARCH: search_main_menu_press_button,
    BUTTON_ABOUT: about_main_menu_press_button,
    BUTTON_USER_PROFILE: profile_main_menu_press_button,
    BUTTON_MANAGE_SUBSCRIPTIONS: subscription_main_menu_press_button,
    BUTTON_REPORT: reports_main_menu_press_button,
    BUTTON_MANAGE_CHANNELS: channels_main_menu_press_button,
    BUTTON_MANAGE_QUERIES: queries_main_menu_press_button,
}


async def default_main_menu_handler(event: events.NewMessage.Event):
    button_name = event.message.raw_text
    await BOT.send_message(
        event.chat_id,
        message=f"Вы нажали кнопку : {button_name} (она ещё не реализована)"
    )


def get_main_menu_handler(button_name: str) -> Callable[[events.NewMessage.Event], Coroutine]:
    return MAIN_MENU_HANDLERS.get(button_name, default_main_menu_handler)
