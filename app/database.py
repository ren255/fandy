from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import streamlit as st

# ホットリロード対策
from sqlmodel.main import default_registry

SQLModel.metadata.clear()
default_registry.dispose()

import app.models  # noqa: E402  モデル登録のため必須


@st.cache_resource
def get_engine():
    """アプリ全体で共有するエンジンを返す（シングルトン）"""
    engine = create_engine(
        "sqlite:///db.sqlite",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    _seed(engine)
    return engine


@contextmanager
def get_session():
    with Session(get_engine()) as session:
        yield session


# シード
def _seed(engine) -> None:
    from sqlmodel import select
    from app.models import Note
    import time

    with Session(engine) as session:
        exists = session.exec(select(Note)).first()
        if exists:
            return
        now = int(time.time())
        session.add(
            Note(
                created_timestamp=now,
                updated_timestamp=now,
                username="SYSTEM",
                body="Auto Generated Note!!! :tada:",
            )
        )
        session.commit()
