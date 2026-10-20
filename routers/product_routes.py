from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.connection import get_session
from crud.product_crud import (
    create_product,
    get_product,
    get_all_products,
    get_products_by_category,
    update_product,
    delete_product,
)
from dependencies import require_admin
from schemas.product import ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
def list_products(
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """
    Retrieve a paginated list of products. Optionally filter by category_id.
    """
    if category_id is not None:
        return get_products_by_category(session, category_id=category_id, skip=skip, limit=limit)
    return get_all_products(session, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single product by its ID.
    """
    db_product = get_product(session, product_id)
    if db_product is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return db_product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_product_route(product_data: ProductCreate, session: Session = Depends(get_session)):
    """
    Create a new product with categories. Requires Admin privileges.
    """
    try:
        return create_product(session, product_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_admin)])
def update_product_route(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
):
    """
    Update a product by its ID. Requires Admin privileges.
    """
    try:
        return update_product(session, product_id, product_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_product_route(product_id: int, session: Session = Depends(get_session)):
    """
    Delete a product by its ID. Requires Admin privileges.
    """
    try:
        delete_product(session, product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return None