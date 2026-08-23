from faker import Faker 

from models.product import Category
from schemas.category import CategoryCreate
from crud.category_crud import (create_category,
    get_category,
    get_categories
)

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