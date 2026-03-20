import hashlib
import streamlit as st
from sqlmodel import select
from app.models import User


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def is_logged_in() -> bool:
    return st.session_state.get("user_id") is not None


def get_current_user(session) -> User | None:
    user_id = st.session_state.get("user_id")
    if user_id is None:
        return None
    return session.get(User, user_id)


def login(session, name: str, password: str) -> bool:
    """成功時True、失敗時False"""
    hashed = _hash_password(password)
    user = session.exec(
        select(User).where(User.name == name, User.password == hashed)
    ).first()
    if user is None:
        return False
    st.session_state["user_id"] = user.id
    return True


def logout() -> None:
    st.session_state.pop("user_id", None)


def require_login() -> User:
    """未ログインならst.stop()。ログイン済みならUserを返す。"""
    if not is_logged_in():
        st.warning("ログインが必要です")
        st.stop()
    from app.database import get_session

    with get_session() as session:
        user = get_current_user(session)
        if user is None:
            logout()
            st.warning("ユーザーが見つかりません")
            st.stop()
        return user


def register(session, name: str, password: str) -> User:
    """新規ユーザー作成。名前重複時はValueError。"""
    exists = session.exec(select(User).where(User.name == name)).first()
    if exists:
        raise ValueError(f"ユーザー名 '{name}' はすでに使われています")
    user = User(name=name, password=_hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
