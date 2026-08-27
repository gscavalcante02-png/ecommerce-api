import pytest 
from faker import Faker

from crud.category_crud import create_category
from crud.product_crud import create_product
from crud.user_crud import create_user
from crud.order_crud import (
    create_order,
    get_order,
    get_orders_by_user,
    update_order_status
)
from models.user import User
from models.order import OrderStatus
from schemas.category import CategoryCreate
from schemas.order import OrderCreate, OrderItemCreate
from schemas.product import ProductCreate
from schemas.user import UserCreate


fake = Faker()


def test_create_order(session):
    """
    
    """
    user = create_user(
        session,
        UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )
    )
    category =create_category(session, CategoryCreate(name=fake.word()))

    product = create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=10.0,
            stock=15,
            category_ids=[category.id],
        )
    )

    order_data = OrderCreate(
        items=[OrderItemCreate(product_id=product.id, quantity=5)]
    )

    created_order = create_order(session, order_data, user_id=user.id)

    assert created_order.id is not None
    assert created_order.user_id == user.id
    assert len(created_order.items) == 1
    assert created_order.items[0].product_id == product.id
    assert created_order.items[0].quantity == 5
    assert created_order.items[0].price_at_purchase == 10.0

    session.refresh(product)
    assert product.stock == 10


def test_create_order_insufficient_stock(session):
    user = create_user(
        session,
        UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )
    )
    category =create_category(session, CategoryCreate(name=fake.word()))

    product = create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=10.0,
            stock=2,
            category_ids=[category.id],
        )
    )


    order_data = OrderCreate(
        items=[OrderItemCreate(product_id=product.id, quantity=5)]
    )

    with pytest.raises(ValueError) as exc_info:
        create_order(session, order_data, user_id=user.id)

    assert f"Insufficient stock for product '{product.name}'" in str(exc_info.value)


def test_get_order_returns_none_if_not_found(session):
    result = get_order(session, order_id=9999)

    assert result is None


def test_update_order_status_success(session):
    user = create_user(
        session,
        UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )
    )
    category =create_category(session, CategoryCreate(name=fake.word()))

    product = create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=10.0,
            stock=15,
            category_ids=[category.id],
        )
    )
    order_data = OrderCreate(
        items=[OrderItemCreate(product_id=product.id, quantity=2)]
    )

    order = create_order(session, order_data, user_id=user.id)

    assert order.status == OrderStatus.PENDING

    updated_order = update_order_status(
        session,
        order_id=order.id,
        new_status=OrderStatus.COMPLETED
    )

    session.refresh(order)

    assert updated_order.status == OrderStatus.COMPLETED
    assert order.status == OrderStatus.COMPLETED


def test_update_order_status_not_found(session):
    with pytest.raises(ValueError, match="Order 9999 not found."):
        update_order_status(
            session,
            order_id=9999,
            new_status=OrderStatus.CANCELED
        )
