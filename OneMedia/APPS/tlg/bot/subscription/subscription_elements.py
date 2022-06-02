import inspect

from telethon import Button

from APPS.tlg.bot.action_storage import ActionStorage
from APPS.tlg.bot.profile.profile_repo import UserInfo
from APPS.tlg.bot.subscription.subscription_repo import get_number_of_subscriptions_by_user, UserSubscription
from APPS.tlg.emoji_bot import EMOJI

GET_DATA_EDIT_SUBSCRIPTION = "edit_subscription"
GET_DATA_ADD_SUBSCRIPTION = "add_subscription"

ACTION_VIEW_SUBSCRIPTION = "Просмотреть подписку"
ACTION_REMOVE_SUBSCRIPTION = "Удалить подписку"
ACTION_EDIT_SUBSCRIPTION = "Изменить подписку"
ACTION_DISABLE_SUBSCRIPTION = "Disable подписку"
ACTION_ENABLE_SUBSCRIPTION = "Enable подписку"

BUTTON_MY_SUBSCRIPTIONS = "Мои подписки"
BUTTON_TURN_OFF_SUBSCRIPTIONS = f"Отключить сервис {EMOJI.GRAY_CROSS}"
BUTTON_TURN_ON_SUBSCRIPTIONS = f"Включить сервис {EMOJI.LAMP}"
BUTTON_VIEW_SUBSCRIPTION = "View"
BUTTON_REMOVE_SUBSCRIPTION = "Remove"
BUTTON_DISABLE_SUBSCRIPTION = "Disable"
BUTTON_ENABLE_SUBSCRIPTION = "Enable"


async def get_subscription_element_elements(subscription: UserSubscription):
    return {
        "message": get_subscription_list_subscription_description(subscription),
        "buttons": [
            [
                Button.inline(
                    BUTTON_VIEW_SUBSCRIPTION,
                    data=ActionStorage.put_data(ACTION_VIEW_SUBSCRIPTION, subscription)
                ),
                get_activation_button(subscription),
            ]
        ]
    }


async def get_main_menu_elements(user_info: UserInfo):
    return {
        "message": await get_main_subscription_description(user_info),
        "buttons": [
            [Button.inline(BUTTON_MY_SUBSCRIPTIONS)],
            [get_overall_activation_button(user_info)]
        ]
    }


async def get_main_subscription_description(user_info: UserInfo) -> str:
    number_of_subscriptions = await get_number_of_subscriptions_by_user(user_info.user_id)
    warning = ""
    if not user_info.meta.enable_subscription:
        warning = f"\n(Вы **отключили** сервис подписок{EMOJI.EXCLAMATIONS})"
    res = f"""
    У вас {number_of_subscriptions} {EMOJI.NEWS_PAPER} активированных подписок.{warning}
    
    {EMOJI.POINT_DOWN} Управление подписками {EMOJI.POINT_DOWN}
    """
    return inspect.cleandoc(res)


async def get_subscription_description(subscription: UserSubscription) -> str:
    res = f"""
{EMOJI.NEWS_PAPER} **Информация о подписке**:
**Name**: {subscription.subscription_name}
```{subscription.query.to_json()}
```
    """
    return inspect.cleandoc(res)


async def get_edit_subscription_description(subscription: UserSubscription) -> str:
    res = f"""
{EMOJI.POINT_RIGHT} Чтобы поменять подписку отправьте 
{GET_DATA_EDIT_SUBSCRIPTION} {subscription.uid} + измененный JSON запроса.

**Общий шаблон**: ```{GET_DATA_EDIT_SUBSCRIPTION} {subscription.uid}
Name: {subscription.subscription_name} // имя можно изменить
{{
  "channels": [("<имя источнка>","<название канала>")],
  "enabled": true, // включена ли query
  "is_global": true, // если true "channels" не нужны
  "terms": [ 
    // списками указываются синонимы, 
    // буду искать те документы в которых есть все термы внешнего списка
    ["терм1","терм1синоним1", "терм1синоним2"],
    "терм2"
  ]
}}
```

Текущие данные:
```{GET_DATA_EDIT_SUBSCRIPTION} {subscription.uid}
Name: {subscription.subscription_name}
{subscription.query.to_json()}
```
"""
    return inspect.cleandoc(res)


def get_add_subscription_description() -> str:
    res = f"""
Все доступные каналы можно посмотреть во вкладке меню **"Каналы"**

**Шаблон на отправку**:
```
{GET_DATA_ADD_SUBSCRIPTION}
Name: <имя подписки>
{{
  "channels": [("<имя источнка>","<название канала>")],
  "enabled": true, // включена ли query
  "is_global": true, // если true "channels" не нужны
  "terms": [ 
    // списками указываются синонимы, 
    // буду искать те документы в которых есть все термы внешнего списка
    ["терм1","терм1синоним1", "терм1синоним2"],
    "терм2"
  ]
}}
```
"""
    return inspect.cleandoc(res)


async def get_enabled_subscription_description(subscription: UserSubscription) -> str:
    return f"Подписка : ({subscription.query.uid}) {subscription.query.name}  активирована {EMOJI.LAMP}"


async def get_disabled_subscription_description(subscription: UserSubscription) -> str:
    return f"Подписка : ({subscription.query.uid}) {subscription.query.name}  деактивирована {EMOJI.GRAY_CROSS}"


def get_activation_button(subscription: UserSubscription) -> Button:
    if subscription.uid:
        return Button.inline(
            BUTTON_DISABLE_SUBSCRIPTION,
            data=ActionStorage.put_data(ACTION_DISABLE_SUBSCRIPTION, subscription)
        )
    return Button.inline(
        BUTTON_ENABLE_SUBSCRIPTION,
        data=ActionStorage.put_data(ACTION_ENABLE_SUBSCRIPTION, subscription)
    )


def get_overall_activation_button(user_info: UserInfo) -> Button:
    if user_info.meta.enable_subscription:
        return Button.inline(BUTTON_TURN_OFF_SUBSCRIPTIONS)
    return Button.inline(BUTTON_TURN_ON_SUBSCRIPTIONS)


def get_subscription_list_subscription_description(subscription: UserSubscription):
    activation: str = EMOJI.LAMP
    if not subscription.uid:
        activation = EMOJI.GRAY_CROSS
    return f"{activation} {subscription.query.name} (**query uid:** {subscription.query.uid})"
