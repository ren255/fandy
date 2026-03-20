import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import JoinedEvent
from app.services.auth import require_login
from app.pages.eventlist import render_event_list


def render_collection() -> None:
    st.markdown("## コレクション")

    user = require_login()

    with get_session() as session:
        joined = session.exec(
            select(JoinedEvent).where(JoinedEvent.user_id == user.id)
        ).all()

    event_ids = [j.event_id for j in joined]
    render_event_list(event_ids, joinable=False)
