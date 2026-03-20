import streamlit as st
from app.pages.header import render_header
from app.pages.collection import render_collection
from app.pages.event import render_event
from app.pages.login import render_login
from app.pages.event_form import render_event_form
from app.pages.invite_form import render_invite_form
from app.pages.event_page import render_event_page
from app.pages.photo_upload import render_photo_upload

from app.pages.invite_redirect import handle_invite_redirect, handle_pending_invite
from app.services.auth import is_logged_in


def main() -> None:
    st.set_page_config(
        page_title="App",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    handle_invite_redirect()

    page = render_header()

    # ログイン直後のpending invite処理
    if is_logged_in():
        handle_pending_invite()

    if page == "コレクション":
        render_collection()
    elif page == "イベント":
        render_event()
    elif page == "ログイン":
        render_login()
    elif page == "イベント作成":
        render_event_form()
    elif page == "招待コード参加":
        render_invite_form()
    elif page == "イベント詳細":
        event_id = st.session_state.get("viewing_event_id")
        if event_id:
            render_event_page(event_id)
    elif page == "写真アップロード":
        render_photo_upload()


if __name__ == "__main__":
    main()
