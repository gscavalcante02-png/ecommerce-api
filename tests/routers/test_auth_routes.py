from faker import Faker
from fastapi import status 

from crud.user_crud import create_user
from schemas.user import UserCreate

fake = Faker()

def test_login_success(client, session):

    raw_password = fake.password()
    user_data = UserCreate(
        name=fake.name(),
        email=fake.email(),
        password=raw_password,
    )
    created_user = create_user(session, user_data)

    login_data = {
        "username": created_user.email,
        "password": raw_password,
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, session):
    user_data = UserCreate(
        name=fake.name(),
        email=fake.email(),
        password=fake.password(),
    )
    created_user = create_user(session, user_data)

    login_data = {
        "username": created_user.email,
        "password": "wrong_password_123",
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect e-mail or password."