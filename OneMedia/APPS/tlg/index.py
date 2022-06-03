import asyncio
import re
import time
from multiprocessing.connection import Connection
from typing import Union

import asyncpg
from nltk.stem.snowball import SnowballStemmer

from APPS.logger import log
from APPS.tlg.dao_layer import async_retrieve_all_messages_with_channel, setup_pg_connection_pool
from APPS.tlg.utility_collections import punctuation, russian_stop_words, english_stop_words
from PROPERTIES.TLG_BOT_PROPERTIES import PROPERTIES


class InvertedIndex:
    SPLITTER = re.compile(r"\b\S+\b")

    def __init__(self):
        self.index = {}
        self.stemmer = SnowballStemmer("russian")
        self.stemmer_eng = SnowballStemmer("english")

    # (count of occurrences, dict_of_documents)
    def add(self, stemmed_word, message_id, channel):
        if stemmed_word in self.index:
            item = self.index[stemmed_word][0]
            self.index[stemmed_word][1] += 1
            if (message_id, channel) in item:
                item[(message_id, channel)] += 1
            else:
                item[(message_id, channel)] = 1
        else:
            self.index[stemmed_word] = [{(message_id, channel): 1}, 1]

    @staticmethod
    def replace_punctuation(sentence: str):
        res = sentence
        for punc in punctuation:
            res = res.replace(punc, " ")
        return res

    @staticmethod
    def enrich_words_set(word_list, doubled=True):
        doubled_words = set()
        if doubled:
            for i in range(len(word_list)):
                if len(word_list[i]) <= 3:
                    continue
                for j in range(max(0, i - 1), min(len(word_list), i + 2)):
                    if i == j:
                        continue
                    if len(word_list[j]) <= 3:
                        continue
                    doubled_words.add(word_list[j] + word_list[i])
                    doubled_words.add(word_list[i] + word_list[j])
        return word_list + list(doubled_words)

    def process_text(self, sentence: str):
        processed_sentence = InvertedIndex.replace_punctuation(sentence)
        words = re.findall(InvertedIndex.SPLITTER, processed_sentence)
        words_set = self.enrich_words_set(
            [word for word in words if word not in russian_stop_words and word not in english_stop_words])

        words_stemmed = []
        for word in words_set:
            if word.isascii():
                words_stemmed.append(self.stemmer_eng.stem(word))
            else:
                words_stemmed.append(self.stemmer.stem(word))
        return words_stemmed

    # rows = [[sentence, message_id, channel]]
    def create_index(self, rows):
        for row in rows:
            text = row[0]
            message_id = row[1]
            channel = row[2]
            words = self.process_text(text)
            for word in words:
                self.add(
                    stemmed_word=word,
                    message_id=message_id,
                    channel=channel
                )

    def search_phrase(self, query, limit=3):
        query_words = self.process_text(query)
        result = {}
        for word in query_words:
            if word in self.index:
                messages = self.index[word][0]
                count = self.index[word][1]
                for message in messages.keys():
                    if message in result:
                        result[message] += messages[message] / float(count)
                    else:
                        result[message] = messages[message] / float(count)
        result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:limit]
        return result


index: InvertedIndex = None


def get_index(parent_conn: Connection = None) -> Union[None, InvertedIndex]:
    global index
    if parent_conn and parent_conn.poll():
        index = parent_conn.recv()
        log("Found index in pipe!")
    return index


async def update_index_scheduled(pool: asyncpg.pool.Pool = None, child_conn: Connection = None):
    if pool is None:
        pool = await setup_pg_connection_pool()
    while True:
        await run_rebuild_index_task(pool)
        child_conn.send(index)
        await asyncio.sleep(PROPERTIES.sleep_time_approaches)


async def update_index_scheduled_notify(pool: asyncpg.pool.Pool = None, child_conn: Connection = None):
    if pool is None:
        pool = await setup_pg_connection_pool()
    while True:
        await run_rebuild_index_task(pool)
        child_conn.send(index)
        await asyncio.sleep(PROPERTIES.sleep_time_approaches * 4)


async def run_rebuild_index_task(pool: asyncpg.pool.Pool):
    global index
    try:
        log("Start rebuild_index!")

        now = time.time()
        temp = InvertedIndex()
        all_messages = await async_retrieve_all_messages_with_channel(pool)
        temp.create_index(all_messages)
        end = time.time()

        index = temp
        log(f"End rebuild_index (took {int(end - now)} seconds)!")
    except Exception as exp:
        log(f"Exception happened on rebuild {exp}")


class FullSet(set):
    def __contains__(self, item):
        return True

# index = InvertedIndex()
# rows = [
#     ["Григорий пошёл домой на селиваново!", "1", "канал1"],
#     ["Григорий пошёл домой на селиваново!", "1", "канал2"],
#     ["Иванов пошёл домой на селиваново!", "2", "канал2"],
#     ["Дрозды летели низко, но это хорошо!", "4", "канал1"],
# ]
# index.create_index(rows)
#
# print(index.search_phrase("Дрозды пошёл"))
#
# print(index.index)
