from telethon import Button
from telethon import events

from APPS.tlg.bot.about.about_elements import get_about_description, BUTTON_SUPPORT, get_support_accepted_description
from APPS.tlg.bot.action_storage import ActionStorage, last_message_dispatcher
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.bot_elements import get_main_menu_buttons
from APPS.tlg.bot.support.support_repo import SupportRequest, SupportQuery, SupportType


@BOT.on(events.NewMessage(pattern='(#|/)(about)'))
async def about_main_menu_press_button(event: events.NewMessage.Event):
    await BOT.send_message(
        event.chat_id,
        message=get_about_description(),
        buttons=[
            [Button.url(text="Наш сайт", url="http://onemedia.dh-center.ru/")],
            [Button.inline(text=BUTTON_SUPPORT)],
        ],
        link_preview=True
    )
    raise events.StopPropagation


@BOT.on(events.CallbackQuery(pattern=f'^{BUTTON_SUPPORT}'))
async def ask_support_press_button(event: events.CallbackQuery.Event):
    user_id = event.chat_id
    ActionStorage.put_data_for_user(action_name=BUTTON_SUPPORT, user_id=user_id, data="no data")
    await BOT.send_message(
        user_id,
        message=f"Напишите ваш запрос в наш Support.",
        buttons=Button.force_reply()
    )
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_SUPPORT)
async def ask_support(event: events.NewMessage.Event, data: str):
    support_request = SupportRequest(
        event.chat_id,
        support_query=SupportQuery(
            support_type=SupportType.SUPPORT,
            data={
                "msg": event.message.raw_text
            }
        )
    )
    await support_request.save()
    await event.reply(
        message=get_support_accepted_description(support_request.uid),
        buttons=get_main_menu_buttons()  # to restore main menu
    )
    raise events.StopPropagation
