import pytest

from faker import Faker

from crud.category_crud import (
    create_category,
    get_categories, 
    get_category, 
    get_category_by_name
)
from schemas.category import CategoryCreate

fake = Faker()


def test_create_category(session):
    fake_name = fake.word()
    category_data = CategoryCreate(name=fake_name)

    created_category = create_category(session, category_data)

    assert created_category.id is not None
    assert created_category.name == fake_name


def test_get_category(session):
    fake_name = fake.word()
    category_data = CategoryCreate(name=fake_name)

    created_category = create_category(session, category_data)

    found_category = get_category(session, created_category.id)

    assert found_category is not None
    assert found_category.id == created_category.id
    assert found_category.name == fake_name


def test_get_categories(session):
    for _ in range(5):
        category_data = CategoryCreate(name=fake.word())
        create_category(session, category_data)

    first_page = get_categories(session, skip=0, limit=3)
    second_page = get_categories(session, skip=3, limit=3)

    assert len(first_page) == 3
    assert len(second_page) == 2


def test_get_category_by_name_sucsess(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    found_category = get_category_by_name(session, category_data.name)    

    assert found_category.id == created_category.id
    assert found_category.name == created_category.name


def test_get_category_by_name_not_found(session):
    non_existent_name = fake.word()

    with pytest.raises(ValueError) as exc_info:
        get_category_by_name(session, non_existent_name)

    assert f"Category '{non_existent_name}' not found." in str(exc_info.value)