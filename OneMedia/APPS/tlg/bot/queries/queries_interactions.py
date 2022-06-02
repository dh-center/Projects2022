import inspect
import json
from typing import List

from telethon import Button
from telethon import events

from APPS.tlg.bot.action_storage import last_message_dispatcher, ActionStorage, action_dispatcher
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.bot_elements import get_main_menu_buttons
from APPS.tlg.bot.profile.profile_repo import get_user_info_by_user_id, UserInfo
from APPS.tlg.bot.queries.queries_elements import BUTTON_ADD_QUERY, BUTTON_MY_QUERIES, get_query_created_description, \
    get_query_already_exist_description, BUTTON_REMOVE_QUERY, ACTION_REMOVE_QUERY, get_query_list_query_description, \
    ACTION_VIEW_EDIT_QUERY, \
    BUTTON_VIEW_EDIT_QUERY, get_query_vew_edit_description, BUTTON_CHANGE_QUERY_DISABLE_GLOBAL, \
    BUTTON_CHANGE_QUERY_ENABLE_GLOBAL, BUTTON_CHANGE_QUERY_NAME, BUTTON_CHANGE_QUERY_MUST_TERMS, \
    BUTTON_CHANGE_QUERY_SHOULD_TERMS, BUTTON_CHANGE_QUERY_EXCLUDED_TERMS, \
    BUTTON_CHANGE_QUERY_MUST_TERMS_ACTION, BUTTON_CHANGE_QUERY_SHOULD_TERMS_ACTION, \
    BUTTON_CHANGE_QUERY_EXCLUDED_TERMS_ACTION, BUTTON_CHANGE_QUERY_NAME_ACTION, HELP_TERMS_QUERY, \
    BUTTON_CHANGE_QUERY_CHANNELS_EXCLUDED, BUTTON_CHANGE_QUERY_CHANNELS_INCLUDED, BUTTON_CHANGE_QUERY_SOURCES_VK, \
    BUTTON_CHANGE_QUERY_SOURCES_WEB, BUTTON_CHANGE_QUERY_SOURCES_TLG, source_with_enabled_indicator
from APPS.tlg.bot.subscription.subscription_repo import get_number_of_queries_by_user, UserQuery, NewsQuery, \
    get_queries_list, delete_query
from APPS.tlg.emoji_bot import EMOJI


async def queries_main_menu_press_button(event: events.NewMessage.Event):
    user_info = await get_user_info_by_user_id(event.chat_id)
    await BOT.send_message(event.chat_id, **(await get_main_menu_elements(user_info)))
    raise events.StopPropagation


async def get_main_menu_elements(user_info: UserInfo):
    return {
        "message": await get_main_queries_description(user_info),
        "buttons": [
            [Button.inline(BUTTON_MY_QUERIES)],
            [Button.inline(BUTTON_ADD_QUERY)],
        ]
    }


async def get_main_queries_description(user_info: UserInfo) -> str:
    number_of_queries = await get_number_of_queries_by_user(user_info.user_id)

    res = f"""
    У вас {number_of_queries}{EMOJI.SEARCH} запросов.

    {EMOJI.POINT_DOWN} Управление запросами {EMOJI.POINT_DOWN}
    """
    return inspect.cleandoc(res)


@BOT.on(events.CallbackQuery(pattern=f'^{BUTTON_ADD_QUERY}'))
async def add_query(event: events.CallbackQuery.Event):
    user_id = event.chat_id
    message = await BOT.send_message(
        user_id, message=f"Напишите имя запроса {EMOJI.SEARCH}",
        buttons=Button.force_reply()
    )
    ActionStorage.put_data_for_user(action_name=BUTTON_ADD_QUERY, user_id=user_id, data=message.id)
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_ADD_QUERY)
async def add_query_finish(event: events.NewMessage.Event, bot_question_message_id: int):
    user_query = UserQuery(
        user_id=event.chat_id, name=event.message.raw_text, query=NewsQuery()
    )
    user_reply_message_id = event.message.id
    await BOT.delete_messages(event.chat_id, message_ids=[user_reply_message_id, bot_question_message_id])

    if await user_query.exist():
        await BOT.send_message(
            event.chat_id,
            message=get_query_already_exist_description(user_query.name)
        )
        await add_query(event)
        raise events.StopPropagation

    await user_query.save()
    await BOT.send_message(
        event.chat_id,
        message=get_query_created_description(user_query.uid),
        buttons=get_main_menu_buttons()  # necessary to restore main menu
    )
    await BOT.send_message(
        event.chat_id,
        **(await get_query_view_edit_elements(user_query))
    )
    raise events.StopPropagation


@BOT.on(events.CallbackQuery(pattern=f'^{BUTTON_MY_QUERIES}'))
async def get_queries_list_main_menu_interaction(event: events.CallbackQuery.Event):
    queries: List[UserQuery] = await get_queries_list(event.chat_id)
    await BOT.send_message(event.chat_id, message=f"{EMOJI.POINT_DOWN} Ваши запросы {EMOJI.POINT_DOWN}")
    for query in queries:
        await BOT.send_message(event.chat_id, **(get_query_list_elements(query)))
    raise events.StopPropagation


def get_query_list_elements(query: UserQuery):
    return {
        "message": get_query_list_query_description(query),
        "buttons": [
            [
                Button.inline(
                    BUTTON_VIEW_EDIT_QUERY,
                    data=ActionStorage.put_data(ACTION_VIEW_EDIT_QUERY, query)
                ),
                Button.inline(
                    BUTTON_REMOVE_QUERY,
                    data=ActionStorage.put_data(ACTION_REMOVE_QUERY, query)
                ),
            ]
        ]
    }


@action_dispatcher(action_name=ACTION_VIEW_EDIT_QUERY)
async def vied_edit_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    await BOT.send_message(
        event.chat_id, **(await get_query_view_edit_elements(user_query))
    )
    raise events.StopPropagation


async def get_query_view_edit_elements(user_query: UserQuery):
    buttons = [
        [Button.inline(BUTTON_CHANGE_QUERY_NAME, ActionStorage.put_data(BUTTON_CHANGE_QUERY_NAME, user_query))],
        [
            Button.inline(button_name, ActionStorage.put_data(button_name, user_query))
            for button_name in
            [BUTTON_CHANGE_QUERY_MUST_TERMS, BUTTON_CHANGE_QUERY_SHOULD_TERMS, BUTTON_CHANGE_QUERY_EXCLUDED_TERMS]
        ],
        [
            Button.inline(
                text=source_with_enabled_indicator(user_query, button_name),
                data=ActionStorage.put_data(button_name, (button_name, user_query))
            ) for button_name in
            [BUTTON_CHANGE_QUERY_SOURCES_TLG, BUTTON_CHANGE_QUERY_SOURCES_WEB, BUTTON_CHANGE_QUERY_SOURCES_VK]
        ],
        [
            Button.inline(button_name, ActionStorage.put_data(button_name, user_query))
            for button_name in
            [BUTTON_CHANGE_QUERY_CHANNELS_INCLUDED, BUTTON_CHANGE_QUERY_CHANNELS_EXCLUDED]
        ],
    ]

    return {
        "message": get_query_vew_edit_description(user_query),
        "buttons": buttons
    }


@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_SOURCES_TLG)
@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_SOURCES_WEB)
@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_SOURCES_VK)
async def toggle_source(event: events.CallbackQuery.Event, data):
    user_id = event.chat_id
    (source, user_query) = data

    news_query = user_query.query
    sources_set = news_query.get_sources_set()
    if source in news_query.get_sources_set():
        msg = f"Disabled {EMOJI.GRAY_CROSS}"
        news_query.sources = [*sorted(sources_set - {source})]
    else:
        msg = f"Enabled {EMOJI.LAMP}"
        news_query.sources = [*sorted(sources_set | {source})]

    await user_query.save()

    query_view = await get_query_view_edit_elements(user_query)
    await BOT.edit_message(
        event.chat, message=event.message_id,
        text=query_view["message"],
        buttons=query_view["buttons"]
    )
    await BOT.send_message(
        user_id, message=f"Source: {source} {msg}"
    )

    raise events.StopPropagation


# Must change
@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_MUST_TERMS)
async def edit_must_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    user_id = event.chat_id
    msg = f"""
    Напишите **MUST** термы:
    
    {HELP_TERMS_QUERY}
    """
    message = await BOT.send_message(
        user_id, message=inspect.cleandoc(msg),
        buttons=Button.force_reply()
    )
    ActionStorage.put_data_for_user(
        action_name=BUTTON_CHANGE_QUERY_MUST_TERMS_ACTION, user_id=user_id,
        data=(event.message_id, message.id, user_query)
    )
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_MUST_TERMS_ACTION)
async def must_query_finish(event: events.NewMessage.Event, data):
    main_message_id: int = data[0]
    bot_question_message_id: int = data[1]
    user_query: UserQuery = data[2]
    user_reply_message_id = event.message.id
    await BOT.delete_messages(event.chat_id, message_ids=[user_reply_message_id, bot_question_message_id])

    terms = []
    try:
        terms = json.loads(f'{{ "terms" : [{event.message.raw_text}]}}')["terms"]
    except Exception as e:
        await BOT.send_message(
            event.chat_id,
            message=f"Can not parse terms try again! {EMOJI.PROBLEM_FACE}",
            buttons=get_main_menu_buttons()  # necessary to restore main menu
        )
        raise events.StopPropagation

    user_query.query.must_terms = [[term] if isinstance(term, str) else term for term in terms]
    await user_query.save()
    query_view = await get_query_view_edit_elements(user_query)
    await BOT.edit_message(
        event.chat, message=main_message_id,
        text=query_view["message"],
        buttons=query_view["buttons"]
    )
    await BOT.send_message(
        event.chat_id,
        message=f"Must terms changed {EMOJI.SUPPORTIVE_SMILE}",
        buttons=get_main_menu_buttons()  # necessary to restore main menu
    )
    raise events.StopPropagation


# Should change
@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_SHOULD_TERMS)
async def edit_should_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    user_id = event.chat_id
    msg = f"""
    Напишите **SHOULD** термы:
    
    {HELP_TERMS_QUERY}
    """
    message = await BOT.send_message(
        user_id, message=inspect.cleandoc(msg),
        buttons=Button.force_reply()
    )
    ActionStorage.put_data_for_user(
        action_name=BUTTON_CHANGE_QUERY_SHOULD_TERMS_ACTION, user_id=user_id,
        data=(event.message_id, message.id, user_query)
    )
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_SHOULD_TERMS_ACTION)
async def should_query_finish(event: events.NewMessage.Event, data):
    main_message_id: int = data[0]
    bot_question_message_id: int = data[1]
    user_query: UserQuery = data[2]
    user_reply_message_id = event.message.id
    await BOT.delete_messages(event.chat_id, message_ids=[user_reply_message_id, bot_question_message_id])

    terms = []
    try:
        terms = json.loads(f'{{ "terms" : [{event.message.raw_text}]}}')["terms"]
    except Exception as e:
        await BOT.send_message(
            event.chat_id,
            message=f"Can not parse terms try again! {EMOJI.PROBLEM_FACE}",
            buttons=get_main_menu_buttons()  # necessary to restore main menu
        )
        raise events.StopPropagation

    user_query.query.should_terms = [[term] if isinstance(term, str) else term for term in terms]
    await user_query.save()
    query_view = await get_query_view_edit_elements(user_query)
    await BOT.edit_message(
        event.chat, message=main_message_id,
        text=query_view["message"],
        buttons=query_view["buttons"]
    )
    await BOT.send_message(
        event.chat_id,
        message=f"Should terms changed {EMOJI.SUPPORTIVE_SMILE}",
        buttons=get_main_menu_buttons()  # necessary to restore main menu
    )
    raise events.StopPropagation


# Excluded change
@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_EXCLUDED_TERMS)
async def edit_excluded_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    user_id = event.chat_id
    msg = f"""
    Напишите **EXCLUDED** термы:
    
    {HELP_TERMS_QUERY}
    """
    message = await BOT.send_message(
        user_id, message=inspect.cleandoc(msg),
        buttons=Button.force_reply()
    )
    ActionStorage.put_data_for_user(
        action_name=BUTTON_CHANGE_QUERY_EXCLUDED_TERMS_ACTION, user_id=user_id,
        data=(event.message_id, message.id, user_query)
    )
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_EXCLUDED_TERMS_ACTION)
async def excluded_query_finish(event: events.NewMessage.Event, data):
    main_message_id: int = data[0]
    bot_question_message_id: int = data[1]
    user_query: UserQuery = data[2]
    user_reply_message_id = event.message.id
    await BOT.delete_messages(event.chat_id, message_ids=[user_reply_message_id, bot_question_message_id])

    terms = []
    try:
        terms = json.loads(f'{{ "terms" : [{event.message.raw_text}]}}')["terms"]
    except Exception as e:
        await BOT.send_message(
            event.chat_id,
            message=f"Can not parse terms try again! {EMOJI.PROBLEM_FACE}",
            buttons=get_main_menu_buttons()  # necessary to restore main menu
        )
        raise events.StopPropagation

    user_query.query.excluded_terms = [[term] if isinstance(term, str) else term for term in terms]
    await user_query.save()
    query_view = await get_query_view_edit_elements(user_query)
    await BOT.edit_message(
        event.chat, message=main_message_id,
        text=query_view["message"],
        buttons=query_view["buttons"]
    )
    await BOT.send_message(
        event.chat_id,
        message=f"Excluded terms changed {EMOJI.SUPPORTIVE_SMILE}",
        buttons=get_main_menu_buttons()  # necessary to restore main menu
    )
    raise events.StopPropagation


# Name change
@action_dispatcher(action_name=BUTTON_CHANGE_QUERY_NAME)
async def edit_name_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    user_id = event.chat_id
    msg = f"""
    Напишите новое имя:
    """
    message = await BOT.send_message(
        user_id, message=inspect.cleandoc(msg),
        buttons=Button.force_reply()
    )
    ActionStorage.put_data_for_user(
        action_name=BUTTON_CHANGE_QUERY_NAME_ACTION, user_id=user_id,
        data=(event.message_id, message.id, user_query)
    )
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_NAME_ACTION)
async def name_query_finish(event: events.NewMessage.Event, data):
    main_message_id: int = data[0]
    bot_question_message_id: int = data[1]
    user_query: UserQuery = data[2]
    user_reply_message_id = event.message.id
    await BOT.delete_messages(event.chat_id, message_ids=[user_reply_message_id, bot_question_message_id])

    # check name doesn't exist
    new_name = event.message.raw_text.strip()
    if await UserQuery(user_id=event.chat_id, name=new_name, query=NewsQuery()).exist():
        await BOT.send_message(
            event.chat_id,
            message=get_query_already_exist_description(new_name)
        )
        raise events.StopPropagation

    user_query.name = new_name
    await user_query.save()
    query_view = await get_query_view_edit_elements(user_query)
    await BOT.edit_message(
        event.chat, message=main_message_id,
        text=query_view["message"],
        buttons=query_view["buttons"]
    )
    await BOT.send_message(
        event.chat_id,
        message=f"Name changed {EMOJI.SUPPORTIVE_SMILE}",
        buttons=get_main_menu_buttons()  # necessary to restore main menu
    )
    raise events.StopPropagation


# Remove
@action_dispatcher(action_name=ACTION_REMOVE_QUERY)
async def remove_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    await delete_query(user_query.uid)
    await BOT.delete_messages(
        event.chat_id, event.message_id
    )
    raise events.StopPropagation


# Name change
@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_ENABLE_GLOBAL)
@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_DISABLE_GLOBAL)
async def edit_is_global_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    user_query.query.is_global = not user_query.query.is_global
    await user_query.save()
    query_view = await get_query_view_edit_elements(user_query)
    await BOT.edit_message(
        event.chat, message=event.message_id,
        text=query_view["message"],
        buttons=query_view["buttons"]
    )
    raise events.StopPropagation


@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_CHANNELS_EXCLUDED)
@last_message_dispatcher(action_name=BUTTON_CHANGE_QUERY_CHANNELS_INCLUDED)
async def change_query_channels_inlcluded(event: events.CallbackQuery.Event, user_query: UserQuery):
    await BOT.send_message(
        event.chat,
        message=f"Для удобства, каналы запросов можно менять только через UI."
                f"\n(По умолчанию если **Included channels** пустые, запрос будет "
                f"применяться ко всем существующим каналам)",
        buttons=Button.url("Поменять запрос на UI", "http://onemedia.dh-center.ru/static/site/work.html")
    )
    raise events.StopPropagation
