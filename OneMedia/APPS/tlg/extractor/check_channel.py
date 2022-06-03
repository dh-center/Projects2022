import json
import time
from random import random
from urllib.request import urlopen

from APPS.logger import log
from APPS.tlg.dao_layer import update_anchor_attributes_subscribers
from PROPERTIES.BOT_USED_FOR_API_CALLS import BOT_API_PROPERTIES

url = f"https://api.telegram.org/bot{BOT_API_PROPERTIES.tokens[0]}/getChatMembersCount?chat_id=@"
skipped_processing = {}
skip_number = 750


def get_num_of_subscribers(channel_name):
    try:
        with urlopen(url + channel_name) as f:
            resp = json.load(f)

        return True, resp['result']
    except Exception as exp:
        log(f"Cannot get subscribers for {channel_name} with {exp}")
        return False, 0


def is_eligible_for_processing(channel_id, channel_name, subscribers):
    global skipped_processing, skip_number
    if subscribers is None:
        result, subscribers = initialise_subscribers(channel_id, channel_name)
        if not result:
            log(f"Fallen on initialisation of subscribers for channel {channel_name} with id {channel_id}")
            return False, "INIT_FALL", subscribers
        else:
            log(f"Initialised subscribers for channel {channel_name} with id {channel_id} subscribers {subscribers}")
            return subscribers >= skip_number, "INIT_OK", subscribers

    update_subscribers_result, update_subscribers_message = lazily_update_subscribers(channel_id, channel_name)

    if not update_subscribers_result:
        log(f"Fallen on lazily_update_subscribers for channel {channel_name} with id {channel_id}")
        return subscribers >= skip_number, "LAZY_FALL", subscribers

    if update_subscribers_message == "LAZY_ACTIVE":
        return subscribers >= skip_number, "LAZY_OK", subscribers

    return subscribers >= skip_number, "OK", subscribers


def initialise_subscribers(channel_id, channel_name):
    result, subscribers = get_num_of_subscribers(channel_name)
    time.sleep(7)
    if result:
        log(f"Update channel {channel_name} with subscribers {subscribers}")
        update_anchor_attributes_subscribers(channel_id, channel_name, subscribers)
        return True, subscribers
    return False, 0


def lazily_update_subscribers(channel_id, channel_name):
    if channel_id not in skipped_processing:
        skipped_processing[channel_id] = 0

    skipped_processing[channel_id] += 1

    if skipped_processing[channel_id] >= 7:
        skipped_processing[channel_id] = 0

    if skipped_processing[channel_id] == 3 + (int(channel_id) % 4) and random() > 0.7:
        result, _ = initialise_subscribers(channel_id, channel_name)
        return result, "LAZY_ACTIVE"
    return True, "LAZY_SKIPPED"

# print(get_num_of_subscribers("karaulny"))
