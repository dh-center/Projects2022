from typing import List

from telethon import events

from APPS.tlg.bot.action_storage import action_dispatcher
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.profile.profile_repo import get_user_info_by_user_id, UserInfo
from APPS.tlg.bot.profile.profile_utils import turn_on_overall_subscriptions_for_user, \
    turn_off_overall_subscriptions_for_user
from APPS.tlg.bot.queries.queries_elements import get_query_vew_edit_description
from APPS.tlg.bot.subscription.subscription_elements import BUTTON_MY_SUBSCRIPTIONS, \
    ACTION_REMOVE_SUBSCRIPTION, \
    ACTION_VIEW_SUBSCRIPTION, GET_DATA_EDIT_SUBSCRIPTION, GET_DATA_ADD_SUBSCRIPTION, ACTION_DISABLE_SUBSCRIPTION, \
    ACTION_ENABLE_SUBSCRIPTION, \
    get_enabled_subscription_description, get_disabled_subscription_description, \
    BUTTON_TURN_OFF_SUBSCRIPTIONS, BUTTON_TURN_ON_SUBSCRIPTIONS, get_main_menu_elements, \
    get_subscription_element_elements
from APPS.tlg.bot.subscription.subscription_repo import get_subscriptions_list, UserSubscription, delete_subscription, \
    get_subscription, NewsQuery, UserQuery, get_queries_list
from APPS.tlg.emoji_bot import EMOJI


async def subscription_main_menu_press_button(event: events.NewMessage.Event):
    user_info = await get_user_info_by_user_id(event.chat_id)
    await BOT.send_message(event.chat_id, **(await get_main_menu_elements(user_info)))
    raise events.StopPropagation


@BOT.on(events.CallbackQuery(pattern=f'^{BUTTON_MY_SUBSCRIPTIONS}'))
async def get_subscription_list_description(event: events.CallbackQuery.Event):
    subscriptions: List[UserSubscription] = await get_subscriptions_list(event.chat_id)
    queries: List[UserQuery] = await get_queries_list(event.chat_id)

    subscriptions_map = {subscription.query.uid: subscription for subscription in subscriptions}

    real_subscriptions = [
        (await get_real_subscription_for_query(query, subscriptions_map.get(query.uid, None)))
        for query in queries
    ]
    await BOT.send_message(event.chat_id, message=f"{EMOJI.POINT_DOWN} Ваши подписки {EMOJI.POINT_DOWN}")
    for subscription in real_subscriptions:
        await BOT.send_message(event.chat_id, **(await get_subscription_element_elements(subscription)))
    raise events.StopPropagation


async def get_real_subscription_for_query(query: UserQuery, subscription: UserSubscription):
    if subscription: return subscription
    return UserSubscription(query.user_id, query)


@action_dispatcher(action_name=ACTION_VIEW_SUBSCRIPTION)
async def view_subscription(event: events.CallbackQuery.Event, subscription: UserSubscription):
    await BOT.send_message(
        event.chat_id,
        message=get_query_vew_edit_description(subscription.query)
    )
    raise events.StopPropagation


@action_dispatcher(action_name=ACTION_REMOVE_SUBSCRIPTION)
async def remove_subscription(event: events.CallbackQuery.Event, subscription: UserSubscription):
    res = await delete_subscription(subscription.uid)
    msg = f'Не смог удалить : "{subscription.subscription_name}"!'
    if res:
        msg = f'"{subscription.subscription_name}" {EMOJI.BASKET} удалено.'
    await BOT.delete_messages(event.chat, message_ids=[event.message_id])
    await BOT.send_message(event.chat_id, message=msg)
    raise events.StopPropagation


async def rebuild_subscription_item_menu_on_event(event: events.CallbackQuery.Event, subscription: UserSubscription):
    elements = await get_subscription_element_elements(subscription)
    await BOT.edit_message(
        event.chat, message=event.message_id,
        text=elements['message'],
        buttons=elements['buttons']
    )


@action_dispatcher(action_name=ACTION_DISABLE_SUBSCRIPTION)
async def disable_subscription(event: events.CallbackQuery.Event, subscription: UserSubscription):
    await delete_subscription(subscription.uid)
    subscription.uid = None
    await rebuild_subscription_item_menu_on_event(event, subscription)
    await BOT.send_message(event.chat_id, message=await get_disabled_subscription_description(subscription))
    raise events.StopPropagation


@action_dispatcher(action_name=ACTION_ENABLE_SUBSCRIPTION)
async def enable_subscription(event: events.CallbackQuery.Event, subscription: UserSubscription):
    await subscription.save()
    await rebuild_subscription_item_menu_on_event(event, subscription)
    await BOT.send_message(event.chat_id, message=await get_enabled_subscription_description(subscription))
    raise events.StopPropagation


@BOT.on(events.NewMessage(pattern=fr"^{GET_DATA_EDIT_SUBSCRIPTION}"))
async def edit_subscription_get_data(event: events.NewMessage.Event):
    lines = event.message.raw_text.splitlines()
    first_line = lines[0]
    uid = int(first_line.split(" ")[-1])
    subscription = await get_subscription(uid)
    subscription.subscription_name = lines[1][len("Name:"):].strip()
    subscription.query = NewsQuery.from_json("\n".join(lines[2:]))
    await subscription.save()
    await BOT.send_message(
        event.chat_id,
        message=f"Для подписки {uid} {EMOJI.NEWS_PAPER} изменения сохранены."
    )
    raise events.StopPropagation


async def rebuild_main_menu_on_event(event: events.CallbackQuery.Event, user_info: UserInfo):
    elements = await get_main_menu_elements(user_info)
    await BOT.edit_message(
        event.chat, message=event.message_id,
        text=elements['message'],
        buttons=elements['buttons']
    )


@BOT.on(events.CallbackQuery(pattern=f'^{BUTTON_TURN_OFF_SUBSCRIPTIONS}'))
async def turn_off_subscriptions(event: events.CallbackQuery.Event):
    turn_off_overall_subscriptions_for_user(event.chat_id)
    user_info = await get_user_info_by_user_id(event.chat_id)
    user_info.meta.enable_subscription = False
    await user_info.save()
    await rebuild_main_menu_on_event(event, user_info)
    await BOT.send_message(event.chat_id, message="Нотификация по подпискам отключена.")
    raise events.StopPropagation


@BOT.on(events.CallbackQuery(pattern=f'^{BUTTON_TURN_ON_SUBSCRIPTIONS}'))
async def turn_on_subscriptions(event: events.CallbackQuery.Event):
    turn_on_overall_subscriptions_for_user(event.chat_id)
    user_info = await get_user_info_by_user_id(event.chat_id)
    user_info.meta.enable_subscription = True
    await user_info.save()
    await rebuild_main_menu_on_event(event, user_info)
    await BOT.send_message(event.chat_id, message="Нотификация по подпискам актививрована.")
    raise events.StopPropagation


@BOT.on(events.NewMessage(pattern=fr"^{GET_DATA_ADD_SUBSCRIPTION}"))
async def add_subscription_get_data(event: events.NewMessage.Event):
    lines = event.message.raw_text.splitlines()
    subscription_name = lines[1][len("Name:"):].strip()
    query = NewsQuery.from_json("\n".join(lines[2:]))
    subscription = UserSubscription(
        user_id=event.chat_id,
        subscription_name=subscription_name,
        query=query
    )
    await subscription.save()
    await BOT.send_message(
        event.chat_id,
        message=f"Подписка {subscription.uid} {EMOJI.NEWS_PAPER} добавлена."
    )
    raise events.StopPropagation
