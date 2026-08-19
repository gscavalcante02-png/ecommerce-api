from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

# ASSOCIATIVE TABLE (Product ↔ Category)
class ProductCategory(SQLModel, table=True):
    product_id: int = Field(
        foreign_key="product.id", primary_key=True
    )
    category_id: int = Field(
        foreign_key="category.id", primary_key=True
    )

# CATEGORY ENTITY
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationship back to products 
    products: List["Product"] = Relationship(
        back_populates="categories", link_model=ProductCategory
    )

# PRODUCT ENTITY
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    stock: int = 0

    # N:N Relationship pointing to Category through ProductCategory
    categories: List[Category] = Relationship(
        back_populates="products", link_model=ProductCategory
    )