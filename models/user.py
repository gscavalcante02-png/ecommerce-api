from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from enum import Enum 

# TYPE_CHECKING prevents circular import loops at runtime,
# while allowing VS Code / mypy to keep auto-complete working.
if TYPE_CHECKING:
    from models.order import Order

class Role(str, Enum):
    user = "user"
    admin = "admin"

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: Role = Field(default=Role.user)

    # 1:N Relationship with Order
    # A user can have a list of orders
    orders: list["Order"] = Relationship(back_populates="user")
