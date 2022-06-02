import inspect

from APPS.tlg.emoji_bot import EMOJI

ACTION_SEARCH_BY_QUERIES = "ACTION_SEARCH_BY_QUERIES"
ACTION_CHOOSE_QUERY_SEARCH = "ACTION_CHOOSE_QUERY_SEARCH"


def get_search_description() -> str:
    about_search = "**Демо версия поиска по всей базе новостей.**\n" \
                   "(очень ограниченная сложность запроса, размер выдачи только 20 результатов)" \
                   "\n\nПолная функциональность поиска доступна по API, пожалуйста свяжитесь с нами " \
                   "для получения доступа к API поиска."

    res = about_search + f"\n\n{EMOJI.POINT_RIGHT} Поиск по обязательным термам в тексте:" \
                         f"\n/gsearch_all_of <набор слов через запятую, любое выражение> " \
                         f"и я поищу новости этому отвечающие глобально среди всех мной отслеживаемых." \
                         f"\n\n{EMOJI.POINT_RIGHT} Поиск по набору термов:" \
                         f"\n/gsearch_any_of <набор слов через запятую, любое выражение> " \
                         f"и я поищу новости этому отвечающие глобально среди всех мной отслеживаемых." \
                         f"\n\n{EMOJI.POINT_RIGHT} Поиск по произвольной строке (lucene синтаксис):" \
                         f"\n/gsearch_simple_of <любая фраза> " \
                         f"и я поищу новости этому отвечающие глобально среди всех мной отслеживаемых."

    res += f"\n\n{EMOJI.LAMP} Для получения общей информации по запросу " \
           f"попробуйте воспользоваться функциональностью **Отчёты** в главном меню."

    return inspect.cleandoc(res)
