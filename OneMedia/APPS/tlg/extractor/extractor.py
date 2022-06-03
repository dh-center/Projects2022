import time

from telethon.tl.types import Channel, Message

from APPS.logger import log
from APPS.stat_monitoring import log_exception, Source, EventName, tell_extractor_is_alive
from APPS.tlg.dao_layer import retrieve_all_channels, initialise_anchor, \
    insert_message_tg_without_transaction_tg, update_anchor_attributes, initialise_anchor_by_channel_name, clean_chat_id
from APPS.tlg.emoji_bot import EMOJI
from PROPERTIES.TLG_EXTRACTOR_PROPERTIES import PROPERTIES


class ExtractorStats:

    def __init__(self, all_channels):
        self.fallen_channels = 0
        self.successful_channels = 0
        self.not_empty_channels = 0
        self.empty_channels = 0
        self.not_empty_successful_channels = 0
        self.possible_to_save_messages = 0
        self.missed_to_save_messages = 0
        self.saved_messages = 0
        self.skipped_as_another_type = 0

        self.client_iter_count = 0
        self.client_iter_count_success = 0
        self.client_iter_count_fallback = 0
        self.client_iter_count_fallback_success = 0

        self.attrs_changed = 0
        self.attrs_changed_succ = 0
        self.all_channels_size = len(all_channels)

        self.forward_encountered = 0
        self.forward_started_to_extract = 0
        self.forward_rejected_not_channel_type = 0
        self.forward_fallen_on_add = 0
        self.forward_added_in_db = 0
        self.forward_already_in = 0
        self.forward_with_empty_id = 0

        self.stopped_encountered = 0

        self.subscription_check_more = 0
        self.subscription_check_less = 0
        self.subscription_init_has_fallen = 0
        self.subscription_init_has_succ = 0
        self.subscription_lazy_update_has_fallen = 0
        self.subscription_lazy_update_succ = 0


def aggregate_massages():
    prev_full_cycle = 0
    while True:
        start = time.time()

        tell_extractor_is_alive(msg="Starting channels iteration")

        # stats of iteration
        all_channels = retrieve_all_channels()

        iteration_channels_ids = {channel_id for
                                  channel, last_message, channel_id, channel_display_text, channel_type, system_mark, subscribers, sub_update_time
                                  in
                                  all_channels}

        cur_stats: ExtractorStats = ExtractorStats(all_channels)

        for ind, (
                channel, last_message, channel_id, channel_display_text, channel_type, system_mark, subscribers,
                sub_update_time) in enumerate(
            all_channels, start=1):
            log(f"Check channel : {channel}:{(channel, last_message, channel_id, channel_display_text, channel_type, system_mark, subscribers, sub_update_time)}")

            if system_mark == "STOPPED":
                cur_stats.stopped_encountered += 1
                log("STOPPED will skip {channel}! ")
                continue

            # result, eligibility_message, subscribers = is_eligible_for_processing(channel_id, channel, subscribers)
            #
            # if eligibility_message == "INIT_FALL":
            #     cur_stats.subscription_init_has_fallen += 1
            # if eligibility_message == "INIT_OK":
            #     cur_stats.subscription_init_has_succ += 1
            # if eligibility_message == "LAZY_FALL":
            #     cur_stats.subscription_lazy_update_has_fallen += 1
            # if eligibility_message == "LAZY_OK":
            #     cur_stats.subscription_lazy_update_succ += 1
            #
            # log(f"Eligibility info for channel {channel} : {(result, eligibility_message, subscribers)}")
            # if not result:
            #     cur_stats.subscription_check_less += 1
            #     log(f"Subscribers {channel} (id:{channel_id}) amount is too small for processing {subscribers}")
            #     continue
            # else:
            #     cur_stats.subscription_check_more += 1
            #     log(f"Subscribers {channel} (id:{channel_id}) amount is valid for processing {subscribers}")

            with tg_client as client:

                tell_extractor_is_alive(
                    f"Checking channel : {channel} ({ind} out of {cur_stats.all_channels_size})\n"
                    f"\n"
                    f"{EMOJI.SUBSCRIBERS} subscription check more: {cur_stats.subscription_check_more}\n"
                    f"{EMOJI.SUBSCRIBERS} subscription check less (SKIPPED): {cur_stats.subscription_check_less}\n"
                    f"{EMOJI.SUBSCRIBERS} subscription check init fallen: {cur_stats.subscription_init_has_fallen}\n"
                    f"{EMOJI.SUBSCRIBERS} subscription check init succ: {cur_stats.subscription_init_has_succ}\n"
                    f"{EMOJI.SUBSCRIBERS} subscription check lazy update fallen: {cur_stats.subscription_lazy_update_has_fallen}\n"
                    f"{EMOJI.SUBSCRIBERS} subscription check lazy update succ: {cur_stats.subscription_lazy_update_succ}\n"
                    f"\n"
                    f"{EMOJI.EXTRACTOR} fallen channels: {cur_stats.fallen_channels} \n"
                    f"{EMOJI.EXTRACTOR} successful channels: {cur_stats.successful_channels}\n"
                    f"{EMOJI.EXTRACTOR} empty channels: {cur_stats.empty_channels}\n"
                    f"{EMOJI.EXTRACTOR} not empty channels: {cur_stats.not_empty_channels}\n"
                    f"{EMOJI.EXTRACTOR} not empty successful channels: {cur_stats.not_empty_successful_channels}\n"
                    f"ALL: {cur_stats.all_channels_size}\n\n"
                    f"{EMOJI.SAVE} possible to save messages: {cur_stats.possible_to_save_messages}\n"
                    f"{EMOJI.SAVE} saved messages: {cur_stats.saved_messages}\n"
                    f"{EMOJI.SAVE} missed messages: {cur_stats.missed_to_save_messages}\n"
                    f"{EMOJI.SAVE} skipped messages as another type: {cur_stats.skipped_as_another_type}\n\n"
                    f"{EMOJI.DOWNLOAD_ITER} all client_iter() attempts: {cur_stats.client_iter_count}\n"
                    f"{EMOJI.DOWNLOAD_ITER} success client_iter() attempts: {cur_stats.client_iter_count_success}\n"
                    f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts: {cur_stats.client_iter_count_fallback}\n"
                    f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts success: {cur_stats.client_iter_count_fallback_success}\n"
                    f"\n"
                    f"{EMOJI.TIME} time passed since channels iteration start : {round(time.time() - start)} seconds\n"
                    f"{EMOJI.TIME} previous channels iteration took : {prev_full_cycle} seconds\n"
                    f"\n"
                    f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes to be updated: {cur_stats.attrs_changed}\n"
                    f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes are updated: {cur_stats.attrs_changed_succ}\n"
                    f"\n"
                    f"{EMOJI.FORWARDED} forward encountered: {cur_stats.forward_encountered}\n"
                    f"{EMOJI.FORWARDED} started to extract in current iteration: {cur_stats.forward_started_to_extract}\n"
                    f"{EMOJI.FORWARDED} forward rejected as not channel type: {cur_stats.forward_rejected_not_channel_type}\n"
                    f"{EMOJI.FORWARDED} forward fallen on add to the db: {cur_stats.forward_fallen_on_add}\n"
                    f"{EMOJI.FORWARDED} forward added to the db: {cur_stats.forward_added_in_db}\n"
                    f"{EMOJI.FORWARDED} forward were in the db before: {cur_stats.forward_already_in}\n"
                    f"{EMOJI.FORWARDED} forward with an empty id: {cur_stats.forward_with_empty_id}\n"
                    f"{EMOJI.FORWARDED} stopped encountered: {cur_stats.stopped_encountered}\n"
                )
                result_of_saving = True
                try:
                    if channel_id is None:
                        log(f"Channel id for channelName {channel} is None")
                        messages = list(client.iter_messages(
                            entity=channel, limit=20, wait_time=PROPERTIES.wait_time_iter_messages
                        ))
                        channel_id = initialise_anchor_by_channel_name(channel, messages[0], last_message)

                    if last_message == 'NOT_SET':
                        messages = ask_for_messages_with_fallback(client, channel, channel_id, last_message,
                                                                  cur_stats, limit=300)

                        new_anchor = min([message.id for message in messages])
                        initialise_anchor(channel_id, messages[0], new_anchor)
                        log(f"Anchor set for {channel}: {new_anchor}")
                        cur_stats.empty_channels += 1
                    else:
                        if system_mark == "FORWARDED":
                            cur_stats.forward_started_to_extract += 1

                        messages = ask_for_messages_with_fallback(client, channel, channel_id, last_message, cur_stats)

                        log(f"!==== Check channel resulted in {len(messages)} messages=====!")
                        if len(messages) > 0:
                            cur_stats.not_empty_channels += 1
                            new_anchor = max([message.id for message in messages])
                            log(f"Old Anchor: {last_message}, New Anchor: {new_anchor}")

                            # update if name has changed or type has changed
                            channel, channel_display_text, channel_type = update_attrs_of_anchor(messages, channel_id,
                                                                                                 channel,
                                                                                                 channel_display_text,
                                                                                                 channel_type,
                                                                                                 cur_stats)

                            cur_stats.possible_to_save_messages += len(messages)
                            result_of_saving = insert_message_tg_without_transaction_tg(
                                channel, channel_id, channel_display_text, messages, new_anchor
                            )

                            if result_of_saving:
                                cur_stats.saved_messages += len(messages)
                                cur_stats.not_empty_successful_channels += 1
                                # remember forwarded
                                for message in messages:
                                    if message.forward is not None:
                                        cur_stats.forward_encountered += 1
                                        if isinstance(message.forward.chat, Channel):
                                            if clean_chat_id(message.forward.chat_id) in iteration_channels_ids:
                                                cur_stats.forward_already_in += 1
                                                continue
                                            if message.forward.chat.id is None or message.forward.chat.username is None:
                                                cur_stats.forward_with_empty_id += 1
                                                log(f"Strange forward consider to check: {channel}, {message.id}")
                                                continue

                                            result, type_message = True, "DUPLICATED"
                                            # add_anchor_forwarded(message.forward.chat.id,
                                            #                                         message.forward.chat.username,
                                            #                                         message.forward.chat.title,
                                            #                                         message.forward.channel_post)

                                            if result:
                                                if type_message == "DUPLICATED":
                                                    cur_stats.forward_already_in += 1
                                                else:
                                                    cur_stats.forward_added_in_db += 1
                                                    log(f"Channel {message.forward.chat.username}"
                                                        f" will be extracted soon as forwarded!")
                                            else:
                                                cur_stats.forward_fallen_on_add += 1
                                                log(f"Forwarded channel {message.forward.chat.username} fallen on add!")
                                        else:
                                            log(f"Message {message.id} from {message.chat.username} with type {message.forward} "
                                                f"with text: {message.text} was rejected as not to be from channel")
                                            cur_stats.forward_rejected_not_channel_type += 1
                            else:
                                cur_stats.missed_to_save_messages += len(messages)
                        else:
                            cur_stats.empty_channels += 1

                        if result_of_saving:
                            log(f"!===== Check channel resulted in saving all {len(messages)} messages =====!")

                except Exception as exp:
                    result_of_saving = False
                    log_exception(
                        source=Source.TLG, channel_name=channel, event_name=EventName.EXCEPTION,
                        msg="tlg extractor exception", exp=exp
                    )
                finally:
                    if result_of_saving:
                        cur_stats.successful_channels += 1
                        tell_extractor_is_alive(
                            f"Went to sleep for : {PROPERTIES.sleep_time_channel} seconds\n"
                            f"(after checking {channel} : {ind} out of {cur_stats.all_channels_size}),\n"
                            "\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check more: {cur_stats.subscription_check_more}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check less (SKIPPED): {cur_stats.subscription_check_less}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check init fallen: {cur_stats.subscription_init_has_fallen}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check init succ: {cur_stats.subscription_init_has_succ}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check lazy update fallen: {cur_stats.subscription_lazy_update_has_fallen}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check lazy update succ: {cur_stats.subscription_lazy_update_succ}\n"
                            f"\n"
                            f"{EMOJI.EXTRACTOR} fallen channels: {cur_stats.fallen_channels}\n"
                            f"{EMOJI.EXTRACTOR} successful channels: {cur_stats.successful_channels}\n"
                            f"{EMOJI.EXTRACTOR} empty channels: {cur_stats.empty_channels}\n"
                            f"{EMOJI.EXTRACTOR} not empty channels: {cur_stats.not_empty_channels}\n"
                            f"{EMOJI.EXTRACTOR} not empty successful channels: {cur_stats.not_empty_successful_channels}\n"
                            f"ALL: {cur_stats.all_channels_size}\n\n"
                            f"{EMOJI.SAVE} possible to save messages: {cur_stats.possible_to_save_messages}\n"
                            f"{EMOJI.SAVE} saved messages: {cur_stats.saved_messages}\n"
                            f"{EMOJI.SAVE} missed messages: {cur_stats.missed_to_save_messages}\n"
                            f"{EMOJI.SAVE} skipped messages as another type: {cur_stats.skipped_as_another_type}\n\n"
                            f"{EMOJI.DOWNLOAD_ITER} all client_iter() attempts: {cur_stats.client_iter_count}\n"
                            f"{EMOJI.DOWNLOAD_ITER} success client_iter() attempts: {cur_stats.client_iter_count_success}\n"
                            f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts: {cur_stats.client_iter_count_fallback}\n"
                            f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts success: {cur_stats.client_iter_count_fallback_success}\n"
                            f"\n"
                            f"{EMOJI.TIME} time passed since channels iteration start : {round(time.time() - start)} seconds\n"
                            f"{EMOJI.TIME} previous channels iteration took : {prev_full_cycle} seconds\n"
                            f"\n"
                            f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes to be updated: {cur_stats.attrs_changed}\n"
                            f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes are updated: {cur_stats.attrs_changed_succ}\n"
                            f"\n"
                            f"{EMOJI.FORWARDED} forward encountered: {cur_stats.forward_encountered}\n"
                            f"{EMOJI.FORWARDED} started to extract in current iteration: {cur_stats.forward_started_to_extract}\n"
                            f"{EMOJI.FORWARDED} forward rejected as not channel type: {cur_stats.forward_rejected_not_channel_type}\n"
                            f"{EMOJI.FORWARDED} forward fallen on add to the db: {cur_stats.forward_fallen_on_add}\n"
                            f"{EMOJI.FORWARDED} forward added to the db: {cur_stats.forward_added_in_db}\n"
                            f"{EMOJI.FORWARDED} forward were in the db before: {cur_stats.forward_already_in}\n"
                            f"{EMOJI.FORWARDED} forward with an empty id: {cur_stats.forward_with_empty_id}\n"
                            f"{EMOJI.FORWARDED} stopped encountered: {cur_stats.stopped_encountered}\n"
                        )
                    else:
                        cur_stats.fallen_channels += 1
                        tell_extractor_is_alive(
                            f"Went to sleep for : {PROPERTIES.sleep_time_channel} seconds \n"
                            f"(after checking {channel} : {ind} out of {cur_stats.all_channels_size}),\n"
                            "\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check more: {cur_stats.subscription_check_more}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check less (SKIPPED): {cur_stats.subscription_check_less}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check init fallen: {cur_stats.subscription_init_has_fallen}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check init succ: {cur_stats.subscription_init_has_succ}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check lazy update fallen: {cur_stats.subscription_lazy_update_has_fallen}\n"
                            f"{EMOJI.SUBSCRIBERS} subscription check lazy update succ: {cur_stats.subscription_lazy_update_succ}\n"
                            f"\n"
                            f"{EMOJI.EXTRACTOR} (AFTER BROKEN SAVE), fallen channels: {cur_stats.fallen_channels}\n"
                            f"{EMOJI.EXTRACTOR} successful channels: {cur_stats.successful_channels}\n"
                            f"{EMOJI.EXTRACTOR} empty channels: {cur_stats.empty_channels}\n"
                            f"{EMOJI.EXTRACTOR} not empty channels: {cur_stats.not_empty_channels}\n"
                            f"{EMOJI.EXTRACTOR} not empty successful channels: {cur_stats.not_empty_successful_channels}\n"
                            f"ALL: {cur_stats.all_channels_size}\n\n"
                            f"{EMOJI.SAVE} possible to save messages: {cur_stats.possible_to_save_messages}\n"
                            f"{EMOJI.SAVE} saved messages: {cur_stats.saved_messages}\n"
                            f"{EMOJI.SAVE} missed messages: {cur_stats.missed_to_save_messages}\n"
                            f"{EMOJI.SAVE} skipped messages as another type: {cur_stats.skipped_as_another_type}\n\n"
                            f"{EMOJI.DOWNLOAD_ITER} all client_iter() attempts: {cur_stats.client_iter_count}\n"
                            f"{EMOJI.DOWNLOAD_ITER} success client_iter() attempts: {cur_stats.client_iter_count_success}\n"
                            f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts: {cur_stats.client_iter_count_fallback}\n"
                            f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts success: {cur_stats.client_iter_count_fallback_success}\n"
                            f"\n"
                            f"{EMOJI.TIME} time passed since channels iteration start : {round(time.time() - start)} seconds\n"
                            f"{EMOJI.TIME} previous channels iteration took : {prev_full_cycle} seconds\n"
                            f"\n"
                            f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes to be updated: {cur_stats.attrs_changed}\n"
                            f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes are updated: {cur_stats.attrs_changed_succ}\n"
                            f"\n"
                            f"{EMOJI.FORWARDED} forward encountered: {cur_stats.forward_encountered}\n"
                            f"{EMOJI.FORWARDED} started to extract in current iteration: {cur_stats.forward_started_to_extract}\n"
                            f"{EMOJI.FORWARDED} forward rejected as not channel type: {cur_stats.forward_rejected_not_channel_type}\n"
                            f"{EMOJI.FORWARDED} forward fallen on add to the db: {cur_stats.forward_fallen_on_add}\n"
                            f"{EMOJI.FORWARDED} forward added to the db: {cur_stats.forward_added_in_db}\n"
                            f"{EMOJI.FORWARDED} forward were in the db before: {cur_stats.forward_already_in}\n"
                            f"{EMOJI.FORWARDED} forward with an empty id: {cur_stats.forward_with_empty_id}\n"
                            f"{EMOJI.FORWARDED} stopped encountered: {cur_stats.stopped_encountered}\n"
                        )
                    time.sleep(PROPERTIES.sleep_time_channel)

        prev_full_cycle = round(time.time() - start)
        tell_extractor_is_alive(
            f"(FULL ITERATION IS COMPLETED!)\n"
            f"Went to sleep between channels iterations for : {PROPERTIES.sleep_time_approaches} seconds,\n"
            "\n"
            f"{EMOJI.SUBSCRIBERS} subscription check more: {cur_stats.subscription_check_more}\n"
            f"{EMOJI.SUBSCRIBERS} subscription check less (SKIPPED): {cur_stats.subscription_check_less}\n"
            f"{EMOJI.SUBSCRIBERS} subscription check init fallen: {cur_stats.subscription_init_has_fallen}\n"
            f"{EMOJI.SUBSCRIBERS} subscription check init succ: {cur_stats.subscription_init_has_succ}\n"
            f"{EMOJI.SUBSCRIBERS} subscription check lazy update fallen: {cur_stats.subscription_lazy_update_has_fallen}\n"
            f"{EMOJI.SUBSCRIBERS} subscription check lazy update succ: {cur_stats.subscription_lazy_update_succ}\n"
            f"\n"
            f"{EMOJI.EXTRACTOR} fallen extractors: {cur_stats.fallen_channels}\n"
            f"{EMOJI.EXTRACTOR} successful extractors: {cur_stats.successful_channels}\n"
            f"{EMOJI.EXTRACTOR} empty extractors: {cur_stats.empty_channels}\n"
            f"{EMOJI.EXTRACTOR} not empty extractors: {cur_stats.not_empty_channels}\n"
            f"{EMOJI.EXTRACTOR} not empty successful extractors: {cur_stats.not_empty_successful_channels}\n"
            f"ALL: {cur_stats.all_channels_size}\n\n"
            f"{EMOJI.SAVE} possible to save messages: {cur_stats.possible_to_save_messages}\n"
            f"{EMOJI.SAVE} saved messages: {cur_stats.saved_messages}\n"
            f"{EMOJI.SAVE} missed messages: {cur_stats.missed_to_save_messages}\n"
            f"{EMOJI.SAVE} skipped messages as another type: {cur_stats.skipped_as_another_type}\n\n"
            f"{EMOJI.DOWNLOAD_ITER} all client_iter() attempts: {cur_stats.client_iter_count}\n"
            f"{EMOJI.DOWNLOAD_ITER} success client_iter() attempts: {cur_stats.client_iter_count_success}\n"
            f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts: {cur_stats.client_iter_count_fallback}\n"
            f"{EMOJI.DOWNLOAD_ITER} fallback client_iter() attempts success: {cur_stats.client_iter_count_fallback_success}\n"
            f"\n"
            f"{EMOJI.TIME} time passed since channels iteration start : {prev_full_cycle} seconds\n"
            f"\n"
            f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes to be updated: {cur_stats.attrs_changed}\n"
            f"{EMOJI.CHANGE_ATTRIBUTES} channel attributes are updated: {cur_stats.attrs_changed_succ}\n"
            f"\n"
            f"{EMOJI.FORWARDED} forward encountered: {cur_stats.forward_encountered}\n"
            f"{EMOJI.FORWARDED} started to extract in current iteration: {cur_stats.forward_started_to_extract}\n"
            f"{EMOJI.FORWARDED} forward rejected as not channel type: {cur_stats.forward_rejected_not_channel_type}\n"
            f"{EMOJI.FORWARDED} forward fallen on add to the db: {cur_stats.forward_fallen_on_add}\n"
            f"{EMOJI.FORWARDED} forward added to the db: {cur_stats.forward_added_in_db}\n"
            f"{EMOJI.FORWARDED} forward were in the db before: {cur_stats.forward_already_in}\n"
            f"{EMOJI.FORWARDED} forward with an empty id: {cur_stats.forward_with_empty_id}\n"
            f"{EMOJI.FORWARDED} stopped encountered: {cur_stats.stopped_encountered}\n"
        )
        log(f"Went to sleep, fallen extractors: {cur_stats.fallen_channels}, \n"
            f"subscription check more: {cur_stats.subscription_check_more}\n"
            f"subscription check less (SKIPPED): {cur_stats.subscription_check_less}\n"
            f"subscription check init fallen: {cur_stats.subscription_init_has_fallen}\n"
            f"subscription check init succ: {cur_stats.subscription_init_has_succ}\n"
            f"subscription check lazy update fallen: {cur_stats.subscription_lazy_update_has_fallen}\n"
            f"subscription check lazy update succ: {cur_stats.subscription_lazy_update_succ}\n"
            f"successful extractors: {cur_stats.successful_channels}\n"
            f"empty extractors: {cur_stats.empty_channels}\n"
            f"not empty extractors: {cur_stats.not_empty_channels}\n"
            f"not empty successful extractors: {cur_stats.not_empty_successful_channels}\n"
            f"ALL: {cur_stats.all_channels_size}\n"
            f"possible to save messages: {cur_stats.possible_to_save_messages}\n"
            f"saved messages: {cur_stats.saved_messages}\n"
            f"missed messages: {cur_stats.missed_to_save_messages}\n"
            f"skipped messages as another type: {cur_stats.skipped_as_another_type}\n"
            f"all client_iter() attempts: {cur_stats.client_iter_count}\n"
            f"success client_iter() attempts: {cur_stats.client_iter_count_success}\n"
            f"time taken: {prev_full_cycle} secs\n"
            f"channel attributes to be updated: {cur_stats.attrs_changed}\n"
            f"channel attributes are updated: {cur_stats.attrs_changed_succ}\n"
            f"fallback client_iter() attempts: {cur_stats.client_iter_count_fallback}\n"
            f"fallback client_iter() attempts success: {cur_stats.client_iter_count_fallback_success}\n"
            f"forward encountered: {cur_stats.forward_encountered}\n"
            f"started to extract in current iteration: {cur_stats.forward_started_to_extract}\n"
            f"forward rejected as not channel type: {cur_stats.forward_rejected_not_channel_type}\n"
            f"forward fallen on add to the db: {cur_stats.forward_fallen_on_add}\n"
            f"forward added to the db: {cur_stats.forward_added_in_db}\n"
            f"forward were in the db before: {cur_stats.forward_already_in}\n"
            f"forward with an empty id: {cur_stats.forward_with_empty_id}\n"
            f"stopped encountered: {cur_stats.stopped_encountered}\n"
            )
        time.sleep(PROPERTIES.sleep_time_approaches)


def ask_for_messages_with_fallback(client, channel_name, channel_id, last_message, curr_stat: ExtractorStats,
                                   limit: int = None):
    result = None
    try:
        curr_stat.client_iter_count += 1
        if limit is not None:
            result = list(client.iter_messages(
                entity=int(channel_id), limit=limit, wait_time=PROPERTIES.wait_time_iter_messages
            ))
        else:
            result = list(client.iter_messages(
                entity=int(channel_id), min_id=int(last_message), wait_time=PROPERTIES.wait_time_iter_messages
            ))
        curr_stat.client_iter_count_success += 1
        filtered = [item for item in result if isinstance(item, Message)]
        filtered_another_type = [item for item in result if not isinstance(item, Message)]
        curr_stat.skipped_as_another_type += len(filtered_another_type)
        log(f"messages len: {len(filtered)}\n"
            f"skipped len: {len(filtered_another_type)}\n"
            f"skipped messages: {filtered_another_type}")
        return filtered
    except ValueError as e:
        log(f"Fallback client_iter for {channel_name} {str(e)}")
        curr_stat.client_iter_count_fallback += 1
        if limit is not None:
            result = list(client.iter_messages(
                entity=channel_name, limit=limit, wait_time=PROPERTIES.wait_time_iter_messages))
        else:
            result = list(client.iter_messages(
                entity=channel_name, min_id=int(last_message), wait_time=PROPERTIES.wait_time_iter_messages
            ))
        curr_stat.client_iter_count_fallback_success += 1

        filtered = [item for item in result if isinstance(item, Message)]
        filtered_another_type = [item for item in result if not isinstance(item, Message)]
        curr_stat.skipped_as_another_type += len(filtered_another_type)
        log(f"messages len: {len(filtered)}\n"
            f"skipped len: {len(filtered_another_type)}\n"
            f"skipped messages: {filtered_another_type}")
        return filtered


def update_attrs_of_anchor(messages, channel_id, channel_name, channel_display_text, channel_type, stat):
    sample = messages[0]
    new_channel_type = sample.chat.__class__.__name__
    if sample.chat.username != channel_name or sample.chat.title != channel_display_text \
            or channel_type != new_channel_type:
        stat.attrs_changed += 1

        log(f"Channel with id {channel_id} has changed it's attributes from"
            f" {channel_name}|{channel_display_text}|{channel_type} ->"
            f" {sample.chat.username}|{sample.chat.title}|{new_channel_type}")

        if update_anchor_attributes(channel_id, sample.chat.username, sample.chat.title, new_channel_type):
            stat.attrs_changed_succ += 1
            return sample.chat.username, sample.chat.title, new_channel_type

    return channel_name, channel_display_text, channel_type


if __name__ == '__main__':
    tg_client = PROPERTIES.client_extractor.start()

    log("Start messages aggregation: ")
    aggregate_massages()
