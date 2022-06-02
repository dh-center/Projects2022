import uuid

from cachetools import TTLCache
from telethon import events

_CACHE = TTLCache(ttl=24 * 60 * 60, maxsize=10 ** 7)
_DISPATCHERS = {}

ACTION_NAME = 'action_name'


class ActionStorage:

    @staticmethod
    async def dispatch_handler(event: events.CallbackQuery.Event):
        data = _CACHE.get(int.from_bytes(bytes=event.data, byteorder='big'), None)
        if not data:
            return None
        dispatcher = _DISPATCHERS.get(data[ACTION_NAME], None)
        if dispatcher:
            return await dispatcher(event, data['data'])
        return None

    @staticmethod
    async def dispatch_handler_for_user(event: events.NewMessage.Event):
        user_id = event.chat_id
        data = _CACHE.get(user_id, None)
        if not data:
            return None
        _CACHE.pop(user_id)
        dispatcher = _DISPATCHERS.get(data[ACTION_NAME], None)
        if dispatcher:
            return await dispatcher(event, data['data'])
        return None

    @staticmethod
    def put_data(action_name: str, data) -> bytes:
        data = {'data': data, ACTION_NAME: action_name}
        key = generate_64_uuid()
        _CACHE[key] = data
        return key.to_bytes(64, byteorder='big')

    @staticmethod
    def put_data_for_user(action_name: str, user_id: int, data):
        data = {'data': data, ACTION_NAME: action_name}
        _CACHE[user_id] = data

    @staticmethod
    def get_data(key: bytes):
        return _CACHE.get(key, None)


def action_dispatcher(action_name: str):
    def wrapper(func):
        _DISPATCHERS[action_name] = func
        return func

    return wrapper


def last_message_dispatcher(action_name: str):
    def wrapper(func):
        _DISPATCHERS[action_name] = func
        return func

    return wrapper


def generate_64_uuid() -> int:
    return uuid.uuid1().int >> 64


if __name__ == '__main__':
    a = (uuid.uuid1().int >> 64)
    to_bytes = a.to_bytes(64, byteorder='big')
    from_bytes = int.from_bytes(bytes=to_bytes, byteorder='big')
    print(from_bytes)
