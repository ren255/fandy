from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """ユーザー"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=140)
    password: str


import random
import string


def _gen_invite_code() -> str:
    return "".join(random.choices(string.ascii_uppercase, k=4))


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: int = Field(foreign_key="user.id")
    created_timestamp: int
    description: str
    invite_code: str = Field(default_factory=_gen_invite_code, max_length=4)
    public: bool = Field(default=True)


class UploadedFile(SQLModel, table=True):
    """files/ に保存したファイルのメタデータ"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_timestamp: int
    created_by: int = Field(foreign_key="user.id")
    original_name: str
    mime_type: str
    file_path: str


class Photo(SQLModel, table=True):
    """イベントに紐づく写真"""

    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="uploadedfile.id")
    event_id: int = Field(foreign_key="event.id")


class JoinedEvent(SQLModel, table=True):
    """ユーザーが参加するイベント。"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
