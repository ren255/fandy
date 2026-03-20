"""
main.py の先頭付近（render_header() より前）で呼ぶ。

    from app.pages.invite_redirect import handle_invite_redirect
    handle_invite_redirect()

/invite/ABCD 形式のURLでアクセスされたとき、
?invite=ABCD のクエリパラメータを読み取って自動参加処理を行う。

Streamlit では path routing がないため、
    https://yourapp/?invite=ABCD
の形式で運用する。
"""

import streamlit as st
from sqlmodel import select
from app.database import get_session
from app.models import Event, JoinedEvent
from app.services.auth import is_logged_in, get_current_user


def handle_invite_redirect() -> None:
    """クエリパラメータ ?invite=XXXX を処理する。"""
    params = st.query_params
    code = params.get("invite", "").strip().upper()
    if not code:
        return

    # 処理済みなら再実行しない
    if st.session_state.get("_invite_handled") == code:
        return

    if not is_logged_in():
        # ログイン後に再処理できるようコードを保持しておく
        st.session_state["pending_invite_code"] = code
        st.info("ログインすると招待リンクが有効になります。")
        return

    with get_session() as session:
        user = get_current_user(session)
        if user is None:
            return

        event = session.exec(select(Event).where(Event.invite_code == code)).first()

        if event is None:
            st.error(f"招待コード「{code}」は無効です。")
            st.query_params.clear()
            return

        already = session.exec(
            select(JoinedEvent).where(
                JoinedEvent.user_id == user.id,
                JoinedEvent.event_id == event.id,
            )
        ).first()

        if not already:
            session.add(JoinedEvent(user_id=user.id, event_id=event.id))
            session.commit()

        event_id = event.id
        description = event.description

    st.session_state["_invite_handled"] = code
    st.session_state["viewing_event_id"] = event_id
    st.session_state["current_page"] = "イベント詳細"
    st.query_params.clear()

    if not already:
        st.success(f"「{description}」に参加しました！")
    else:
        st.info(f"「{description}」にすでに参加しています。")

    st.rerun()


def handle_pending_invite() -> None:
    """ログイン直後に pending_invite_code があれば処理する。"""
    code = st.session_state.pop("pending_invite_code", None)
    if code:
        st.query_params["invite"] = code
        st.rerun()
