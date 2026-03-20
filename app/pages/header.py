from pathlib import Path
import streamlit as st


def render_header() -> str:
    """ヘッダーとナビゲーションを描画。現在のページ名を返す。"""
    # 1行: ロゴ | ナビゲーション | Sign In
    col_logo, col_nav, col_signin = st.columns([2, 6, 2])

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

    with col_signin:
        st.button("Sign In", key="sign_in_btn", use_container_width=True)

    # セッション状態でページ管理
    if "current_page" not in st.session_state:
        st.session_state.current_page = "コレクション"
    if collection_clicked:
        st.session_state.current_page = "コレクション"
    if event_clicked:
        st.session_state.current_page = "イベント"

    st.divider()
    return st.session_state.current_page
