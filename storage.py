import logging
import sqlite3
from pathlib import Path

import pymysql

from models import User, StorageError, UserNotFoundError

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


class MySQLStorage:
    def __init__(self, host, port, user, password, database) -> None:
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database = database
        self._init_db()

    def _get_connection(self):
        conn = pymysql.connect(host=self.host,
                               port=self.port,
                               user=self.user,
                               password=self.password,
                               database=self.database,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        return conn

    def _init_db(self):
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL,
                age INT,
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(50)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
                conn.commit()
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()
            logger.error(e)
            raise StorageError('初始化数据库表失败') from e
        finally:
            if conn:
                conn.close()

    def add(self, name: str, age: int | None = None, email: str | None = None, phone: str | None = None) -> User:
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO users (name,age,email,phone) VALUES (%s,%s,%s,%s)
                """, (name, age, email, phone))
                user_id = cursor.lastrowid
                new_user = User(id=user_id, name=name, age=age, email=email, phone=phone)
                conn.commit()
                return new_user
        except pymysql.IntegrityError as e:
            if conn:
                conn.rollback()
            logger.error(e)
            raise StorageError(f'字段 {email} 冲突用户增加失败')
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()
            logger.error(e)
            raise StorageError('数据库写入失败') from e
        finally:
            if conn:
                conn.close()

    def get_by_id(self, user_id: int) -> User | None:
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT * FROM users WHERE id = %s
                """, (user_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return User.from_dict(row)
        except pymysql.MySQLError as e:
            logger.warning(e)
            raise StorageError(f'获取 {user_id} 失败') from e
        finally:
            if conn:
                conn.close()

    def list_all(self) -> list[User]:
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT * FROM users ORDER BY id 
                """)
                rows = cursor.fetchall()
                users = [User.from_dict(row) for row in rows]
                return users
        except pymysql.MySQLError as e:
            logger.error(e)
            raise StorageError('用户读取失败') from e
        finally:
            if conn:
                conn.close()

    def delete(self, user_id :int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                DELETE FROM users WHERE id = %s
                """, (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()
            logger.error(e)
            raise StorageError('数据库删除失败') from e
        finally:
            if conn:
                conn.close()

    def update(self, user: User) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                UPDATE users SET name=%s, age=%s, email=%s, phone=%s WHERE id = %s
                """, (user.name, user.age, user.email, user.phone, user.id))
                conn.commit()
                return cursor.rowcount > 0
        except pymysql.IntegrityError as e:
            if conn:
                conn.rollback()
            logger.error(e)
            raise StorageError('邮箱重复更新失败') from e
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()
            logger.error(e)
            raise StorageError('数据库更新失败') from e
        finally:
            if conn:
                conn.close()
