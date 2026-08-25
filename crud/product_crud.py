
from sqlmodel import Session, select, update

from models.product import Category, Product, ProductCategory
from schemas.product import ProductCreate, ProductUpdate


def create_product(session: Session, product_data: ProductCreate) -> Product:
    """
    Create a new product with its associated categories.

    Raises ValueError if any category_id in product_data does not exist.
    """
    categories = session.exec(
        select(Category).where(Category.id.in_(product_data.category_ids))
    ).all()

    if len(categories) != len(product_data.category_ids):
        raise ValueError("One or more category_ids do not exist")

    new_product = Product(
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
        categories=categories,
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product


def get_product(session: Session, product_id: int) -> Product | None:
    """
    Retrieve a single product by its id, or None if it doesn't exist.
    """
    return session.get(Product, product_id)


def get_all_products(session: Session, skip: int = 0, limit: int = 10) -> list[Product]:
    """
    Retrieve a paginated list of products.
    """
    statement = select(Product).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_products_by_category(
    session: Session, category_name: str, skip: int = 0, limit: int = 10
) -> list[Product]:
    """
    Retrieve a paginated list of products belonging to a given category name.
    """
    statement = (
        select(Product)
        .join(ProductCategory)
        .join(Category)
        .where(Category.name == category_name)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_product(session: Session, db_product: Product, product_data: ProductUpdate):
    """
    Update only the fields provided in product_data, leaving the rest unchanged.
    """
    update_data = product_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


def deduct_stock(session: Session, product_id: int, quantity: int) -> bool:
    statement = (
        update(Product)
        .where(Product.id == product_id, Product.stock >= quantity)
        .values(stock=Product.stock - quantity)
    )

    result = session.exec(statement)
    session.commit()

    return result.rowcount > 0


def delete_product(session: Session, db_product: Product) -> bool:
    """
    Delete the given product from the database.
    """
    session.delete(db_product)
    session.commit()
    return True
