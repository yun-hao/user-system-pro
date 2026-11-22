from pathlib import Path

import pytest

from models import ValidationError, UserNotFoundError, StorageError
from user_manager import UserManager


def test_add_and_list_users(tmp_path: Path) -> None:
    # 1. Arrange（准备）：在 pytest 提供的临时目录里拼一个测试文件路径，实例化管理器
    file_path = tmp_path / "users.json"
    manager = UserManager(file_path)

    # 2. Act（执行）：写死两组正常数据，直接调用业务方法
    u1 = manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")
    u2 = manager.add_user(name="李四")  # 故意不传选填项，顺便验证默认值是不是 None
    users = manager.list_users()

    # 3. Assert（断言）：验证结果是否完全符合预期
    assert u1.id == 1001
    assert u2.id == 1002
    assert len(users) == 2
    assert users[0].name == "张三"
    assert users[0].age == 20
    assert users[1].name == "李四"
    assert users[1].age is None


def test_persistence_across_instances(tmp_path) -> None:
    # 1. Arrange
    file_path = tmp_path / "users.json"

    # 2. Act（执行）
    manager1 = UserManager(file_path)
    manager1.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    manager2 = UserManager(file_path)
    users = manager2.list_users()
    # 3
    assert users[0].name == "张三"
    assert users[0].age == 20


def test_add_user_validation_error(tmp_path) -> None:
    # 1. Arrange
    file_path = tmp_path / "users.json"
    manager = UserManager(file_path)

    with pytest.raises(ValidationError):
        manager.add_user(name="")

    with pytest.raises(ValidationError):
        manager.add_user(name=" ")

    with pytest.raises(ValidationError):
        manager.add_user(name="张三", age=-1)

    with pytest.raises(ValidationError):
        manager.add_user(name="张三", age=True)


def test_get_and_delete_user_not_found(tmp_path) -> None:
    file_path = tmp_path / "users.json"
    manager = UserManager(file_path)
    with pytest.raises(UserNotFoundError):
        manager.get_user(9999)

    with pytest.raises(UserNotFoundError):
        manager.delete_user(9999)


def test_load_corrupted_json_raises_storage_error(tmp_path) -> None:
    file_path = tmp_path / "users.json"
    file_path.write_text("{bad json")
    with pytest.raises(StorageError):
        UserManager(file_path)


def test_update_user_success(tmp_path) -> None:
    file_path = tmp_path / "users.json"
    manager = UserManager(file_path)
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    manager.update_user(user_id=1001, age=40, email=None)
    users1 = manager.list_users()
    assert users1[0].id == 1001
    assert users1[0].age == 40
    assert users1[0].name == '张三'
    assert users1[0].email == "zs@example.com"
    assert users1[0].phone == "13800000001"

    manager = UserManager(file_path)
    users2 = manager.list_users()
    assert users2[0].id == 1001
    assert users2[0].age == 40
    assert users2[0].name == '张三'
    assert users2[0].email == "zs@example.com"
    assert users2[0].phone == "13800000001"


def test_update_user_errors(tmp_path: Path) -> None:
    file_path = tmp_path / "users.json"
    manager = UserManager(file_path)
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")
    users = manager.list_users()

    with pytest.raises(UserNotFoundError):
        manager.update_user(user_id=9999)
    with pytest.raises(ValidationError):
        manager.update_user(user_id=1001, name='王五', age=-1)
    assert users[0].name == '张三'

    with pytest.raises(ValidationError):
        manager.update_user(user_id=1001, email="zsexample.com")
    with pytest.raises(ValidationError):
        manager.update_user(user_id=1001, phone="1111111")
    with pytest.raises(ValidationError):
        manager.update_user(user_id=True)


def test_delete_user_success(tmp_path: Path) -> None:
    file_path = tmp_path / "users.json"
    manager = UserManager(file_path)
    manager.add_user(name="张三", age=20, email="zs@example.com", phone="13800000001")

    manager.delete_user(user_id=1001)
    manager = UserManager(file_path)
    assert manager.list_users() == []
