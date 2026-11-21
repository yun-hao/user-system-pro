import json
import logging
from pathlib import Path

from models import User, StorageError

logger = logging.getLogger(__name__)


def load_users(file_path: Path) -> list[User]:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        logger.info('文件不存在')
        return []
    try:
        raw_data = json.loads(file_path.read_text(encoding='utf-8'))
        users = [User.from_dict(item) for item in raw_data]
        return users
    except OSError as e:
        logger.error('读取文件: %s 失败: %s', file_path, e)
        raise StorageError('读取文件失败') from e
    except json.decoder.JSONDecodeError as e:
        logger.error('解析: %s 错误', file_path)
        raise StorageError('文件解析错误') from e
    except KeyError as e:
        logger.error('重要字段异常 id|name : %s', e)
        raise StorageError('重要字段异常 id|name') from e
    except TypeError as e:
        logger.error('数据类型异常: %s', e)
        raise StorageError('数据类型异常') from e


def save_users(file_path: Path, users: list[User]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw_data = [user.to_dict() for user in users]
        file_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding='utf-8')
    except OSError as e:
        logger.error('写入文件: %s 失败: %s', file_path, e)
        raise StorageError('写入文件失败') from e
