from faker import Faker
from fastapi import status

from crud.user_crud import create_user
from crud.category_crud import create_category
from crud.product_crud import create_product
from models.user import Role
from models.order import OrderStatus
from schemas.user import UserCreate
from schemas.category import CategoryCreate
from schemas.product import ProductCreate

fake = Faker()

def test_create_order_success(client, session):
    password = fake.password()
    user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.user),
    )
    category = create_category(session, CategoryCreate(name=fake.word())) 
    product = create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=30.0,
            stock=10,
            category_ids=[category.id],
        ),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "items": [
            {"product_id": product.id, "quantity": 2}
        ]
    }
    response = client.post("/orders/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == OrderStatus.PENDING
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product.id
    assert data["items"][0]["quantity"] == 2


def test_create_order_insufficient_stock(client, session):
    password = fake.password()
    user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.user),
    )
    category = create_category(session, CategoryCreate(name=fake.word()))
    product = create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=15.0,
            stock=1,
            category_ids=[category.id],
        ),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "items": [
            {"product_id": product.id, "quantity": 5}
        ]
    }
    response = client.post("/orders/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient stock" in response.json()["detail"]


def test_list_user_orders(client, session):
    password = fake.password()
    user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.user),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/orders/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_update_order_status_as_admin(client, session):
    admin_pass = fake.word()
    admin = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=admin_pass, role=Role.admin),
    )
    customer = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=fake.password(), role=Role.user),
    )
    category = create_category(session, CategoryCreate(name=fake.word()))
    product = create_product(
        session,
        ProductCreate(name=fake.word(), price=10.0, stock=10, category_ids=[category.id]),
    )

    from crud.order_crud import create_order
    from schemas.order import OrderCreate, OrderItemCreate
    order = create_order(
        session,
        OrderCreate(items=[OrderItemCreate(product_id=product.id, quantity=1)]),
        user_id=customer.id
    )

    login_res = client.post(
        "/auth/login",
        data={"username": admin.email, "password": admin_pass},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        f"/orders/{order.id}/status",
        json={"status": "completed"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "completed"