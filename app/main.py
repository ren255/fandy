import streamlit as st
from app.pages.header import render_header
from app.pages.collection import render_collection
from app.pages.event import render_event
from app.pages.login import render_login


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


if __name__ == "__main__":
    main()
