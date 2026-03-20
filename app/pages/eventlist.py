import datetime
import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, JoinedEvent
from app.services.auth import require_login


def render_event_list(event_ids: list[int], joinable: bool = False) -> None:
    """
    event_ids: 表示するEventのIDリスト
    joinable:  Trueなら「参加する」ボタンを表示（イベントページ用）
               Falseならコンテナクリックで詳細へ（コレクションページ用）
    """
    if not event_ids:
        st.info("表示するイベントがありません。")
        return

    with get_session() as session:
        events = session.exec(select(Event).where(Event.id.in_(event_ids))).all()

    for event in events:
        with st.container(border=True):
            col_info, col_action = st.columns([8, 2])

            with col_info:
                st.markdown(f"**{event.description}**")
                dt = datetime.datetime.fromtimestamp(event.created_timestamp)
                st.caption(
                    f"{dt.strftime('%Y-%m-%d %H:%M')}　"
                    f"{'公開' if event.public else '🔒 招待のみ'}"
                )

            with col_action:
                if joinable:
                    if st.button(
                        "参加する", key=f"join_{event.id}", use_container_width=True
                    ):
                        _join_event(event.id)
                else:
                    if st.button(
                        "開く", key=f"open_{event.id}", use_container_width=True
                    ):
                        st.session_state["viewing_event_id"] = event.id
                        st.session_state["current_page"] = "イベント詳細"
                        st.rerun()


def _join_event(event_id: int) -> None:
    user = require_login()
    with get_session() as session:
        already = session.exec(
            select(JoinedEvent).where(
                JoinedEvent.user_id == user.id,
                JoinedEvent.event_id == event_id,
            )
        ).first()
        if already:
            st.warning("すでに参加しています")
            return
        session.add(JoinedEvent(user_id=user.id, event_id=event_id))
        session.commit()
    st.success("参加しました！")
    st.rerun()
