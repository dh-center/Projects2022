from typing import Union

from APPS.overall_utils import auto_str

WEB = 'WEB'
VK = 'VK'
TLG = 'TLG'

ALL_SOURCES = [TLG, VK, WEB]

@auto_str
class CommonMessage:
    def __init__(
            self,
            source: str,
            uid: int,
            channel_name: str,
            content: str,
            link: str = None,
            channel_id: Union[str, None] = None,
            channel_title=None,
            sender_username=None,
            sender_id=None,
            title: Union[str, None] = None,
            meta_image: Union[str, None] = None,
            created_time: int = None,
            channel_display_name=None,
            participants: Union[int, None] = None,
            publish_date: Union[int, None] = None,
    ):
        self.source = source
        self.channel_id: Union[str, None] = channel_id
        self.channel_name: str = channel_name
        self.channel_title = channel_title
        self.sender_username = sender_username
        self.sender_id = sender_id
        self.publish_date: Union[int, None] = publish_date
        self.content: str = content
        self.link: str = link
        self.title: Union[str, None] = title
        self.meta_image: Union[str, None] = meta_image
        self.uid: int = uid
        self.created_time: int = created_time
        self.participants: Union[int, None] = participants
        self.channel_display_name = channel_display_name
