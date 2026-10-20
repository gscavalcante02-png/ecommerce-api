from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.connection import get_session
from crud.order_crud import (
    create_order,
    get_order,
    get_orders_by_user,
    update_order_status
)
from dependencies import get_current_user, require_admin
from models.user import User, Role
from schemas.order import  OrderCreate, OrderResponse, OrderStatusUpdate 

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_route(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new order for the authenticated user, validating stock atomically.
    """
    try: 
        return create_order(session, order_data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[OrderResponse])
def list_user_orders(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Retrieve orders belonging to the currently authenticated user. 
    """
    return get_orders_by_user(session, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific order by ID. Users can only view their own orders unless they are admin.
    """
    order = get_order(session, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    if order.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order.")

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse, dependencies=[Depends(require_admin)])
def update_status_route(
    order_id: int,
    status_data: OrderStatusUpdate,
    session: Session = Depends(get_session),
):
    """
    Update the status of an order. Requires Admin privileges.
    """
    try:
        return update_order_status(session, order_id=order_id, new_status=status_data.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    