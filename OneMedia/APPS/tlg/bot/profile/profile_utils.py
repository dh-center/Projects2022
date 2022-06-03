import asyncio
from typing import Set

from telethon import events
from telethon.tl.types import User

from APPS.tlg.bot.profile.profile_repo import UserInfo, UserMetaData, get_enabled_overall_subscriptions_user_set


def construct_user_info_from_event(event: events.NewMessage.Event) -> UserInfo:
    user: User = event.chat
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    username = user.username
    login = username

    full_name = f"{first_name} {last_name} ({username})"
    return UserInfo(user_id=event.chat_id, name=full_name, login=login, meta=UserMetaData())


ENABLED_SUBSCRIPTIONS_USER_SET: Set[int] = None


async def user_has_enabled_subscriptions(user_id: int) -> bool:
    return user_id in ENABLED_SUBSCRIPTIONS_USER_SET


async def update_enabled_subscriptions_users_set():
    global ENABLED_SUBSCRIPTIONS_USER_SET
    ENABLED_SUBSCRIPTIONS_USER_SET = await get_enabled_overall_subscriptions_user_set()


def turn_off_overall_subscriptions_for_user(user_id: int):
    global ENABLED_SUBSCRIPTIONS_USER_SET
    ENABLED_SUBSCRIPTIONS_USER_SET.discard(user_id)


def turn_on_overall_subscriptions_for_user(user_id: int):
    global ENABLED_SUBSCRIPTIONS_USER_SET
    ENABLED_SUBSCRIPTIONS_USER_SET.add(user_id)


asyncio.get_event_loop().run_until_complete(update_enabled_subscriptions_users_set())
