import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_data_dir = os.getenv("DATA_DIR", "data")

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / _data_dir / "users.db"
USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
