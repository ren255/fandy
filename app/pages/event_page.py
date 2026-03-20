import datetime
import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, Photo, UploadedFile
from app.services.auth import require_login


def render_event_page(event_id: int) -> None:
    user = require_login()

    with get_session() as session:
        event = session.get(Event, event_id)
        if event is None:
            st.error("イベントが見つかりません")
            return

        # 写真一覧取得
        photos = session.exec(select(Photo).where(Photo.event_id == event_id)).all()
        photo_file_ids = [p.file_id for p in photos]

        files = (
            session.exec(
                select(UploadedFile).where(UploadedFile.id.in_(photo_file_ids))
            ).all()
            if photo_file_ids
            else []
        )
        file_map = {f.id: f for f in files}

    # ── ヘッダー ──────────────────────────────
    if st.button("← 戻る", key="event_page_back"):
        st.session_state.pop("viewing_event_id", None)
        st.session_state["current_page"] = "コレクション"
        st.rerun()

    st.markdown(f"## {event.description}")

    col_meta, col_code = st.columns([7, 3])
    with col_meta:
        dt = datetime.datetime.fromtimestamp(event.created_timestamp)
        st.caption(f"作成日時: {dt.strftime('%Y-%m-%d %H:%M')}")
        visibility = "公開" if event.public else "🔒 招待のみ"
        st.caption(visibility)
    with col_code:
        st.markdown("招待コード")
        st.code(event.invite_code, language=None)

    st.divider()

    # ── 写真一覧 ──────────────────────────────
    st.markdown("### 写真")

    if not photos:
        st.info("写真がまだありません。")
    else:
        # 3列グリッド表示
        cols = st.columns(3)
        for i, photo in enumerate(photos):
            uf = file_map.get(photo.file_id)
            if uf is None:
                continue
            with cols[i % 3]:
                try:
                    st.image(
                        uf.file_path, caption=uf.original_name, use_container_width=True
                    )
                except Exception:
                    st.warning(f"読み込み失敗: {uf.original_name}")

    # ── 右下: 写真追加ボタン群 ──────────────────
    st.markdown("---")
    _, col_upload, col_camera = st.columns([6, 2, 2])
    with col_upload:
        if st.button(
            "📷 写真を追加",
            key="go_photo_upload",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["upload_target_event_id"] = event_id
            st.session_state["current_page"] = "写真アップロード"
            st.rerun()
    with col_camera:
        if st.button(
            "📸 カメラで撮影",
            key="go_camera_capture",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["upload_target_event_id"] = event_id
            st.session_state["current_page"] = "カメラ撮影"
            st.rerun()
