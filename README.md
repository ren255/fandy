# app

StreamlitとSQLModelを使ったシンプルなCRUDアプリのテンプレート。  
SQLiteをDBとして使用し、Dockerで起動できる。

## Quick Start

### コードコピー
```sh
git clone  
```

### データベースファイルを先に作る。
dockerにマウントするときフォルダでなくファイルになるようにするため
```sh
touch db.sqlite
```

### 起動
```sh
docker compose up
```

ブラウザで http://localhost:8501 にアクセス。
コードの変更がはリロードで反映される


### localの環境構築
```sh
python4 -m venv .venv
source .venv/bin/active
pip install -r requirements.txt
```

## Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py       # Streamlitエントリポイント
│   ├── database.py   # エンジン・セッション管理
│   └── models.py     # SQLModelモデル定義
├── db.sqlite         # SQLiteデータベース（自動生成）
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Other Things

**依存関係**

| パッケージ | 用途 |
|-----------|------|
| streamlit | UIフレームワーク |
| sqlmodel  | ORM（SQLAlchemy + Pydantic） |


**DBの初期化**

エンジン初回取得時に `SQLModel.metadata.create_all(engine)` が走るため、マイグレーションツールは不要、create_all はデータを消さないため、db.sqlite をvolumeマウントしている限りデータは永続化される。スキーマ変更時は `db.sqlite` を削除して再起動する。

