import inspect

from APPS.tlg.emoji_bot import EMOJI

BUTTON_SUPPORT = "Support"


def get_about_description() -> str:
    res = """
    **OneMedia** - это открытая исследовательская платформа для анализа новостной картины на территории России и в мире.
    
    (News Search Bot Alpha Version, by DH Center ITMO)
    По вопросам сотрудничества @kinmanz
    """

    return inspect.cleandoc(res)


def get_support_accepted_description(uid: int) -> str:
    res = f"""
    Ваш запрос (**uid: {uid}**) принят к рассмотрению {EMOJI.SUPPORTIVE_SMILE}
    Мы сообщим вам как только начнём над ним работать.
    """
    return inspect.cleandoc(res)
