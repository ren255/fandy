import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, JoinedEvent
from app.services.auth import require_login
from app.pages.eventlist import render_event_list


def render_event() -> None:
    st.markdown("## イベント")

    user = require_login()

    with get_session() as session:
        # 参加済みevent_idを取得
        joined = session.exec(
            select(JoinedEvent).where(JoinedEvent.user_id == user.id)
        ).all()
        joined_ids = {j.event_id for j in joined}

        # 全イベントから参加済みを除外
        all_events = session.exec(select(Event)).all()
        event_ids = [e.id for e in all_events if e.id not in joined_ids]

    render_event_list(event_ids, joinable=True)
