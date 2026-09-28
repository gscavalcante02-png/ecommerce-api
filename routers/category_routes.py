from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.connection import get_session
from crud.category_crud import get_categories, get_category, get_category_by_name, create_category
from dependencies import require_admin
from schemas.category import CategoryCreate, CategoryResponse


router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    name: str | None = None,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """
    Retrieve categories. If `name` is provided, returns the matching
    category as a single-item list. Otherwise, returns a paginated list.
    """
    if name: 
        try: 
            category = get_category_by_name(session, name)
        except ValueError as e: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        return [category]

    return get_categories(session, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_by_id(category_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single category by its ID.
    """
    db_category = get_category(session, category_id)

    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    return db_category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_category_route(category_data: CategoryCreate, session: Session = Depends(get_session)):
    """
    Create a new category. Requires Admin privileges.
    """
    return create_category(session, category_data)