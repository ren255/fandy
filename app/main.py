from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import time

import streamlit as st
from sqlmodel import select

from app.database import get_session
from app.models import Note, UploadedFile

from app.pages.pages import (
    render_read,
    render_create,
    render_update,
    render_delete,
    render_files,
    render_about,
)


def main() -> None:
    st.header("The Littlest Fullstack App!")
    views = {
        "Read Note Feed": render_read,
        "Create a Note": render_create,
        "Update a Note": render_update,
        "Delete a Note": render_delete,
        "Browse Files": render_files,
        "About": render_about,
    }
    choice = st.sidebar.radio("Go To Page:", views.keys())
    views[choice]()


if __name__ == "__main__":
    main()
