import logging

from models import User, UserNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class UserManager:
    def __init__(self, storage):
        self.storage = storage

    def add_user(self, name: str, age: int | None = None, email: str | None = None, phone: str | None = None) -> User:
        name = self._validate_name(name)
        if age is not None:
            age = self._validate_age(age)
        if email is not None:
            email = self._validate_email(email)
        if phone is not None:
            phone = self._validate_phone(phone)

        user = self.storage.add(name, age, email, phone)
        logger.info('%s 新增成功', name)
        return user

    def get_user(self, user_id: int) -> User:
        user_id = self._validate_id(user_id)
        user = self.storage.get_by_id(user_id)
        if user is None:
            logger.warning('%s 用户未找到,获取失败', user_id)
            raise UserNotFoundError(user_id)
        return user

    def list_users(self) -> list[User]:
        return self.storage.list_all()

    def delete_user(self, user_id: int) -> None:
        user_id = self._validate_id(user_id)
        deleted = self.storage.delete(user_id)
        if not deleted:
            logger.warning('没找到')
            raise UserNotFoundError(user_id)
        else:
            logger.info('%s删除成功', user_id)

    def update_user(
            self,
            user_id: int,
            name: str | None = None,
            age: int | None = None,
            email: str | None = None,
            phone: str | None = None,
    ) -> User:
        user_id = self._validate_id(user_id)
        target_user = self.get_user(user_id)
        if name is not None:
            name = self._validate_name(name)
        else:
            name = target_user.name
        if age is not None:
            age = self._validate_age(age)
        else:
            age = target_user.age
        if email is not None:
            email = self._validate_email(email)
        else:
            email = target_user.email
        if phone is not None:
            phone = self._validate_phone(phone)
        else:
            phone = target_user.phone

        target_user.name = name
        target_user.age = age
        target_user.email = email
        target_user.phone = phone
        self.storage.update(target_user)
        logger.info('%s 修改成功', user_id)
        return target_user

    @staticmethod
    def _validate_id(user_id: int) -> int:
        if not isinstance(user_id, int) or isinstance(user_id, bool):
            raise ValidationError('id必须是数字且不能是布尔类型')
        return user_id

    @staticmethod
    def _validate_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            logger.warning('%s 传入类型错误或为空值', name)
            raise ValidationError('name 必须是字符串类型且不为空')
        return name.strip()

    @staticmethod
    def _validate_email(email: str) -> str:
        if not isinstance(email, str) or not email.strip():
            logger.warning('%s 传入类型错误或都是空格', email)
            raise ValidationError('email 必须是字符串类型且不为空格')
        cleaned_email = email.strip()
        if cleaned_email and '@' not in cleaned_email:
            raise ValidationError('邮箱格式不正确')
        return cleaned_email

    @staticmethod
    def _validate_phone(phone: str) -> str:
        if not isinstance(phone, str) or not phone.strip():
            logger.warning('%s 传入类型错误或都是空格', phone)
            raise ValidationError('phone 必须是字符串类型且不为空格')
        cleaned_phone = phone.strip()
        if cleaned_phone and (not cleaned_phone.isdigit() or len(cleaned_phone) != 11):
            raise ValidationError('电话号码必须是11位的数字')
        return cleaned_phone

    @staticmethod
    def _validate_age(age: int) -> int:
        if not isinstance(age, int) or isinstance(age, bool) or age < 0:
            logger.warning('%s 传入类型错误或非法数字', age)
            raise ValidationError('age 必须是合法的数字类型且不能为布尔类型')
        return age
