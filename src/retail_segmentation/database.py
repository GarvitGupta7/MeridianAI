"""SQLite persistence; DATABASE_URL can later point to a PostgreSQL adapter."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect


class RetailRepository:
    """Repository with SQLite by default or PostgreSQL via DATABASE_URL.

    Example: ``DATABASE_URL=postgresql+psycopg://user:password@host:5432/retail``.
    """
    def __init__(self, path: str | Path):
        configured_url = os.getenv("DATABASE_URL")
        self.path = str(path)
        self.url = configured_url or f"sqlite:///{Path(path).resolve().as_posix()}"
        self.engine = create_engine(self.url)

    def save_frame(self, name: str, frame: pd.DataFrame) -> None:
        frame.to_sql(name, self.engine, if_exists="replace", index=False)

    def load_frame(self, name: str) -> pd.DataFrame:
        return pd.read_sql_query(f'SELECT * FROM "{name}"', self.engine)

    def tables(self) -> list[str]:
        return sorted(inspect(self.engine).get_table_names())
