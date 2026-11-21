from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class User:
    id: int
    name: str
    age: int | None = None
    email: str | None = None
    phone: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'User':
        return cls(
            id=data['id'],
            name=data['name'],
            age=data.get('age'),
            email=data.get('email'),
            phone=data.get('phone')
        )


class StorageError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        super().__init__(f'User {user_id} not found')


class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
