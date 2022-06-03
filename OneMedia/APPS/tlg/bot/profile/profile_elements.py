import hashlib
import inspect

from telethon import events
from telethon.tl.types import User

from APPS.tlg.bot.subscription.subscription_repo import get_number_of_subscriptions_by_user
from APPS.tlg.emoji_bot import EMOJI
from APPS.tlg.jwt_provider import get_jwt


async def get_profile_description(event: events.NewMessage.Event) -> str:
    user: User = event.chat
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    username = user.username
    password = hashlib.md5((username + "_oneMedia").encode("utf-8")).hexdigest()

    res = f"""
    **User**: {first_name} {last_name} ({username})
    **Rights**: Unlimited
    **Phone verification**: not provided
    **UI login**: {username}
    **UI password**: {password}
    **System usage info**
    **Подписок**: {await get_number_of_subscriptions_by_user(event.chat_id)} {EMOJI.NEWS_PAPER}
    **Api token (X-One-Media header)**: {get_jwt(username)} 
    """

    return inspect.cleandoc(res)
