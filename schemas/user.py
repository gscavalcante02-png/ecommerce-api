from pydantic import BaseModel, ConfigDict, EmailStr
from models.user import Role

class UserCreate(BaseModel):
    """Data required to register a new user."""

    name: str
    email: EmailStr
    password: str
    role: Role = Role.user


class UserResponse(BaseModel):
    """Public-facing user data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str


class UserUpdate(BaseModel):
    """"""
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: Role | None = None