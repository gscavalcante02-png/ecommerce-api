from faker import Faker

from crud.user_crud import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
)
from models.user import User
from schemas.user import UserCreate


fake = Faker()

def test_create_and_get_user(session):
    fake_name = fake.name()
    fake_email = fake.email()
    fake_password = fake.password()

    user_data = UserCreate(
        name=fake_name,
        email=fake_email,
        password=fake_password,
    )

    created = create_user(session, user_data)

    assert created.id is not None
    assert created.email == fake_email

    found_by_email = get_user_by_email(session, fake_email)
    assert found_by_email is not None
    assert found_by_email.id == created.id


def test_update_user(session):

    user_data = UserCreate(
        name=fake.name(),
        email=fake.email(),
        password=fake.password(),
    )
    db_user = create_user(session, user_data)

    new_name = fake.name()
    update_data = {"name": new_name}
    updated_user = update_user(session, db_user, update_data)

    assert updated_user.name == new_name


def test_delete_user(session):

    user_data = UserCreate(
        name=fake.name(),
        email=fake.email(),
        password=fake.password(),
    )
    db_user = create_user(session, user_data)

    delete_user(session, db_user)

    assert get_user_by_id(session, db_user.id) is None
