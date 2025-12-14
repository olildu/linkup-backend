from typing import Literal, Optional
from pydantic import BaseModel

class ConnectionMatchModel(BaseModel):
    id: int
    username: str
    profile_picture: dict

class ConnectionChatModel(BaseModel):
    id: int
    username: str
    profile_picture: dict
    chat_room_id: int
    unseen_counter : int

    last_message: Optional[str] = None
    last_message_media_type: str | None  