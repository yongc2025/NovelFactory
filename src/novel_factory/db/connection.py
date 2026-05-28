"""
SQLite 连接管理 -- WAL 模式 + 外键约束 + 自动建目录
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from novel_factory.config import settings


def _ensure_db_dir(db_path: Path) -> None:
    """确保数据库文件所在目录存在。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    获取 SQLite 连接的上下文管理器。

    - 自动创建 data/ 目录
    - 启用 WAL 模式（提升并发读写性能）
    - 启用外键约束
    - 提交事务 / 异常回滚 / 最终关闭
    """
    db_path = settings.db_path_resolved
    _ensure_db_dir(db_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
