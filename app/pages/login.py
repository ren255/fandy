import streamlit as st
from app.database import get_session
from app.services.auth import login, register


def render_login() -> None:
    st.markdown("## ログイン / 新規登録")

    tab_login, tab_register = st.tabs(["ログイン", "新規登録"])

    with tab_login:
        _render_login_form()

    with tab_register:
        _render_register_form()


def _render_login_form() -> None:
    name = st.text_input("ユーザー名", key="login_name")
    password = st.text_input("パスワード", type="password", key="login_password")

    if st.button("ログイン", key="login_submit", use_container_width=True):
        if not name or not password:
            st.error("ユーザー名とパスワードを入力してください")
            return
        with get_session() as session:
            success = login(session, name, password)
        if success:
            st.success(f"ようこそ、{name} さん！")
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが正しくありません")


def _render_register_form() -> None:
    name = st.text_input("ユーザー名", key="register_name")
    password = st.text_input("パスワード", type="password", key="register_password")
    password_confirm = st.text_input(
        "パスワード（確認）", type="password", key="register_password_confirm"
    )

    if st.button("登録", key="register_submit", use_container_width=True):
        if not name or not password:
            st.error("ユーザー名とパスワードを入力してください")
            return
        if password != password_confirm:
            st.error("パスワードが一致しません")
            return
        try:
            with get_session() as session:
                register(session, name, password)
            st.success(f"登録が完了しました。{name} さん、ようこそ！")
            # 登録後に自動ログイン
            with get_session() as session:
                login(session, name, password)
            st.rerun()
        except ValueError as e:
            st.error(str(e))
