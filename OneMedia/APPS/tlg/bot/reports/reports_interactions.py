from datetime import datetime
from typing import List

from telethon import events

from APPS.tlg.bot.action_storage import action_dispatcher
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.reports.reports_elements import get_query_list_button, ACTION_CHOOSE_QUERY, get_report_time_variants, \
    ACTION_CHOOSE_1DAY, ACTION_CHOOSE_1WEEK, ACTION_CHOOSE_1MONTH, ACTION_CHOOSE_3MONTHS, get_from_time_from_action
from APPS.tlg.bot.reports.reports_generator import generate_report_from_time
from APPS.tlg.bot.subscription.subscription_repo import UserQuery, get_queries_list
from APPS.tlg.emoji_bot import EMOJI


async def reports_main_menu_press_button(event: events.NewMessage.Event):
    queries: List[UserQuery] = await get_queries_list(event.chat_id)
    buttons = [[get_query_list_button(query)] for query in queries]
    await BOT.send_message(
        event.chat_id,
        message=f"{EMOJI.POINT_DOWN} Выберите запрос для генерации отчёта {EMOJI.POINT_DOWN}",
        buttons=buttons
    )
    raise events.StopPropagation


@action_dispatcher(action_name=ACTION_CHOOSE_QUERY)
async def choose_query(event: events.CallbackQuery.Event, user_query: UserQuery):
    await BOT.send_message(
        event.chat_id, **(get_report_time_variants(user_query))
    )
    raise events.StopPropagation


@action_dispatcher(action_name=ACTION_CHOOSE_1DAY)
@action_dispatcher(action_name=ACTION_CHOOSE_1WEEK)
@action_dispatcher(action_name=ACTION_CHOOSE_1MONTH)
@action_dispatcher(action_name=ACTION_CHOOSE_3MONTHS)
async def generate_report(event: events.CallbackQuery.Event, data):
    action = data[0]

    from_time = get_from_time_from_action(action)
    user_query: UserQuery = data[1]

    now = datetime.now()
    num_of_rows, report_file = await generate_report_from_time(
        name_prefix=f"{user_query.user_id}_{user_query.uid}_from_{from_time:%Y-%m-%d %H:%M}_to_{now :%Y-%m-%d %H:%M}",
        from_time=from_time, now=now, user_query=user_query
    )
    if report_file:
        await BOT.send_message(
            event.chat_id,
            message=f"Ваш отчёт с {from_time:%Y-%m-%d %H:%M} по {now :%Y-%m-%d %H:%M}"
                    f"\nКоличество записей : {num_of_rows}",
            file=report_file
        )
    else:
        await BOT.send_message(
            event.chat_id,
            message=f"Данные не найдены, не смог сгенерировать отчёт. {EMOJI.PROBLEM_FACE}"
        )
    raise events.StopPropagation
