from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import streamlit as st


@st.cache_resource
def get_engine():
    engine = create_engine(
        "sqlite:///db.sqlite",
        connect_args={"check_same_thread": False},
    )
    return engine


@contextmanager
def get_session():
    with Session(get_engine()) as session:
        yield session
