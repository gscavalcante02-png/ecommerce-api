from faker import Faker
from fastapi import status

from crud.user_crud import create_user 
from crud.category_crud import create_category
from crud.product_crud import create_product
from models.user import Role
from schemas.user import UserCreate
from schemas.category import CategoryCreate
from schemas.product import ProductCreate

fake = Faker()


def test_list_products_public(client, session):
    category = create_category(session, CategoryCreate(name=fake.word()))
    create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=50.0,
            stock=10,
            category_ids=[category.id],
        ),
    )

    response = client.get("/products")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_create_product_as_admin(client, session):
    password = fake.password()
    admin = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.admin),
    )
    category = create_category(session, CategoryCreate(name=fake.word()))

    login_res = client.post(
        "/auth/login",
        data={"username": admin.email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": fake.word(),
        "price": 99.99,
        "stock": 20,
        "category_ids": [category.id],
    }
    response = client.post("/products/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert len(data["categories"]) == 1


def test_create_product_forbidden_for_common_user(client, session):
    password = fake.password()
    common_user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.user),
    )
    category = create_category(session, CategoryCreate(name=fake.word()))

    login_res = client.post(
        "/auth/login",
        data={"username": common_user.email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": fake.word(),
        "price": 49.99,
        "stock": 10,
        "category_ids": [category.id],
    }
    response = client.post("/products/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_product_by_id_success(client, session): 
    category = create_category(session, CategoryCreate(name=fake.word()))
    product = create_product(
        session,
        ProductCreate(
            name=fake.word(),
            price=25.0,
            stock=5,
            category_ids=[category.id],
        ),
    )

    response = client.get(f"/products/{product.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == product.id
    assert response.json()["name"] == product.name


def test_product_not_found(client):
    response = client.get("/products/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found."