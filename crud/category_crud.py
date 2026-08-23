from typing import List, Optional
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


def get_category(session: Session, category_id: int) -> Optional[Category]:
    """
    Retrieve a single category by its id, or None if it doesn't exist.
    """
    return session.get(Category, category_id)


def get_categories(session: Session, skip: int = 0, limit: int = 10 ) -> List[Category]:
    """
    Retrieve a paginated list of categories.
    """
    statement = select(Category).offset(skip).limit(limit)
    return list(session.exec(statement).all())