import datetime
import time
from typing import List

import vk_api

from APPS.logger import log
from APPS.stat_monitoring import tell_vk_extractor_is_alive, stat, Source, EventName, log_exception
from APPS.vk.dao_layer import get_all_anchors, insert_vk_message, update_vk_anchor, get_message_by_ids, \
    update_vk_message_anchor, insert_vk_message_anchor_user
from APPS.vk.vk_api_tools import get_vk_tools, get_vk_session
from PROPERTIES.VK_PROPERTIES import VK_PROPERTIES


def get_photos_urls_from_item(item, channel_name: str) -> List[str]:
    res = []
    if 'attachments' not in item:
        return res
    attachments = item['attachments']
    for attachment in attachments:
        try:
            if attachment.get('type', None) != 'photo' or 'photo' not in attachment:
                continue
            photo = attachment['photo']
            if 'sizes' not in photo:
                continue
            sizes = photo['sizes']
            if not sizes:
                continue
            biggest_img = sizes[-1]
            res.append(biggest_img['url'])
        except Exception as exp:
            log_exception(
                source=Source.VK, channel_name=channel_name, event_name=EventName.EXCEPTION, exp=exp,
                msg="get_photos_urls_from_item() exception"
            )

    return res


def download_data(group_id, group_name, last_id):
    log(f"Collecting data for channel_name : {group_name}({group_id}) and last_id : {last_id}")
    try:
        number_of_news = 300
        all_to_save = []
        pinned = []

        count = 0
        while True:
            time.sleep(1)
            wall = get_vk_tools().get_all_slow_iter(
                method='wall.get',
                max_count=100,
                values={
                    'owner_id': "-" + str(group_id), "offset": str(count)
                }
            )
            is_completed = False
            for item in wall:
                count += 1
                post_id = item['id']
                if (last_id is not None and post_id == last_id) or count > number_of_news:
                    is_completed = True
                    break
                if 'is_pinned' in item and item['is_pinned'] == 1:
                    pinned.append(
                        [post_id, item['owner_id'], item['from_id'], item['text'], item['date'],
                         get_photos_urls_from_item(item, group_name)]
                    )
                    continue
                all_to_save.append(
                    [post_id, item['owner_id'], item['from_id'], item['text'], item['date'],
                     get_photos_urls_from_item(item, group_name)]
                )
            if last_id is None or is_completed:
                break
        return all_to_save, pinned, None if len(all_to_save) == 0 else all_to_save[0][0]
    except vk_api.AuthError as exp:
        log_exception(
            source=Source.VK, channel_name=group_name, event_name=EventName.EXCEPTION, exp=exp,
            msg="download_data() exception"
        )
        return


def get_group_id_by_name(name):
    result = get_vk_session().method('groups.getById', {'group_id': name, 'fields': "members_count"})
    result = result[0]
    return [result['id'], result['name'], result['screen_name'], result['members_count']]


def get_group_by_name_or_id(id: str):
    result = get_vk_session().method('groups.getById', {'group_id': id, 'fields': "members_count"})
    result = result[0]
    log(f"get_group_by_name_or_id : {result}")
    return [result['id'], result['name'], result['screen_name'], result['members_count']]


def get_user_info_by_name_or_id(name_or_id: str):
    result = get_vk_session().method('users.get', {'user_ids': name_or_id, 'fields': "followers_count,screen_name"})
    result = result[0]
    log(f"get_user_info_by_name_or_id : {result}")
    return [
        result['id'], f"{result['first_name']} {result['last_name']}", result['screen_name'],
        result["followers_count"]
    ]


def start_extract():
    anchors = None
    while not anchors:
        anchors = get_all_anchors()
        time.sleep(3)
    log(f"Started aggregation with anchors : {anchors}")

    stats = {}
    tell_vk_extractor_is_alive(msg="Start channels iteration")
    len_anchors = len(anchors)
    for ind, (channel_name, channel_id, screen_name, last_message_id, participants, last_time_updated_info, is_group) \
            in enumerate(anchors, start=1):
        try:
            tell_vk_extractor_is_alive(
                msg=f"Went to sleep on {screen_name} for : {VK_PROPERTIES.get_sleep_time_channel()} seconds "
                    f"({ind} out of {len_anchors})"
            )
            time.sleep(VK_PROPERTIES.get_sleep_time_channel())
            if is_group:
                if not participants or not last_time_updated_info \
                        or (datetime.datetime.now() - datetime.timedelta(days=1) > last_time_updated_info):
                    if is_group:
                        info = get_group_by_name_or_id(channel_id)
                    else:
                        info = get_user_info_by_name_or_id(channel_id)
                    update_vk_message_anchor(*info)
            messages, pinned_messages, last_anchor = download_data(channel_id, screen_name, last_message_id)
            saved: int = 0
            for message in messages:
                if insert_vk_message(*message, channel_name=screen_name):
                    saved += 1
            for message in pinned_messages:
                if len(get_message_by_ids(message[0], channel_id)) == 0:
                    if insert_vk_message(*message, channel_name=screen_name):
                        saved += 1
            stat(source=Source.VK, channel_name=str(screen_name), event_name=EventName.SAVE_NEWS)
            if last_anchor is not None:
                update_vk_anchor(last_anchor, channel_id, channel_name=screen_name)
            stats[(screen_name, channel_id)] = {
                "pinned": len(pinned_messages),
                "normal": len(messages),
                "last_anchor": last_anchor
            }
        except Exception as exp:
            log_exception(
                source=Source.VK, channel_name="OneMedia:VK:ALL", event_name=EventName.EXCEPTION, exp=exp,
                msg="start_extract() exception"
            )
    log(f"Aggregation is completed, stats: \n{stats}")


if __name__ == '__main__':
    try:
        while True:
            start_extract()

            tell_vk_extractor_is_alive(msg=f"Went to sleep for : {VK_PROPERTIES.sleep_time_approaches} seconds")
            time.sleep(VK_PROPERTIES.sleep_time_approaches)
    except Exception as exp:
        log_exception(
            source=Source.VK, channel_name="OneMedia:VK:ALL", event_name=EventName.EXCEPTION, exp=exp,
            msg="start exception"
        )

# prepopulate groups
# insert_vk_message_anchor_group(*get_group_by_name_or_id("lentach"))
# insert_vk_message_anchor_group(*get_group_by_name_or_id("lentaru"))
# insert_vk_message_anchor_group(*get_group_by_name_or_id("true_lentach"))
# insert_vk_message_anchor_group(*get_group_by_name_or_id("meduzaproject"))
# insert_vk_message_anchor_group(*get_group_by_name_or_id("meduzaproject"))

# prepopulete users
# insert_vk_message_anchor_user(*get_user_info_by_name_or_id("durov"))
