import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_data_dir = os.getenv("DATA_DIR", "data")
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "sqlite").strip().lower()
SQLITE_DB_PATH = Path(os.getenv("USERS_FILE", "data/users.db"))
MYSQL_CONFIG={
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", ""),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", ""),
}

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / _data_dir / "users.db"
USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

MYSQL_TEST_DATABASE = os.getenv("MYSQL_TEST_DATABASE", "user_system_test")