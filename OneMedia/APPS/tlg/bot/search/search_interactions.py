from typing import List

from telethon import Button
from telethon import events

from APPS.tlg.bot.action_storage import ActionStorage, action_dispatcher
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.search.search import gsearch_all_of, gsearch_any_of, search_simple_query, search_by_query
from APPS.tlg.bot.search.search_elements import get_search_description, ACTION_SEARCH_BY_QUERIES, \
    ACTION_CHOOSE_QUERY_SEARCH
from APPS.tlg.bot.subscription.subscription_repo import UserQuery, get_queries_list
from APPS.tlg.emoji_bot import EMOJI


async def search_main_menu_press_button(event: events.NewMessage.Event):
    await BOT.send_message(
        event.chat_id,
        message=get_search_description(),
        buttons=[
            [
                Button.switch_inline("All", same_peer=True, query="/gsearch_all_of "),
                Button.switch_inline("Any", same_peer=True, query="/gsearch_any_of ")
            ],
            [Button.switch_inline("Simple", same_peer=True, query="/gsearch_simple_of ")],
            [Button.inline("Запрос", data=ActionStorage.put_data(ACTION_SEARCH_BY_QUERIES, "NO_DATA"))],
        ]
    )
    raise events.StopPropagation


@action_dispatcher(action_name=ACTION_CHOOSE_QUERY_SEARCH)
async def choose_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    await search_by_query(event, user_query)
    raise events.StopPropagation


def get_query_list_button(query: UserQuery):
    return Button.inline(
        text=f"{query.name} (query uid: {query.uid})",
        data=ActionStorage.put_data(ACTION_CHOOSE_QUERY_SEARCH, query)
    )


@action_dispatcher(action_name=ACTION_SEARCH_BY_QUERIES)
async def show_all_queries(event: events.CallbackQuery.Event, _):
    queries: List[UserQuery] = await get_queries_list(event.chat_id)
    await BOT.send_message(
        event.chat_id, message=f"{EMOJI.POINT_DOWN} Выберите запрос {EMOJI.POINT_DOWN}",
        buttons=[[get_query_list_button(query)] for query in queries]
    )
    raise events.StopPropagation


@BOT.on(events.NewMessage(pattern=r'^(#|/)gsearch_(any|all|simple)_of\s(\w|\W)+'))
async def global_search_of(event):
    search_type = event.pattern_match.group(2)
    if search_type == 'all':
        await gsearch_all_of(event)
    elif search_type == 'any':
        await gsearch_any_of(event)
    else:
        await search_simple_query(event)
    raise events.StopPropagation


# @BOT.on(events.InlineQuery(pattern=r'^(#|/)gsearch_(any|all)_of\s\[((\w|\W)+)\]'))
@BOT.on(events.NewMessage(pattern=r'^@\w+\s(#|/)gsearch_(any|all|simple)_of\s((\w|\W)+)'))
async def inline_queries(event: events.InlineQuery.Event):
    search_type = event.pattern_match.group(2)
    terms = event.pattern_match.group(3).split(",")
    if search_type == 'all':
        await gsearch_all_of(event)
    elif search_type == 'any':
        await gsearch_any_of(event)
    else:
        await search_simple_query(event)
    raise events.StopPropagation
