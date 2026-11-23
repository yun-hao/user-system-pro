import logging
import sqlite3
from pathlib import Path

from models import User, StorageError

logger = logging.getLogger(__name__)


class SQLiteStorage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER ,
                    email TEXT UNIQUE,
                    phone TEXT)
                    """
                )
        except sqlite3.Error as e:
            logger.error(e)
            raise StorageError('建表异常') from e
        finally:
            conn.close()

    def add(self, name: str, age: int | None = None, email: str | None = None, phone: str | None = None) -> User:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (name,age,email,phone) VALUES (?,?,?,?)
                """, (name, age, email, phone))
                user_id = cursor.lastrowid
                return User(id=user_id, name=name, age=age, email=email, phone=phone)
        except sqlite3.Error as e:
            logger.error(e)
            raise StorageError('新增用户失败') from e
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> User | None:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT * FROM users WHERE id = ?
                """, (user_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                else:
                    return User.from_dict(dict(row))
        except sqlite3.Error as e:
            logger.error(e)
            raise StorageError('获取id失败') from e
        finally:
            conn.close()

    def list_all(self) -> list[User]:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT * FROM users ORDER BY id 
                """)
                rows = cursor.fetchall()
                users = [User.from_dict(dict(u)) for u in rows]
                return users
        except sqlite3.Error as e:
            logger.error(e)
            raise StorageError('读取用户失败') from e
        finally:
            conn.close()

    def delete(self, user_id: int) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                DELETE FROM users WHERE id = ?
                """, (user_id,))
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            logger.error(e)
            raise StorageError('删除用户失败') from e
        finally:
            conn.close()

    def update(self, user: User) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE users SET name=?, age=?, email=?, phone=? WHERE id = ?
                """, (user.name, user.age, user.email, user.phone, user.id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(e)
            raise StorageError('更新用户失败') from e
        finally:
            conn.close()
