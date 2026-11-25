import pytest

import config
from models import ValidationError, UserNotFoundError, StorageError
from storage import SQLiteStorage, MySQLStorage
from user_manager import UserManager


@pytest.fixture(params=['sqlite', 'mysql'])
def manager(request, tmp_path):
    if request.param == 'sqlite':
        storage = SQLiteStorage(tmp_path / 'test.db')
        return UserManager(storage)

    elif request.param == 'mysql':
        test_config = {**config.MYSQL_CONFIG, "database": config.MYSQL_TEST_DATABASE}
        storage = MySQLStorage(**test_config)
        conn = storage._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                TRUNCATE TABLE users;
                """)
            conn.commit()
        finally:
            conn.close()
        return UserManager(storage)

def test_add_and_list_users(manager) -> None:
    # 1. Arrange（准备）：在 pytest 提供的临时目录里拼一个测试文件路径，实例化管理器

    # 2. Act（执行）：写死两组正常数据，直接调用业务方法
    u1 = manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")
    u2 = manager.add_user(name="李四")  # 故意不传选填项，顺便验证默认值是不是 None
    users = manager.list_users()

    # 3. Assert（断言）：验证结果是否完全符合预期
    assert u1.id == 1
    assert u2.id == 2
    assert len(users) == 2
    assert users[0].name == "张三"
    assert users[0].age == 20
    assert users[1].name == "李四"
    assert users[1].age is None


def test_persistence_across_instances(manager) -> None:
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    users = manager.list_users()
    # 3
    assert users[0].name == "张三"
    assert users[0].age == 20


def test_add_user_validation_error(manager) -> None:
    # 1. Arrange

    with pytest.raises(ValidationError):
        manager.add_user(name="")

    with pytest.raises(ValidationError):
        manager.add_user(name=" ")

    with pytest.raises(ValidationError):
        manager.add_user(name="张三", age=-1)

    with pytest.raises(ValidationError):
        manager.add_user(name="张三", age=True)


def test_get_and_delete_user_not_found(manager) -> None:
    with pytest.raises(UserNotFoundError):
        manager.get_user(9999)

    with pytest.raises(UserNotFoundError):
        manager.delete_user(9999)


def test_load_corrupted_db_raises_storage_error(tmp_path) -> None:
    file_path = tmp_path / "users.db"
    file_path.write_text("not a valid sqlite file")
    with pytest.raises(StorageError):
        SQLiteStorage(file_path)


def test_update_user_success(manager) -> None:
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    manager.update_user(user_id=1, age=40, email=None)
    users1 = manager.list_users()
    assert users1[0].id == 1
    assert users1[0].age == 40
    assert users1[0].name == '张三'
    assert users1[0].email == "zs@example.com"
    assert users1[0].phone == "13800000001"

    users2 = manager.list_users()
    assert users2[0].id == 1
    assert users2[0].age == 40
    assert users2[0].name == '张三'
    assert users2[0].email == "zs@example.com"
    assert users2[0].phone == "13800000001"


def test_update_user_errors(manager) -> None:
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")


    with pytest.raises(UserNotFoundError):
        manager.update_user(user_id=9999)
    with pytest.raises(ValidationError):
        users = manager.list_users()
        manager.update_user(user_id=1, name='王五', age=-1)
    assert users[0].name == '张三'

    with pytest.raises(ValidationError):
        manager.update_user(user_id=1, email="zsexample.com")
    with pytest.raises(ValidationError):
        manager.update_user(user_id=1, phone="1111111")
    with pytest.raises(ValidationError):
        manager.update_user(user_id=True)


def test_delete_user_success(manager) -> None:
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    manager.delete_user(user_id=1)

    assert manager.list_users() == []


def test_add_duplicate_email_raise_storage_error(manager) -> None:
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")
    with pytest.raises(StorageError):
        manager.add_user(name='李四', email="zs@example.com")


def test_data_persists_across_instances(manager) -> None:
    created = manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    loaded = manager.get_user(1)
    assert created == loaded


def test_mysql_invalid_password_raises_storage_error():
    bad_config = {**config.MYSQL_CONFIG,"password": "<PASSWORD>"}
    with pytest.raises(StorageError):
        MySQLStorage(**bad_config)
