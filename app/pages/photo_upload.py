import time
import uuid
from pathlib import Path
import streamlit as st
from app.database import get_session
from app.models import UploadedFile, Photo
from app.services.auth import require_login

UPLOAD_DIR = Path("files")


def render_photo_upload() -> None:
    user = require_login()

    event_id = st.session_state.get("upload_target_event_id")
    if event_id is None:
        st.error("アップロード対象のイベントが不明です")
        return

    st.markdown("## 写真をアップロード")

    uploaded = st.file_uploader(
        "画像を選択",
        type=["jpg", "jpeg", "png", "gif", "webp"],
        accept_multiple_files=True,
    )

    col_submit, col_cancel = st.columns([2, 1])

    with col_submit:
        if st.button(
            "アップロード",
            key="photo_upload_submit",
            type="primary",
            use_container_width=True,
            disabled=not uploaded,
        ):
            UPLOAD_DIR.mkdir(exist_ok=True)
            now = int(time.time())

            with get_session() as session:
                for f in uploaded:
                    ext = Path(f.name).suffix
                    unique_name = f"{uuid.uuid4().hex}{ext}"
                    file_path = UPLOAD_DIR / unique_name
                    file_path.write_bytes(f.read())

                    uf = UploadedFile(
                        created_timestamp=now,
                        created_by=user.id,
                        original_name=f.name,
                        mime_type=f.type,
                        file_path=str(file_path),
                    )
                    session.add(uf)
                    session.flush()  # uf.id を確定

                    session.add(Photo(file_id=uf.id, event_id=event_id))

                session.commit()

            st.success(f"{len(uploaded)} 枚アップロードしました！")
            st.session_state["viewing_event_id"] = event_id
            st.session_state["current_page"] = "イベント詳細"
            st.rerun()

    with col_cancel:
        if st.button("キャンセル", key="photo_upload_cancel", use_container_width=True):
            st.session_state["viewing_event_id"] = event_id
            st.session_state["current_page"] = "イベント詳細"
            st.rerun()
