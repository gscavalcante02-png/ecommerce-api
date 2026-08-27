from sqlmodel import Session, select

from models.order import Order, OrderItem, OrderStatus
from schemas.order import OrderCreate

from crud.product_crud import get_product, _deduct_stock_no_commit


def create_order(session: Session, order_data: OrderCreate, user_id: int) -> Order:
    """
    Create a new order with its items, validating product existence and stock.

    Stock is deducted atomically with order creation: if any item fails
    validation, nothing is committed (no order, no stock deduction).
    """
    order_items = []

    for item in order_data.items:
        product = get_product(session, item.product_id)

        if product is None:
            raise ValueError(f"Product {item.product_id} not found")

        if product.stock < item.quantity:
            raise ValueError(f"Insufficient stock for product '{product.name}'")

        _deduct_stock_no_commit(session, item.product_id, item.quantity)

        order_item = OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price,
        )
        order_items.append(order_item)

    new_order = Order(user_id=user_id, items=order_items)

    session.add(new_order)
    session.commit()
    session.refresh(new_order)

    return new_order


def get_order(session: Session, order_id: int) -> Order | None :
    """
    Retrieve a single order by its id, or None if it doens't exist.
    """
    return session.get(Order, order_id)


def get_orders_by_user(session: Session, user_id: int, skip: int = 0, limit: int = 10) -> list[Order]:
    """
    Retrieve a paginated list of orders belonging to a given user.
    """
    statement = (
        select(Order)
        .where(Order.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_order_status(session: Session, order_id: int, new_status: OrderStatus) -> Order:
    """
    Update the status of an existing order.
    """
    order = get_order(session, order_id)

    if order is None: 
        raise ValueError(f"Order {order_id} not found.")

    order.status = new_status

    session.add(order)
    session.commit()
    session.refresh(order)

    return order