from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import streamlit as st
import app.models  # noqa: トップレベルでインポート


@st.cache_resource
def get_engine():
    engine = create_engine(
        "sqlite:///db.sqlite",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine


@contextmanager
def get_session():
    with Session(get_engine()) as session:
        yield session
