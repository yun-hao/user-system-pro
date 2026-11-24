from storage import SQLiteStorage, MySQLStorage

try:
    import readline
except ImportError:
    pass
import logging

import config
from models import StorageError, UserNotFoundError, ValidationError
from user_manager import UserManager

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.BASE_DIR / 'app.log', encoding='utf-8'),
        ]
    )

def create_storage():
    if config.STORAGE_TYPE == 'sqlite':
        return SQLiteStorage(config.USERS_FILE)
    if config.STORAGE_TYPE == 'mysql':
        return MySQLStorage(**config.MYSQL_CONFIG)
    raise ValueError(f"不支持的 STORAGE_TYPE: {config.STORAGE_TYPE}")


def main() -> None:
    setup_logging()
    try:
        storage = create_storage()
        manager = UserManager(storage)
    except (StorageError,ValueError) as e:
        print(e)
        exit(1)
    while True:
        print('-------用户管理系统--------')
        print('1. 新增用户\n2. 查看所有用户\n3. 按ID查询用户\n4. 删除用户\n5. 修改用户\n6. 退出')
        choice = input('请输入你的选择').strip()
        match choice:
            case '1':
                try:
                    name = input('请输入名字')
                    raw_age = input('请输入年龄(回车跳过): ').strip()
                    age = int(raw_age) if raw_age else None
                    email = input('请输入邮箱(回车跳过): ').strip() or None
                    phone = input('请输入电话(回车跳过): ').strip() or None
                    user = manager.add_user(name, age, email, phone)
                    print(f'{user}增加成功')
                except ValueError as e:
                    logger.warning('请输入有效整数')
                except ValidationError as e:
                    print(e)
                except StorageError as e:
                    print(e)

            case '2':
                try:
                    all_users = manager.list_users()
                    users_map = {user.id: user.name for user in all_users}
                    print(users_map)
                except StorageError as e:
                    print(e)

            case '3':
                try:
                    target_id_input = input('输入目标id').strip()
                    if not target_id_input:
                        raise ValidationError('目标为空')
                    else:
                        target_id = int(target_id_input)
                        user = manager.get_user(target_id)
                        user_info = {'name': user.name, 'age': user.age, 'email': user.email, 'phone': user.phone}
                        print(user_info)
                except ValueError as e:
                    logger.warning('请输入有效整数')
                except ValidationError as e:
                    print(e)
                except UserNotFoundError as e:
                    print(e)
                except StorageError as e:
                    print(e)
            case '4':
                try:
                    target_id_input = input('输入目标id').strip()
                    if not target_id_input:
                        raise ValidationError('目标id不能是空格')
                    else:
                        target_id = int(target_id_input)
                        manager.delete_user(target_id)
                        print(f'{target_id}删除成功')

                except ValueError as e:
                    logger.warning('请输入有效整数')
                except ValidationError as e:
                    print(e)
                except UserNotFoundError as e:
                    print(e)
                except StorageError as e:
                    print(e)

            case '5':
                try:
                    target_id_input = input('输入目标id').strip()
                    if not target_id_input:
                        raise ValidationError('目标id不能是空格')
                    else:
                        target_id = int(target_id_input)
                    name = input('请修改名字').strip() or None
                    raw_age = input('请输入年龄(回车跳过): ').strip()
                    age = int(raw_age) if raw_age else None
                    email = input('请修改邮箱(回车跳过): ').strip() or None
                    phone = input('请修改电话(回车跳过): ').strip() or None
                    target_user = manager.update_user(target_id, name, age, email, phone)
                    print(f'{target_user.id}成功修改为{target_user.name}')
                except ValueError as e:
                    logger.warning('请输入有效整数')
                except ValidationError as e:
                    print(e)
                except UserNotFoundError as e:
                    print(e)
                except StorageError as e:
                    print(e)
            case '6':
                break
            case _:
                print('请输入正确的选择')
                continue


if __name__ == '__main__':
    main()
