import time
import uuid
from pathlib import Path
from sqlmodel import select
from app.models import UploadedFile

FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)


def save_uploaded_file(session, file, user_id: int) -> UploadedFile:
    """
    file: st.file_uploader が返す UploadedFile オブジェクト
    ディスク保存 → DBレコード作成 → UploadedFile を返す
    """
    suffix = Path(file.name).suffix
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = FILES_DIR / unique_name

    file_path.write_bytes(file.getvalue())

    record = UploadedFile(
        created_timestamp=int(time.time()),
        created_by=user_id,
        original_name=file.name,
        mime_type=file.type or "application/octet-stream",
        file_path=str(file_path),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_file_path(file_id: int, session) -> Path | None:
    record = session.get(UploadedFile, file_id)
    if record is None:
        return None
    return Path(record.file_path)
