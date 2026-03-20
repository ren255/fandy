import time
import uuid
from pathlib import Path
import streamlit as st
from app.database import get_session
from app.models import UploadedFile, Photo
from app.services.auth import require_login

UPLOAD_DIR = Path("files")


def render_camera_capture() -> None:
    user = require_login()

    event_id = st.session_state.get("upload_target_event_id")
    if event_id is None:
        st.error("アップロード対象のイベントが不明です")
        return

    st.markdown("## カメラで撮影")

    img_file = st.camera_input("カメラを起動して撮影してください")

    col_submit, col_cancel = st.columns([2, 1])

    with col_submit:
        if st.button(
            "保存",
            key="camera_capture_submit",
            type="primary",
            use_container_width=True,
            disabled=img_file is None,
        ):
            UPLOAD_DIR.mkdir(exist_ok=True)
            now = int(time.time())

            unique_name = f"{uuid.uuid4().hex}.jpg"
            file_path = UPLOAD_DIR / unique_name
            file_path.write_bytes(img_file.getvalue())

            with get_session() as session:
                uf = UploadedFile(
                    created_timestamp=now,
                    created_by=user.id,
                    original_name=img_file.name,
                    mime_type="image/jpeg",
                    file_path=str(file_path),
                )
                session.add(uf)
                session.flush()  # uf.id を確定

                session.add(Photo(file_id=uf.id, event_id=event_id))
                session.commit()

            st.success("写真を保存しました！")
            st.session_state["viewing_event_id"] = event_id
            st.session_state["current_page"] = "イベント詳細"
            st.rerun()

    with col_cancel:
        if st.button(
            "キャンセル", key="camera_capture_cancel", use_container_width=True
        ):
            st.session_state["viewing_event_id"] = event_id
            st.session_state["current_page"] = "イベント詳細"
            st.rerun()
