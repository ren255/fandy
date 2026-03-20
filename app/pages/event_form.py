import time
import streamlit as st
from app.database import get_session
from app.models import Event
from app.services.auth import require_login


def render_event_form() -> None:
    st.markdown("## 新規イベント作成")

    user = require_login()

    description = st.text_area(
        "イベント説明", placeholder="イベントの内容を入力してください", height=120
    )
    public = st.checkbox(
        "公開イベント（招待コードなしで参加可能）",
        value=True,
        help="オフにすると招待コードを持つ人だけが参加できます",
    )

    col_submit, col_cancel = st.columns([2, 1])

    with col_submit:
        if st.button(
            "作成する",
            key="event_form_submit",
            use_container_width=True,
            type="primary",
        ):
            if not description.strip():
                st.error("イベント説明を入力してください")
                return
            now = int(time.time())
            with get_session() as session:
                event = Event(
                    created_by=user.id,
                    created_timestamp=now,
                    description=description.strip(),
                    public=public,
                )
                session.add(event)
                session.commit()
                session.refresh(event)
                invite_code = event.invite_code

            st.success(f"イベントを作成しました！　招待コード: **{invite_code}**")
            st.session_state["current_page"] = "イベント"
            st.rerun()

    with col_cancel:
        if st.button("キャンセル", key="event_form_cancel", use_container_width=True):
            st.session_state["current_page"] = "イベント"
            st.rerun()
