from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    age: int | None = None
    email: str | None = None
    phone: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    email: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    age: int | None = None
    email: str | None = None
    phone: str | None = None
