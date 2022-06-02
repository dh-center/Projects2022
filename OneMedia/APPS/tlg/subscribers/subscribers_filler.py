import json
import time

import requests

from APPS.logger import log
from APPS.tlg.dao_layer import update_anchor_attributes_subscribers, retrieve_all_channels
from PROPERTIES.BOT_USED_FOR_API_CALLS import BOT_API_PROPERTIES

turn = 0
tokens = list(set(BOT_API_PROPERTIES.tokens.split(",")))
log(f"Have {len(tokens)} : {tokens}")
# not more than only 100 queries per day (should do it constantly)
sleep_time = 24 * 3600 / (95 * len(tokens))


def get_url():
    global turn, tokens
    turn += 1
    turn %= len(tokens)

    log(f"Used token {turn} : {tokens[turn]}")
    return f"https://api.telegram.org/bot{tokens[turn]}/getChatMembersCount?chat_id=@"


def get_num_of_subscribers(channel_name, subscribers_before):
    try:
        response = requests.get(get_url() + channel_name)
        answer = json.loads(response.content.decode('utf-8'))
        if 'result' in answer:
            return "OK", answer['result']
        log(f"Bad request! with status: ${response.status_code} and message: {answer}")
        if 'description' in answer and 'not found' in answer['description']:
            return "NOT_FOUND", subscribers_before
        return "OTHER", subscribers_before
    except Exception as exp:
        log(f"Cannot get subscribers for {channel_name} with {exp}")
        return "OTHER", subscribers_before


def initialise_subscribers(channel_id, channel_name, subscribers_before):
    global sleep_time

    time.sleep(1)
    system_mark, subscribers = get_num_of_subscribers(channel_name, subscribers_before)
    time.sleep(sleep_time)

    log(f"Update channel {channel_name} with subscribers {subscribers}, put system_mark: {system_mark}")
    update_anchor_attributes_subscribers(channel_id, channel_name, subscribers, system_mark)
    log(f"Will sleep for {sleep_time}")
    return subscribers


count = 0

while True:
    all_channels = retrieve_all_channels()

    all_filtered = [
        (
            channel, last_message, channel_id, channel_display_text, channel_type, system_mark, subscribers,
            sub_update_time
        )
        for
        channel, last_message, channel_id, channel_display_text, channel_type, system_mark, subscribers, sub_update_time
        in all_channels if system_mark != 'NOT_FOUND'
    ]

    # without subscribers have priority
    all_filtered.sort(
        key=lambda item: item[7].timestamp() if item[6] is not None else item[7].timestamp() - 1571005498
    )

    log(f"first: {all_filtered[0][7].timestamp()}, last: {all_filtered[-1][7].timestamp()}")
    log("all_channels len: " + str(len(all_channels)))
    log("all_filtered len: " + str(len(all_filtered)))
    log("all_filtered: " + str([item[7].timestamp() for item in all_filtered[:100]]))
    log("sleep_time: " + str(sleep_time))

    for ind, (
            channel, last_message, channel_id, channel_display_text, channel_type, system_mark, subscribers,
            sub_update_time
    ) in enumerate(all_filtered, start=1):

        if ind > 50:
            log(">>>>>>>>> Filtered Reinit <<<<<<<<<")
            break

        log(f"channel: {channel} subscribers: {subscribers}")
        try:
            initialise_subscribers(channel_id, channel, subscribers)
        except Exception as e:
            print(e)
        count += 1
        log(f"initialised! {count}")
        log("============================================================================")
