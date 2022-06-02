import csv
import io
from datetime import datetime
from typing import Any, Iterable, List, Union, Dict, Tuple

from aiohttp import ClientSession

from APPS.logger import log_exp
from APPS.search_utils import SEARCH_INDEX_URL
from APPS.tlg.bot.subscription.subscription_repo import UserQuery
from APPS.tlg.jwt_provider import JWT_HEADER_NAME, get_jwt


def to_list_of_terms(term):
    if isinstance(term, list):
        return term
    return [term]


async def search_for_report(
        user_query: UserQuery,
        from_time: datetime,
        now: datetime,
        number_of_best_hits: int = 100000
) -> Union[List[Dict[str, Any]], None]:
    async with ClientSession() as session:
        try:
            query = {
                "number_of_best_hits": number_of_best_hits,
                "createdTimeRange": {
                    "from": int(from_time.timestamp() * 1000),
                    "to": int(now.timestamp() * 1000)
                }
            }
            search_query = user_query.query
            if search_query.must_terms:
                query['contentDocTermsMust'] = [{"synonyms": to_list_of_terms(term)} for term in
                                                search_query.must_terms]
            if search_query.should_terms:
                query['contentDocTermsShould'] = [{"synonyms": to_list_of_terms(term)} for term in
                                                  search_query.should_terms]
            if search_query.excluded_terms:
                query['contentDocTermsExcluded'] = [{"synonyms": to_list_of_terms(term)} for term in
                                                    search_query.excluded_terms]

            if search_query.channels_included:
                query['channelNamesIncluded'] = [{"source": source, "channelName": channel_name} for
                                                 source, channel_name in search_query.channels_included]

            if search_query.channels_excluded:
                query['contentDocTermsExcluded'] = [{"source": source, "channelName": channel_name} for
                                                    source, channel_name in search_query.channels_excluded]

            if search_query.sources:
                query['sources'] = list(search_query.sources)

            response = await session.post(
                url=f"{SEARCH_INDEX_URL}/search",
                headers={JWT_HEADER_NAME: get_jwt("bot")},
                json=query
            )
            response.raise_for_status()
            json_dict = await response.json()
        except Exception as exp:
            log_exp("Search.get_alive_stat()", exp)
            return None
    return json_dict


def enrich_report(report: List[Dict]):
    for row in report:
        row["created_time_readable"] = f"{datetime.utcfromtimestamp(row['created_time'] / 1000):%Y-%m-%d %H:%M}"
        row["publish_date_readable"] = f"{datetime.utcfromtimestamp(row['publish_date'] / 1000):%Y-%m-%d %H:%M}"


async def generate_report_from_time(
        name_prefix: str,
        from_time: datetime,
        now: datetime,
        user_query: UserQuery
) -> Tuple[int, io.BytesIO]:
    report = await search_for_report(
        user_query=user_query, from_time=from_time, now=now
    )
    if not report:
        return None, None

    enrich_report(report)
    header = list(report[0].keys())
    return len(report), generate_report_file_from_data(
        name_prefix=name_prefix,
        header=header,
        data=([row.get(key, None) for key in header] for row in sorted(report, key=lambda row: row['created_time']))
    )


def generate_report_file_from_dict_data(
        name_prefix: str,
        header: List[Any],
        data: List[Dict[Any, Any]]
) -> io.BytesIO:
    file = io.StringIO()
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(data)
    bytes_file = io.BytesIO(file.getvalue().encode('utf-8'))
    bytes_file.name = f'report_{name_prefix}.csv'

    return bytes_file


def generate_report_file_from_data(
        name_prefix: str,
        header: Iterable[Any],
        data: Iterable[Iterable[Any]]
) -> io.BytesIO:
    file = io.StringIO()
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data)
    bytes_file = io.BytesIO(file.getvalue().encode('utf-8'))
    bytes_file.name = f'report_{name_prefix}.csv'

    # bytes_file = io.BytesIO()
    # bytes_file.name = f'report_{name_prefix}_{datetime.now().strftime("%Y-%m-%d")}.csv'
    # # https://stackoverflow.com/questions/55889474/convert-io-stringio-to-io-bytesio
    # wrapper_string_file = codecs.getwriter("UTF-8")(bytes_file)
    #
    # writer = csv.writer(wrapper_string_file)
    # writer.writerow(header)
    # writer.writerows(data)
    # bytes_file.flush()

    return bytes_file


if __name__ == '__main__':
    print(generate_report_file_from_data(
        name_prefix="test",
        header=["id1", "id2", "id3"],
        data=[
            ["val1", "val2", "val3"],
            ["val1", "val2", "val3"],
            ["val1", "val2", "val3"],
        ]
    ).getvalue().decode())
