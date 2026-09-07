from faker import Faker
from fastapi import status

from crud.user_crud import create_user
from models.user import Role
from schemas.user import UserCreate

fake = Faker()

def test_register_user_public(client):
    payload = {
        "name": fake.name(),
        "email": fake.email(),
        "password": fake.password(),
    }
    response = client.post("/users/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


def test_register_duplicate_email(client):
    duplicate_email = fake.email()
    payload1 = {
        "name": fake.name(),
        "email": duplicate_email,
        "password": fake.password(),
    }
    client.post("/users/", json=payload1)

    payload2 = {
        "name": fake.name(),
        "email": duplicate_email,
        "password": fake.password(),
    }
    response = client.post("/users/", json=payload2)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered."


def test_admin_route_forbidden_for_common_user(client, session):

    password = fake.password()
    common_user  = create_user(
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
    response = client.get("/users/", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_route_success_for_admin(client, session):

    password = fake.password()
    admin_user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.admin),
    )

    login_res = client.post("/auth/login", data={"username": admin_user.email, "password": password})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_current_user_success(client, session):
    password = fake.password()
    user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user.email
    assert data["id"] == user.id


def test_get_user_by_id_as_admin(client, session):
    password = fake.password()
    admin = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.admin),
    )
    target_user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=fake.password()),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": admin.email, "password": password},
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/users/{target_user.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == target_user.id


def test_list_users_as_admin(client, session):

    admin_pass = fake.password()
    admin = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=admin_pass, role=Role.admin),
    )

    user1 = create_user(session, UserCreate(name=fake.name(), email=fake.email(), password=fake.password()))
    user2 = create_user(session, UserCreate(name=fake.name(), email=fake.email(), password=fake.password()))

    login_res = client.post(
        "/auth/login",
        data={"username": admin.email, "password": admin_pass},
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3


def test_update_user_by_id_as_admin(client, session):
    password = fake.password()
    admin = create_user(
        session, 
        UserCreate(name=fake.name(), email=fake.email(), password=password, role=Role.admin),
    )
    target_user = create_user(
        session,
        UserCreate(name=fake.name(), email=fake.email(), password=fake.password()),
    )

    login_res = client.post(
        "/auth/login",
        data={"username": admin.email, "password": password},
    )
    token = login_res.json()["access_token"]

    new_name = fake.name()
    update_payload = {"name": new_name}

    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch(
        f"/users/{target_user.id}",
        json=update_payload,
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == new_name