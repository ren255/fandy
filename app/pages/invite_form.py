import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, JoinedEvent
from app.services.auth import require_login


def render_invite_form() -> None:
    st.markdown("## 招待コードで参加")

    user = require_login()

    code = (
        st.text_input(
            "招待コード（4文字）",
            max_chars=4,
            placeholder="ABCD",
        )
        .strip()
        .upper()
    )

    col_submit, col_cancel = st.columns([2, 1])

    with col_submit:
        if st.button(
            "参加する",
            key="invite_form_submit",
            use_container_width=True,
            type="primary",
        ):
            if len(code) != 4:
                st.error("4文字の招待コードを入力してください")
                return

            with get_session() as session:
                event = session.exec(
                    select(Event).where(Event.invite_code == code)
                ).first()

                if event is None:
                    st.error("招待コードが見つかりません")
                    return

                already = session.exec(
                    select(JoinedEvent).where(
                        JoinedEvent.user_id == user.id,
                        JoinedEvent.event_id == event.id,
                    )
                ).first()
                if already:
                    st.warning("すでに参加しています")
                    return

                session.add(JoinedEvent(user_id=user.id, event_id=event.id))
                session.commit()

            st.success(f"「{event.description}」に参加しました！")
            st.session_state["current_page"] = "コレクション"
            st.rerun()

    with col_cancel:
        if st.button("キャンセル", key="invite_form_cancel", use_container_width=True):
            st.session_state["current_page"] = "イベント"
            st.rerun()
