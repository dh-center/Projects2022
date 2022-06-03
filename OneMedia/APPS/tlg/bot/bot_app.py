import asyncio

from telethon import events

from APPS.logger import log
from APPS.tlg.bot.action_log import UserAction
from APPS.tlg.bot.action_storage import ActionStorage
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.bot_elements import *
from APPS.tlg.bot.bot_interaction import get_main_menu_handler
from APPS.tlg.bot.notyfier.notyfier import keep_notify_alive
from APPS.tlg.bot.profile.profile_repo import get_user_info_by_user_id
from APPS.tlg.bot.profile.profile_utils import construct_user_info_from_event


@BOT.on(events.NewMessage(pattern='(#|/)(start|help)'))
async def send_welcome(event: events.NewMessage.Event):
    user_info = await get_user_info_by_user_id(event.chat_id)
    if not user_info:
        user_info = construct_user_info_from_event(event)
        await user_info.save()
    await event.reply(
        message=get_start_description(),
        buttons=get_main_menu_buttons(),
    )
    raise events.StopPropagation


@BOT.on(events.NewMessage(pattern=MENU_BUTTONS_REGEXP))
async def main_menu_button_event(event: events.NewMessage.Event):
    button_name = event.message.raw_text
    handler = get_main_menu_handler(button_name)

    await UserAction(
        user_id=event.chat_id, name="main_menu_button_pressed",
        data={"button_name": button_name}
    ).log()
    await handler(event)
    raise events.StopPropagation


@BOT.on(events.CallbackQuery())
async def buttons_callbacks(event):
    res = await ActionStorage.dispatch_handler(event)
    if not res: await event.reply("Готов к работе! (Попробуйте заново, вероятнее всего событие устарело)")


@BOT.on(events.NewMessage)
async def any_message(event: events.NewMessage.Event):
    contact = event.message.contact
    if contact is not None and event.chat_id == contact.user_id:
        await event.reply(
            message=f"Верификация завершена!",
            buttons=get_main_menu_buttons()
        )
        raise events.StopPropagation

    # last_message_tracker
    # try to find user action for last_message_dispatcher
    await ActionStorage.dispatch_handler_for_user(event)

    await event.reply(
        message=f"Got unexpected message : {event.message.text}"
    )


async def main():
    await asyncio.gather(
        keep_bot_alive(),
        keep_notify_alive()
    )


async def keep_bot_alive():
    log("Bot started.")
    # Now you can use all client methods listed below, like for example...
    # await monitoring_bot.send_message('me', 'Hello to myself!')
    while BOT.is_connected():
        await asyncio.sleep(5)


if __name__ == '__main__':
    BOT.loop.run_until_complete(main())
