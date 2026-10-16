from faker import Faker
from fastapi import status 

from crud.user_crud import create_user
from crud.category_crud import create_category
from models.user import Role
from schemas.user import UserCreate
from schemas.category import CategoryCreate

fake = Faker()


def test_create_category_as_admin(client, session):
    password = fake.password()
    admin = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.admin),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": admin.email, "password": password},
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": fake.word()}
    response = client.post("/categories/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data


def test_create_category_forbidden_for_common_user(client, session):
    password = fake.password()
    common_user = create_user(
        session,
        UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=password,
            role=Role.user,
        )
    )

    login_res = client.post("/auth/login", data={
        "username": common_user.email,
        "password": password,
    })
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": fake.word()}
    response = client.post("/categories/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_category_by_id_success(client, session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    response = client.get(f"/categories/{created_category.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == created_category.id     
    assert response.json()["name"] == created_category.name


def test_category_by_id_not_found(client):
    response = client.get("/categories/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category not found."