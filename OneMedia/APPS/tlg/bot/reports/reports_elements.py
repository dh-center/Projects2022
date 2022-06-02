from datetime import datetime, timedelta

from telethon import Button

from APPS.tlg.bot.action_storage import ActionStorage
from APPS.tlg.bot.subscription.subscription_repo import UserQuery
from APPS.tlg.emoji_bot import EMOJI

ACTION_CHOOSE_QUERY = "ACTION_CHOOSE_QUERY_FOR_REPORT"
GET_DATA_ADD_SUBSCRIPTION = "add_subscription"

ACTION_CHOOSE_1DAY = "ACTION_CHOOSE_1DAY_REPORT"
ACTION_CHOOSE_1WEEK = "ACTION_CHOOSE_1WEEK_REPORT"
ACTION_CHOOSE_1MONTH = "ACTION_CHOOSE_1MONTH_REPORT"
ACTION_CHOOSE_3MONTHS = "ACTION_CHOOSE_3MONTHS_REPORT"


def get_query_list_button(query: UserQuery):
    return Button.inline(
        text=f"{query.name} (query uid: {query.uid})",
        data=ActionStorage.put_data(ACTION_CHOOSE_QUERY, query)
    )


def get_report_time_variants(query: UserQuery):
    return {
        "message": f"{EMOJI.POINT_DOWN} Выберите промежуток времени для генерации отчёта {EMOJI.POINT_DOWN}",
        "buttons": [
            [
                Button.inline(
                    "1 day",
                    data=ActionStorage.put_data(ACTION_CHOOSE_1DAY, (ACTION_CHOOSE_1DAY, query))
                ),
                Button.inline(
                    "1 week",
                    data=ActionStorage.put_data(ACTION_CHOOSE_1WEEK, (ACTION_CHOOSE_1WEEK, query))
                ),
                Button.inline(
                    "1 month",
                    data=ActionStorage.put_data(ACTION_CHOOSE_1MONTH, (ACTION_CHOOSE_1MONTH, query))
                ),
                Button.inline(
                    "3 months",
                    data=ActionStorage.put_data(ACTION_CHOOSE_3MONTHS, (ACTION_CHOOSE_3MONTHS, query))
                ),
            ]
        ]
    }


def get_from_time_from_action(action_name: str) -> datetime:
    now = datetime.now()
    time_delta = None
    if action_name == ACTION_CHOOSE_1DAY:
        time_delta = timedelta(days=1)
    elif action_name == ACTION_CHOOSE_1WEEK:
        time_delta = timedelta(weeks=1)
    elif action_name == ACTION_CHOOSE_1MONTH:
        time_delta = timedelta(days=30)
    elif action_name == ACTION_CHOOSE_3MONTHS:
        time_delta = timedelta(days=30 * 3)
    else:
        raise RuntimeError(f"No such action name : {action_name}")

    return now - time_delta
