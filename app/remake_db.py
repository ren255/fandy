# app/remake_db.py
from sqlmodel import SQLModel, create_engine
import app.models  # noqa: モデル登録のため必須

engine = create_engine(
    "sqlite:///db.sqlite",
    connect_args={"check_same_thread": False},
    echo=True,
)

SQLModel.metadata.drop_all(engine)  # 既存テーブルを全削除
SQLModel.metadata.create_all(engine)  # 再作成

print("Done.")
