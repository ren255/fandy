from pathlib import Path
import streamlit as st
from app.services.auth import is_logged_in, logout, get_current_user


def render_header() -> str:
    """ヘッダーとナビゲーションを描画。現在のページ名を返す。"""
    col_logo, col_nav, col_user = st.columns([2, 6, 2])

    with col_logo:
        logo_path = Path("static/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), width=80)
        else:
            st.write("🖼️")

    with col_nav:
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            collection_clicked = st.button(
                "コレクション", key="nav_collection", use_container_width=True
            )
        with nav_col2:
            event_clicked = st.button(
                "イベント", key="nav_event", use_container_width=True
            )

    with col_user:
        if is_logged_in():
            from app.database import get_session

            with get_session() as session:
                user = get_current_user(session)
            user_name = user.name if user else "ユーザー"

            # ユーザー名ボタンを押したらログアウトメニュー
            if st.button(
                f"👤 {user_name}", key="user_menu_btn", use_container_width=True
            ):
                st.session_state["show_logout_menu"] = not st.session_state.get(
                    "show_logout_menu", False
                )

            if st.session_state.get("show_logout_menu", False):
                if st.button("ログアウト", key="logout_btn", use_container_width=True):
                    logout()
                    st.session_state.pop("show_logout_menu", None)
                    st.rerun()
        else:
            if st.button("Sign In", key="sign_in_btn", use_container_width=True):
                st.session_state["current_page"] = "ログイン"

    # ページ管理
    if "current_page" not in st.session_state:
        st.session_state.current_page = "コレクション"
    if collection_clicked:
        st.session_state.current_page = "コレクション"
    if event_clicked:
        st.session_state.current_page = "イベント"

    st.divider()
    return st.session_state.current_page
