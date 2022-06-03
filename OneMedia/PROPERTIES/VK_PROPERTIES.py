import os
from typing import List

SECONDS_A_DAY = 24 * 60 * 60


class VK_PROPERTIES:
    phones = os.getenv('vk_phones', 'phone')
    passwords = os.getenv('vk_passwords', 'pass')
    sleep_time_approaches = 15 * 60

    __phones = None

    @staticmethod
    def get_phones() -> List[str]:
        if not VK_PROPERTIES.__phones:
            VK_PROPERTIES.__phones = [phone.strip() for phone in VK_PROPERTIES.phones.split(',')]
        return VK_PROPERTIES.__phones

    __passwords = None

    @staticmethod
    def get_passwords() -> List[str]:
        if not VK_PROPERTIES.__passwords:
            VK_PROPERTIES.__passwords = [password.strip() for password in VK_PROPERTIES.passwords.split(',')]
        return VK_PROPERTIES.__passwords

    @staticmethod
    def get_sleep_time_channel() -> int:
        # https://vk.com/dev/data_limits
        # limit 5000 a day
        acc_limit = 5000
        acc_count = min(len(VK_PROPERTIES.get_phones()), len(VK_PROPERTIES.get_passwords()))
        quota = acc_limit * acc_count
        # just in case we need it
        safety_pillow = 2
        return (SECONDS_A_DAY // quota) + safety_pillow
