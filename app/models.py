from typing import Optional
from sqlmodel import SQLModel, Field


class UploadedFile(SQLModel, table=True):
    """files/ に保存したファイルのメタデータ。"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_timestamp: int
    username: str = Field(max_length=140)
    original_name: str
    file_path: str
    mime_type: str


class Note(SQLModel, table=True):
    """140文字のMarkdownノート。file_idで添付ファイルを1つ持てる。"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_timestamp: int
    updated_timestamp: int
    username: str = Field(max_length=140)
    body: str = Field(max_length=140)
    file_id: Optional[int] = Field(default=None, foreign_key="uploadedfile.id")
