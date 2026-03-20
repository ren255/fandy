from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import time

import streamlit as st
from sqlmodel import select

from app.database import get_session
from app.models import Note, UploadedFile

CHAR_LIMIT = 140
FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

IMAGE_MIMES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}


def utc_now() -> int:
    return int(time.time())


def fmt_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def save_file(uploaded) -> Path:
    """UploadedFile を files/ に保存してパスを返す。タイムスタンプprefixで衝突回避。"""
    ts = int(time.time() * 1000)
    stem = Path(uploaded.name).stem
    suffix = Path(uploaded.name).suffix
    dest = FILES_DIR / f"{ts}_{stem}{suffix}"
    dest.write_bytes(uploaded.getvalue())
    return dest


def render_attachment(file_id: Optional[int]) -> None:
    """添付ファイルを描画する。画像はプレビュー、それ以外はダウンロードボタン。"""
    if file_id is None:
        return
    with get_session() as session:
        f = session.get(UploadedFile, file_id)
    if f is None:
        st.caption("添付ファイルが見つかりません")
        return
    p = Path(f.file_path)
    if not p.exists():
        st.caption(f"ファイルが削除されています: `{f.file_path}`")
        return
    if f.mime_type in IMAGE_MIMES:
        st.image(str(p), caption=f.original_name, use_container_width=True)
    else:
        st.download_button(
            label=f"⬇️ {f.original_name}",
            data=p.read_bytes(),
            file_name=f.original_name,
            mime=f.mime_type,
            key=f"dl_att_{file_id}",
        )


def render_note(note: Note) -> None:
    """Noteを1件描画する。添付があれば続けて表示。"""
    st.subheader(f"By {note.username} at {fmt_ts(note.created_timestamp)}")
    st.caption(f"Note #{note.id} — Updated at {fmt_ts(note.updated_timestamp)}")
    st.write(note.body)
    render_attachment(note.file_id)


def render_read() -> None:
    with get_session() as session:
        notes = session.exec(select(Note).order_by(Note.id.desc())).all()

    with st.expander("Raw table data"):
        st.table([n.model_dump() for n in notes])

    for note in notes:
        render_note(note)
        st.divider()


def render_create() -> None:
    with st.form("create_form", clear_on_submit=True):
        username = st.text_input("Username", value="anonymous", max_chars=CHAR_LIMIT)
        body = st.text_area("Note", value="Sample Note", max_chars=CHAR_LIMIT)
        uploaded = st.file_uploader("添付ファイル（任意）")
        if st.form_submit_button("Submit"):
            now = utc_now()
            file_id = None
            if uploaded:
                dest = save_file(uploaded)
                with get_session() as session:
                    f = UploadedFile(
                        created_timestamp=now,
                        username=username,
                        original_name=uploaded.name,
                        file_path=str(dest),
                        mime_type=uploaded.type or "application/octet-stream",
                    )
                    session.add(f)
                    session.commit()
                    session.refresh(f)
                    file_id = f.id
            with get_session() as session:
                session.add(
                    Note(
                        created_timestamp=now,
                        updated_timestamp=now,
                        username=username,
                        body=body,
                        file_id=file_id,
                    )
                )
                session.commit()
            st.success("Note created!")


def render_update() -> None:
    with get_session() as session:
        notes = session.exec(select(Note).order_by(Note.id.desc())).all()

    if not notes:
        st.info("ノートがありません。")
        return

    note_map = {n.id: n for n in notes}
    note_id = st.selectbox(
        "更新するノートを選択",
        note_map.keys(),
        format_func=lambda x: f"#{x} — {note_map[x].username} / {fmt_ts(note_map[x].created_timestamp)}",
    )
    target = note_map[note_id]

    with st.form("update_form"):
        username = st.text_input(
            "Username", value=target.username, max_chars=CHAR_LIMIT
        )
        body = st.text_area("Note", value=target.body, max_chars=CHAR_LIMIT)
        uploaded = st.file_uploader("添付ファイルを差し替え（任意）")
        if st.form_submit_button("Update"):
            now = utc_now()
            file_id = target.file_id
            if uploaded:
                dest = save_file(uploaded)
                with get_session() as session:
                    f = UploadedFile(
                        created_timestamp=now,
                        username=username,
                        original_name=uploaded.name,
                        file_path=str(dest),
                        mime_type=uploaded.type or "application/octet-stream",
                    )
                    session.add(f)
                    session.commit()
                    session.refresh(f)
                    file_id = f.id
            with get_session() as session:
                note = session.get(Note, note_id)
                note.username = username
                note.body = body
                note.updated_timestamp = now
                note.file_id = file_id
                session.add(note)
                session.commit()
            st.success(f"Note #{note_id} を更新しました。")


def render_delete() -> None:
    with get_session() as session:
        notes = session.exec(select(Note).order_by(Note.id.desc())).all()

    if not notes:
        st.info("ノートがありません。")
        return

    note_map = {n.id: n for n in notes}
    note_id = st.selectbox("削除するノートを選択", note_map.keys())
    render_note(note_map[note_id])

    if st.button("🗑️ Delete (取り消し不可)", type="primary"):
        with get_session() as session:
            note = session.get(Note, note_id)
            session.delete(note)
            session.commit()
        st.success(f"Note #{note_id} を削除しました。")
        st.rerun()


def render_files() -> None:
    """アップロード済みファイルの一覧。どのNoteに紐づいているか表示。"""
    with get_session() as session:
        files = session.exec(
            select(UploadedFile).order_by(UploadedFile.id.desc())
        ).all()

    if not files:
        st.info("ファイルがまだありません。")
        return

    with st.expander("Raw table data"):
        st.table([f.model_dump() for f in files])

    for f in files:
        p = Path(f.file_path)
        st.markdown(f"**#{f.id}** `{f.original_name}` — {fmt_ts(f.created_timestamp)}")
        st.caption(f"`{f.file_path}` | `{f.mime_type}`")
        if not p.exists():
            st.warning("ファイルが見つかりません")
            continue
        if f.mime_type in IMAGE_MIMES:
            st.image(str(p), caption=f.original_name, use_container_width=True)
        else:
            st.download_button(
                label=f"⬇️ {f.original_name}",
                data=p.read_bytes(),
                file_name=f.original_name,
                mime=f.mime_type,
                key=f"dl_{f.id}",
            )
        st.divider()


def render_about() -> None:
    readme = Path("README.md")
    st.markdown(
        readme.read_text() if readme.exists() else "README.md が見つかりません。"
    )
