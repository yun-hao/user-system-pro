import logging
from pathlib import Path

from models import User, UserNotFoundError, ValidationError
from storage import load_users, save_users

logger = logging.getLogger(__name__)


class UserManager:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.users = load_users(file_path)

    def add_user(self, name: str, age: int | None = None, email: str | None = None, phone: str | None = None) -> User:
        if not isinstance(name, str) or not name.strip():
            logger.warning('%s 传入类型错误或为空值', name)
            raise ValidationError('name 必须是字符串类型且不为空')
        if age is not None:
            if not isinstance(age, int) or isinstance(age, bool) or age < 0:
                logger.warning('%s 传入类型错误或非法数字', age)
                raise ValidationError('age 必须是合法的数字类型且不能为布尔类型')
        if not self.users:
            user_id = 1001
        else:
            user_id = max(u.id for u in self.users) + 1
        cleaned_name = name.strip()

        user = User(user_id, cleaned_name, age, email, phone)
        self.users.append(user)
        save_users(self.file_path, self.users)
        logger.info('%s 新增成功', name)
        return user

    def get_user(self, user_id: int) -> User:
        for user in self.users:
            if user.id == user_id:
                return user
        logger.warning('%s 用户未找到,获取失败', user_id)
        raise UserNotFoundError(user_id)

    def list_users(self) -> list[User]:
        return list(self.users)

    def delete_user(self, user_id: int) -> None:
        for user in self.users:
            if user.id == user_id:
                self.users.remove(user)
                save_users(self.file_path, self.users)
                logger.info('%s 删除成功', user_id)
                return
        logger.warning('%s 用户未找到,删除失败', user_id)
        raise UserNotFoundError(user_id)
