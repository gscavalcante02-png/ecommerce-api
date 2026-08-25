from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Data required to register a new user."""

    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public-facing user data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
