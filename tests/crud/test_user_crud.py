from models.user import User
from crud.user_crud import (create_user, 
    get_user_by_email, 
    get_user_by_id,
    update_user,
    delete_user
)

def test_create_and_get_user(session):

    new_user = User(
        name="Teste Silva",
        email="teste@email.com",
        hashed_password="senha_criptografada_mock"
    )

    created = create_user(session, new_user)

    assert created.id is not None
    assert created.email == "teste@email.com"

    found_by_email = get_user_by_email(session, "teste@email.com")
    assert found_by_email is not None
    assert found_by_email.id == created.id


def test_update_user(session):

    user = User(name="Nome Antigo", email="update@email.com", hashed_password="123")
    db_user = create_user(session, user)

    update_data = {"name": "Nome Novo"}
    updated_user = update_user(session, db_user, update_data)

    assert updated_user.name == "Nome Novo"


def test_delete_user(session):

    user = User(name="Para Deletar", email="delete@email.com", hashed_password="123")
    db_user = create_user(session, user)

    delete_user(session, db_user)

    assert  get_user_by_id(session, db_user.id) is None