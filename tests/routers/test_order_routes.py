from faker import Faker
from fastapi import status

from crud.order_crud import create_order
from crud.user_crud import create_user
from crud.category_crud import create_category
from crud.product_crud import create_product
from models.user import Role
from models.order import OrderStatus
from schemas.order import OrderCreate, OrderItemCreate
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


def test_get_order_by_id_success(client, session):
    """A user can retrieve their own order by ID."""
    password = fake.password()
    user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.user),
    )
    category = create_category(session, CategoryCreate(name=fake.word()))
    product = create_product(
        session,
        ProductCreate(name=fake.word(), price=20.0, stock=10, category_ids=[category.id]),
    )

    # Create the order directly through the CRUD layer
    order = create_order(
        session,
        OrderCreate(items=[OrderItemCreate(product_id=product.id, quantity=2)]),
        user_id=user.id,
    )

    login_res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/orders/{order.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == order.id
    assert data["status"] == OrderStatus.PENDING
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product.id
    assert data["items"][0]["quantity"] == 2


def test_get_order_forbidden_for_other_user(client, session):
    """A user must not be able to view another user's order."""
    owner = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=fake.password(), role=Role.user),
    )
    other_password = fake.password()
    other_user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=other_password, role=Role.user),
    )
    category = create_category(session, CategoryCreate(name=fake.word()))
    product = create_product(
        session,
        ProductCreate(name=fake.word(), price=20.0, stock=10, category_ids=[category.id]),
    )
    order = create_order(
        session,
        OrderCreate(items=[OrderItemCreate(product_id=product.id, quantity=1)]),
        user_id=owner.id,
    )

    login_res = client.post(
        "/auth/login",
        data={"username": other_user.email, "password": other_password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/orders/{order.id}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to view this order."


def test_get_order_not_found(client, session):
    """Requesting an order that does not exist returns 404."""
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

    response = client.get("/orders/999", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Order not found."