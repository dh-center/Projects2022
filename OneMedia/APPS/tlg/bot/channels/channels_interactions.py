import io
from datetime import datetime

from telethon import events, Button

from APPS.tlg.bot.action_storage import ActionStorage, last_message_dispatcher
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.bot_elements import get_main_menu_buttons
from APPS.tlg.bot.channels.channels_elements import get_channels_description, BUTTON_ADD_CHANNEL_TLG, \
    BUTTON_ADD_CHANNEL_VK, BUTTON_ADD_CHANNEL_WEB, ACTION_BUTTON_ADD_CHANNEL_TLG, ACTION_BUTTON_ADD_CHANNEL_WEB, \
    ACTION_BUTTON_ADD_CHANNEL_VK, ACTION_BUTTON_ADD_CHANNEL
from APPS.tlg.bot.channels.channels_repo import get_channels_stat
from APPS.tlg.bot.support.support_repo import SupportRequest, SupportQuery, SupportType
from APPS.tlg.emoji_bot import EMOJI


async def channels_main_menu_press_button(event: events.NewMessage.Event):
    overall_channels, reply = await get_channels_stat()
    file = None
    if not reply:
        await event.reply(message=f"{EMOJI.TIME} Идёт инициализация источников, в течение минуты они будут доступны.")
    else:
        file = io.BytesIO(reply.encode('utf-8'))
        file.name = f'channels_list_{datetime.now().strftime("%Y-%m-%d")}.md'
        await event.reply(message=f"{EMOJI.POINT_UP}**Доступные каналы**{EMOJI.POINT_UP}", file=file)

    await BOT.send_message(
        event.chat_id,
        message=await get_channels_description(overall_channels),
        buttons=[
            [Button.inline(text=BUTTON_ADD_CHANNEL_TLG, data=ACTION_BUTTON_ADD_CHANNEL_TLG)],
            [Button.inline(text=BUTTON_ADD_CHANNEL_VK, data=ACTION_BUTTON_ADD_CHANNEL_VK)],
            [Button.inline(text=BUTTON_ADD_CHANNEL_WEB, data=ACTION_BUTTON_ADD_CHANNEL_WEB)],
        ]
    )
    raise events.StopPropagation


@BOT.on(events.CallbackQuery(
    pattern=f'^{ACTION_BUTTON_ADD_CHANNEL_TLG}|{ACTION_BUTTON_ADD_CHANNEL_VK}|{ACTION_BUTTON_ADD_CHANNEL_WEB}'))
async def add_channel_init(event: events.CallbackQuery.Event):
    user_id = event.chat_id
    source = event.data.decode()

    message = await BOT.send_message(
        user_id, message=f"Напишите имя канала {EMOJI.SEARCH}",
        buttons=Button.force_reply()
    )
    ActionStorage.put_data_for_user(action_name=ACTION_BUTTON_ADD_CHANNEL, user_id=user_id, data=(message.id, source))
    raise events.StopPropagation


@last_message_dispatcher(action_name=ACTION_BUTTON_ADD_CHANNEL)
async def add_channel_finish(event: events.NewMessage.Event, data):
    main_message_id = data[0]
    real_source = get_real_source_from_action(data[1])
    data = event.message.raw_text

    await BOT.delete_messages(event.chat_id, [main_message_id, event.message.id])

    support_request = SupportRequest(
        event.chat_id,
        support_query=SupportQuery(
            support_type=SupportType.ADD_CHANNEL,
            data={"source": real_source, "channel_name": data}
        )
    )
    await support_request.save()

    await BOT.send_message(
        event.chat_id,
        message=f"Канал **{data}** добавлен в обработку на добавление "
                f"(**uid: {support_request.uid}**). {EMOJI.SUPPORTIVE_SMILE}",
        buttons=get_main_menu_buttons()  # necessary to restore main menu
    )
    raise events.StopPropagation


def get_real_source_from_action(action: str) -> str:
    if action == ACTION_BUTTON_ADD_CHANNEL_TLG:
        return "TLG"
    elif action == ACTION_BUTTON_ADD_CHANNEL_VK:
        return "VK"
    elif action == ACTION_BUTTON_ADD_CHANNEL_WEB:
        return "WEB"
    else:
        raise RuntimeError(f"Unexpected action {action}")
