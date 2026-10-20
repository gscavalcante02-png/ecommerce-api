from datetime import datetime

from pydantic import BaseModel, ConfigDict
from models.order import OrderStatus

class OrderItemCreate(BaseModel):
    """A single item the costumer wants to include in the order."""

    product_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    """A single item within an order, as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    price_at_purchase: float


class OrderCreate(BaseModel):
    """Data required to place a new order - a list of items to purchase."""

    items: list[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    """Data required to update an order's status."""

    status: OrderStatus


class OrderResponse(BaseModel):
    """Order data returned by the API, including all its items."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    status: OrderStatus
    created_at: datetime
    items: list[OrderItemResponse]
