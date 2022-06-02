import itertools
from typing import List, Generator

import vk_api

from APPS.logger import log
from APPS.stat_monitoring import tell_vk_extractor_is_alive
from APPS.tlg.emoji_bot import EMOJI
from PROPERTIES.VK_PROPERTIES import VK_PROPERTIES


def captcha_handler(info: str, captcha):
    """
    При возникновении капчи вызывается эта функция и ей передается объект
    капчи. Через метод get_url можно получить ссылку на изображение.
    Через метод try_again можно попытаться отправить запрос с кодом капчи
    """
    tell_vk_extractor_is_alive(msg=f"{EMOJI.FIRE} Waiting for captcha!")

    log("vk Captcha is needed!")
    key = input(f"{info} Enter captcha code {captcha.get_url()}: ").strip()

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def auth_handler(info: str):
    """
    При двухфакторной аутентификации вызывается эта функция.
    """
    log("Auth vk is needed!")

    # Код двухфакторной аутентификации
    key = input(f"Enter authentication code ({info}): ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


VK_SESSIONS: List[vk_api.VkApi] = []
for phone, password in zip(VK_PROPERTIES.get_phones(), VK_PROPERTIES.get_passwords()):
    vk_session = vk_api.VkApi(
        phone, password,
        # функция для обработки двухфакторной аутентификации
        auth_handler=lambda: auth_handler(f"For phone : {phone}"),
        captcha_handler=lambda *args: captcha_handler(f"For phone : {phone}", *args),
        config_filename=f"sessions/vk_config.v2.{phone}.json"
    )
    vk_session.auth(token_only=True)
    VK_SESSIONS.append(vk_session)


def get_vk_session_gen() -> Generator[vk_api.VkApi, None, None]:
    for session in itertools.cycle(VK_SESSIONS):
        log(f"Session {session.login} acquired")
        yield session


def get_vk_tools_gen() -> Generator[vk_api.VkTools, None, None]:
    for vk_tools in itertools.cycle(vk_api.VkTools(vk_session) for vk_session in VK_SESSIONS):
        log(f"Session {vk_tools.vk.login} acquired")
        yield vk_tools


VK_SESSIONS_GEN = get_vk_session_gen()
VK_TOOLS_GEN = get_vk_tools_gen()


def get_vk_session():
    return next(VK_SESSIONS_GEN)


def get_vk_tools():
    return next(VK_TOOLS_GEN)
