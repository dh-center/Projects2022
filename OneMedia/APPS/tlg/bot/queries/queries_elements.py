import inspect

from APPS.tlg.bot.subscription.subscription_repo import UserQuery
from APPS.tlg.emoji_bot import EMOJI

BUTTON_MY_QUERIES = "Мои запросы"
BUTTON_ADD_QUERY = "Добавить запрос"

BUTTON_VIEW_EDIT_QUERY = f"View/Edit {EMOJI.PENCIL}"
BUTTON_REMOVE_QUERY = f"Remove {EMOJI.BASKET}"

ACTION_VIEW_EDIT_QUERY = "Просмотреть изменить запрос"
ACTION_REMOVE_QUERY = "Удалить запрос"

BUTTON_CHANGE_QUERY_NAME = f"Name"
BUTTON_CHANGE_QUERY_NAME_ACTION = f"Name_ACTION"
BUTTON_CHANGE_QUERY_SOURCES_VK = f"VK"
BUTTON_CHANGE_QUERY_SOURCES_TLG = f"TLG"
BUTTON_CHANGE_QUERY_SOURCES_WEB = f"WEB"
BUTTON_CHANGE_QUERY_MUST_TERMS = f"Must"
BUTTON_CHANGE_QUERY_MUST_TERMS_ACTION = f"Must_ACTION"
BUTTON_CHANGE_QUERY_SHOULD_TERMS = f"Should"
BUTTON_CHANGE_QUERY_SHOULD_TERMS_ACTION = f"Should_ACTION"
BUTTON_CHANGE_QUERY_EXCLUDED_TERMS = f"Excluded"
BUTTON_CHANGE_QUERY_EXCLUDED_TERMS_ACTION = f"Excluded_ACTION"
BUTTON_CHANGE_QUERY_CHANNELS_INCLUDED = f"Channels Included"
BUTTON_CHANGE_QUERY_CHANNELS_EXCLUDED = f"Channels Excluded"
BUTTON_CHANGE_QUERY_CHANNELS_ACTION = f"Channels_ACTION"
BUTTON_CHANGE_QUERY_ENABLE_GLOBAL = f"{EMOJI.LAMP}Enable Global"
BUTTON_CHANGE_QUERY_DISABLE_GLOBAL = f"{EMOJI.GRAY_CROSS}Disable Global"

HELP_TERMS_QUERY = f"""
Через запятую (регистр не имеет значения), каждый терм в двойных кавычках, синонимы в квадратных скобках:
`["рф", "россия", "russia"], "население", "2022"`
"""


def get_query_already_exist_description(query_name: str) -> str:
    res = f"""{EMOJI.EXCLAMATIONS} Запрос с таким именем : **{query_name}** уже существует, выберите другое имя."""
    return inspect.cleandoc(res)


def get_query_created_description(uid: int) -> str:
    res = f"""
    Запрос (**uid: {uid}**) создан {EMOJI.SUPPORTIVE_SMILE}
    Начните изменять его чтобы установить все необходимые параметры.{EMOJI.POINT_DOWN}
    """
    return inspect.cleandoc(res)


def get_query_list_query_description(query: UserQuery) -> str:
    res = f"""
    {query.name} (**uid:** {query.uid})
    """
    return inspect.cleandoc(res)


def get_query_vew_edit_description(user_query: UserQuery) -> str:
    query = user_query.query
    res = f"""
    **Запрос**{EMOJI.SEARCH} (**uid** : {user_query.uid}) (created time : {user_query.created_time:%Y-%m-%d %H:%M})
    **Name** : {user_query.name}    
    
    {EMOJI.POINT_RIGHT}**Terms**
      * **Must terms** : {query.must_terms}
      * **Should terms** : {query.should_terms}
      * **Excluded terms** : {query.excluded_terms}
      
    {EMOJI.POINT_RIGHT}**Sources** : 
    {[*query.get_sources()]}
    
    {EMOJI.POINT_RIGHT}**Included Channels** : 
    {query.get_channels_included_description()}
    
    {EMOJI.POINT_RIGHT}**Excluded Channels** : 
    {query.get_channels_excluded_description()}
    """
    return inspect.cleandoc(res)


def source_with_enabled_indicator(user_query: UserQuery, source: str) -> str:
    if source in user_query.query.get_sources():
        return f"{source} {EMOJI.LAMP}"
    return f"{source} {EMOJI.GRAY_CROSS}"
