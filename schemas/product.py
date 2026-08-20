from typing import List
from pydantic import BaseModel, ConfigDict


class CategoryInProduct(BaseModel):
    """Minimal category info shown inside a product response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProductCreate(BaseModel):
    """Data required to create a new product."""
    name: str
    price: float
    stock: int


class ProductResponse(BaseModel):
    """Product data returned by the API, including its categories."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    stock: int
    categories: List[CategoryInProduct]