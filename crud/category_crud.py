
from sqlmodel import Session, select

from models.product import Category
from schemas.category import CategoryCreate


def create_category(session: Session, category: CategoryCreate):
    """
    Create a new category in the database and return it.
    """
    new_category = Category(name=category.name)
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


def get_category(session: Session, category_id: int) -> Category | None:
    """
    Retrieve a single category by its id, or None if it doesn't exist.
    """
    return session.get(Category, category_id)


def get_categories(session: Session, skip: int = 0, limit: int = 10) -> list[Category]:
    """
    Retrieve a paginated list of categories.
    """
    statement = select(Category).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_category_by_name(session: Session, name: str) -> Category:
    """
    Retrieve a single category by its name.

    Raises ValueError if no category with the given name exists.
    """
    category = session.exec(
        select(Category).where(Category.name == name)
    ).first()

    if category is None:
        raise ValueError(f"Category '{name}' not found.")

    return category
