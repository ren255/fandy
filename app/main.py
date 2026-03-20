import streamlit as st
from app.pages.header import render_header
from app.pages.collection import render_collection
from app.pages.event import render_event
from app.pages.login import render_login
from app.pages.event_form import render_event_form
from app.pages.invite_form import render_invite_form


def main() -> None:
    st.set_page_config(
        page_title="App",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    current_page = render_header()

    if current_page == "コレクション":
        render_collection()
    elif current_page == "イベント":
        render_event()
    elif current_page == "ログイン":
        render_login()
    elif current_page == "イベント作成":
        render_event_form()
    elif current_page == "招待コード参加":
        render_invite_form()


if __name__ == "__main__":
    main()
