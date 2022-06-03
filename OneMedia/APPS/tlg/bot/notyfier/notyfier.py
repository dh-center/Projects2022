import asyncio
import html
import inspect
from typing import List

from telethon import Button

from APPS.entyties import CommonMessage, VK, WEB, TLG
from APPS.logger import log
from APPS.stat_monitoring import log_exception_without_stat
from APPS.text_processing_utils.text_processors import text_to_words
from APPS.tlg.bot.action_log import UserAction
from APPS.tlg.bot.bot_configuration import BOT
from APPS.tlg.bot.notyfier.notify_repo import get_notify_anchors, get_vk_messages, \
    update_anchors_on_restart, NotifyAnchor, get_web_messages, get_tlg_messages
from APPS.tlg.bot.profile.profile_utils import user_has_enabled_subscriptions
from APPS.tlg.bot.subscription.subscription_repo import UserSubscription, UserQuery, get_all_subscriptions_list


async def keep_notify_alive():
    await update_anchors_on_restart()
    log("Notify initiated")
    while True:
        await notify()
        await asyncio.sleep(5)


async def notify_on_message(msg: CommonMessage, subscriptions: List[UserSubscription]):
    log(f"Try notifying on message {msg.source} : {msg.uid}")
    words = text_to_words(msg.content.lower() + " " + str(msg.title).lower())
    for subscription in subscriptions:
        if not await user_has_enabled_subscriptions(subscription.user_id):
            continue
        query: UserQuery = subscription.query
        if not query.has_terms():
            continue

        # check channels
        search_query = query.query
        if msg.source not in search_query.get_sources_set():
            continue
        if search_query.channels_included and (msg.source, msg.channel_name) not in search_query.channels_included:
            continue
        if search_query.channels_excluded and (msg.source, msg.channel_name) in search_query.channels_excluded:
            continue

        should_notify = True

        # check must terms
        for term in search_query.must_terms:
            if isinstance(term, list):
                if any(st.lower() in words for st in term): continue
            elif isinstance(term, str):
                if term.lower() in words: continue
            should_notify = False
            break
        if not should_notify:
            continue

        if not search_query.must_terms:
            # check at least one should term match
            should_notify = False
            for term in search_query.should_terms:
                if isinstance(term, list):
                    if any(st.lower() in words for st in term):
                        should_notify = True
                        break
                elif isinstance(term, str):
                    if term.lower() in words:
                        should_notify = True
                        break
            if not should_notify:
                continue

        # check excluded terms
        for term in search_query.excluded_terms:
            if isinstance(term, list):
                if any(st.lower() in words for st in term):
                    should_notify = False
            elif isinstance(term, str):
                if term.lower() in words:
                    should_notify = False
            if not should_notify:
                break
        if not should_notify:
            continue

        # log
        log(f"Notified on message {msg.source} : {msg.uid}, user {subscription.user_id}")
        await UserAction(
            user_id=subscription.user_id, name="user_notify",
            data={"source": msg.source, "uid": msg.uid, "subscription_uid": subscription.uid}
        ).log()

        await BOT.send_message(
            subscription.user_id,
            message=get_message_description(msg, subscription),
            buttons=Button.url("Открыть новость", url=msg.link),
            parse_mode='html'
        )


def get_message_description(msg: CommonMessage, subscription: UserSubscription):
    res = inspect.cleandoc(
        f"""<b>Query</b> : {subscription.query.name} (uid: {subscription.query.uid})
(for subscription uid: {subscription.uid})
        
<b>Source</b> : {msg.source}
<b>Channel name</b> : {msg.channel_name}

<b>msg uid</b>: {msg.uid}
<b>Found time</b> : {msg.created_time}
<b>Title</b> : {html.escape(str(msg.title))}
<b>Image</b> : {msg.meta_image}
<b>Content</b> : {html.escape(msg.content)}
""")
    appendix = "...\n(полный текст новости смотрите в источнике)" if len(res) > 4000 else ""
    return res[:4000] + appendix


async def notify():
    anchors = await get_notify_anchors()
    log(f"Anchors : {anchors}")
    subscriptions = [subscription async for subscription in get_all_subscriptions_list()]
    for anchor in anchors:
        messages = await get_messages_for_anchor(anchor)
        for message in messages:
            try:
                await notify_on_message(message, subscriptions)
            except Exception as exp:
                log_exception_without_stat(f"Exception on message : {message}", exp)


async def get_messages_for_anchor(anchor: NotifyAnchor) -> List[CommonMessage]:
    res = []
    if anchor.source_type == VK:
        res = await get_vk_messages(anchor.last_uid)
    elif anchor.source_type == WEB:
        res = await get_web_messages(anchor.last_uid)
    elif anchor.source_type == TLG:
        res = await get_tlg_messages(anchor.last_uid)

    if res:
        # save last processed uid
        anchor.last_uid = res[-1].uid
        await anchor.save()
        return res
    return []
