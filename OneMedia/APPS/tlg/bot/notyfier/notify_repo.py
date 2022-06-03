import asyncio
from typing import List

import asyncpg

from APPS.entyties import CommonMessage, VK, WEB, TLG
from APPS.overall_utils import auto_str
from APPS.tlg.dao_layer import setup_pg_connection_pool


@auto_str
class NotifyAnchor:
    def __init__(self, source_type: str, last_uid: int):
        self.source_type = source_type
        self.last_uid = last_uid

    async def save(self):
        return await save_notify_anchor(self)


async def get_vk_messages(from_uid: int):
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """
            select vm.message_id,
                   vm.owner_id,
                   vm.from_id,
                   vm.message_content,
                   vm.publish_date,
                   vm.meta_image,
                   vm.uid,
                   vm.created_time,
                   vma.channel_name,
                   vma.channel_id,
                   vma.screen_name,
                   vma.participants
            from vk_message vm
                     join vk_message_anchors vma on -vma.channel_id = vm.owner_id
            where vm.uid > $1
            order by uid
            """, from_uid
        )
    if found:
        return [
            CommonMessage(
                source=VK, uid=record['uid'], channel_name=record['screen_name'], content=record["message_content"],
                meta_image=record["meta_image"],
                created_time=record["created_time"].strftime('%Y-%m-%d %H:%M:%S'),
                link=fr"https://vk.com/{record['screen_name']}?w=wall{record['owner_id']}_{record['message_id']}"
            ) for record in found
        ]


async def get_web_messages(from_uid: int):
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """
            select m.message_id,
                   m.link,
                   m.channel_name,
                   m.sender_name,
                   m.publish_date,
                   m.title,
                   m.content,
                   m.meta_image,
                   m.uid,
                   m.created_time
            from web_message m
            where m.uid > $1
            order by uid
            """, from_uid
        )
    if found:
        return [
            CommonMessage(
                source=WEB, uid=record['uid'], channel_name=record['channel_name'], content=record["content"],
                meta_image=record["meta_image"],
                created_time=record["created_time"].strftime('%Y-%m-%d %H:%M:%S'),
                title=record["title"], link=record["link"]
            ) for record in found
        ]


async def get_tlg_messages(from_uid: int):
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch(
            """
            select m.message_id,
                   m.channel_id,
                   m.channel_name,
                   m.channel_title,
                   m.sender_username,
                   m.sender_id,
                   m.publish_date,
                   m.content,
                   m.source_id,
                   m.forward_channel_id,
                   m.forward_message_id,
                   m.meta_image,
                   m.uid,
                   m.created_time,
                   oa.subscribers,
                   oa.channel_type,
                   oa.channel_display_name
            from message m
                     join ono_anchors oa on m.channel_id = oa.channel_id
            where m.uid > $1
            order by uid
            """, from_uid
        )
    if found:
        return [
            CommonMessage(
                source=TLG, uid=record['uid'], channel_name=record['channel_name'], content=record["content"],
                meta_image=record["meta_image"],
                created_time=record["created_time"].strftime('%Y-%m-%d %H:%M:%S'),
                link=fr"https://t.me/{record['channel_name']}/{record['message_id']}",
                # link=fr"https://t.me/c/{record['channel_id']}/{record['message_id']}",
                # link=fr"http://onemedia.dh-center.ru/rest/redirect?redirectUrl=https://t.me/{record['channel_name']}/{record['message_id']}",
            ) for record in found
        ]


async def get_notify_anchors() -> List[NotifyAnchor]:
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        found = await connection.fetch("select * from notify_anchors")
    if found:
        return [NotifyAnchor(**record) for record in found]


async def save_notify_anchor(anchor: NotifyAnchor):
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            """
            update notify_anchors
            set last_uid = $2
            where source_type = $1
            """, anchor.source_type, anchor.last_uid
        )


async def update_anchors_on_restart():
    """
    To avoid flood to clients
    """
    pool: asyncpg.pool.Pool = await setup_pg_connection_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            """
            update notify_anchors
            set last_uid = (select GREATEST(0, max(uid) - 100, 
                (select last_uid from notify_anchors where source_type = 'TLG')) from message)
            where source_type = 'TLG';
            """
        )
        await connection.execute(
            """
            update notify_anchors
            set last_uid = (select GREATEST(0, max(uid) - 100, 
                (select last_uid from notify_anchors where source_type = 'VK')) from vk_message)
            where source_type = 'VK';
            """
        )
        await connection.execute(
            """
            update notify_anchors
            set last_uid = (select GREATEST(0, max(uid) - 100, 
                (select last_uid from notify_anchors where source_type = 'WEB')) from web_message)
            where source_type = 'WEB';
            """
        )


async def main():
    async def gen_test(a):
        if a > 5:
            for el in [1, 2, 3]:
                yield el

    print([i async for i in gen_test(11)])


if __name__ == '__main__':
    asyncio.run(main())
