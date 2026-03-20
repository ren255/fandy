import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, JoinedEvent
from app.services.auth import require_login
from app.pages.eventlist import render_event_list


def render_collection() -> None:
    st.markdown("## コレクション")

    user = require_login()

    with get_session() as session:
        joined = session.exec(
            select(JoinedEvent).where(JoinedEvent.user_id == user.id)
        ).all()
        joined_ids = [j.event_id for j in joined]

        events = (
            session.exec(select(Event).where(Event.id.in_(joined_ids))).all()
            if joined_ids
            else []
        )

    if not events:
        st.info("参加しているイベントがありません。")
        return

    for event in events:
        with st.container(border=True):
            col_info, col_code = st.columns([7, 3])
            with col_info:
                import datetime

                dt = datetime.datetime.fromtimestamp(event.created_timestamp)
                st.markdown(f"**{event.description}**")
                st.caption(f"作成日時: {dt.strftime('%Y-%m-%d %H:%M')}")
            with col_code:
                st.markdown("招待コード")
                st.code(event.invite_code, language=None)
                visibility = "公開" if event.public else "🔒 招待のみ"
                st.caption(visibility)
