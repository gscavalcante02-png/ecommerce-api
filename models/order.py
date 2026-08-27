from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from enum import Enum

# TYPE_CHECKING prevents circular import loops at runtime,
# while allowing VS Code / mypy to keep auto-complete working.
if TYPE_CHECKING:
    from models.user import User

class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"

# ENRICHED ASSOCIATIVE TABLE (Order ↔ Product)
class OrderItem(SQLModel, table=True):
    order_id: int = Field(foreign_key="order.id", primary_key=True)
    product_id: int = Field(foreign_key="product.id", primary_key=True)

    # Extra fields (enriched junction)
    quantity: int = Field(default=1)
    price_at_purchase: float

    order: "Order" = Relationship(back_populates="items")


# ORDER ENTITY
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    # Foreign key pointing to User (1:N relation)
    user_id: int | None = Field(default=None, foreign_key="user.id")

    # Relationships
    user: Optional["User"] = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order")

