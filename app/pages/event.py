import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, JoinedEvent
from app.services.auth import require_login
from app.pages.eventlist import render_event_list


def render_event() -> None:
    st.markdown("## イベント")

    user = require_login()

    col_create, col_invite = st.columns(2)
    with col_create:
        if st.button(
            "＋ 新規イベント作成",
            key="go_event_form",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "イベント作成"
            st.rerun()
    with col_invite:
        if st.button(
            "🔑 招待コードで参加", key="go_invite_form", use_container_width=True
        ):
            st.session_state["current_page"] = "招待コード参加"
            st.rerun()

    st.divider()

    with get_session() as session:
        joined = session.exec(
            select(JoinedEvent).where(JoinedEvent.user_id == user.id)
        ).all()
        joined_ids = {j.event_id for j in joined}

        # publicなイベントのみ一覧表示（非公開は招待コード経由のみ）
        all_events = session.exec(
            select(Event).where(Event.public == True)  # noqa: E712
        ).all()
        event_ids = [e.id for e in all_events if e.id not in joined_ids]

    render_event_list(event_ids, joinable=True)
