from faker import Faker

from models.product import Product
from crud.category_crud import create_category
from crud.product_crud import (
    create_product,
    get_product,
    get_all_products,
    deduct_stock,
    delete_product,
    get_products_by_category,
    update_product
)
from schemas.category import CategoryCreate
from schemas.product import ProductCreate, ProductUpdate

fake = Faker()


def test_create_product(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    fake_name = fake.word()
    fake_price = fake.pyfloat()
    fake_stock = fake.random_int()
    product_data = ProductCreate(
        name=fake_name,
        price=fake_price,
        stock=fake_stock,
        category_ids=[created_category.id],
    )
    created_product = create_product(session, product_data)

    assert created_product.id is not None
    assert created_product.name == fake_name
    assert created_product.price == fake_price
    assert created_product.stock == fake_stock
    assert len(created_product.categories) == 1
    assert created_product.categories[0].id == created_category.id


def test_get_product(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)
    
    fake_name = fake.word()
    fake_price = fake.pyfloat(positive=True )
    fake_stock = fake.random_int()
    product_data = ProductCreate(
        name=fake_name,
        price=fake_price,
        stock=fake_stock,
        category_ids=[created_category.id],
    )
    created_product = create_product(session, product_data)

    found_product = get_product(session, created_product.id)

    assert found_product is not None
    assert found_product.id == created_product.id
    assert found_product.name == fake_name
    assert found_product.price == fake_price
    assert found_product.stock == fake_stock
    assert len(found_product.categories) == 1


def test_get_all_products(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)
    
    for _ in range(5):
        product_data = ProductCreate(
            name=fake.word(),
            price=fake.pyfloat(positive=True),
            stock=fake.random_int(),
            category_ids=[created_category.id],
        )
        create_product(session, product_data)

    first_page = get_all_products(session, skip=0, limit=3)
    second_page = get_all_products(session, skip=3, limit=3)

    assert len(first_page) == 3
    assert len(second_page) == 2


def test_deduct_stock_success(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    product_data = ProductCreate(
            name=fake.word(),
            price=fake.pyfloat(positive=True),
            stock=10,
            category_ids=[created_category.id],
        )

    created_product = create_product(session, product_data)

    result = deduct_stock(session, created_product.id, 3)

    assert result is True
    updated_product = get_product(session, created_product.id)
    assert updated_product.stock == 7
    assert updated_product.stock == 7

def test_deduct_stock_insufficient(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    product_data = ProductCreate(
        name=fake.word(), price=fake.pyfloat(positive=True), stock=10,
        category_ids=[created_category.id],
    )
    created_product = create_product(session, product_data)

    result = deduct_stock(session, created_product.id, 15)

    assert result is False
    unchanged_product = get_product(session, created_product.id)
    assert unchanged_product.stock == 10


def test_delete_product(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    product_data = ProductCreate(
        name=fake.word(), price=fake.pyfloat(positive=True), stock=fake.random_int(),
        category_ids=[created_category.id],
    )

    created_product = create_product(session, product_data)

    result = delete_product(session, created_product)

    assert result is True
    deleted_product = get_product(session, created_product.id)
    assert deleted_product is None


def test_get_products_by_category(session):
    category_a_data = CategoryCreate(name="Category A")
    category_b_data = CategoryCreate(name="Category B")

    category_a = create_category(session, category_a_data)
    category_b = create_category(session, category_b_data)

    for _ in range(3):
        product_data = ProductCreate(
            name=fake.word(),
            price=fake.pyfloat(positive=True),
            stock=fake.random_int(),
            category_ids=[category_a.id],
        )
        create_product(session, product_data)

    for _ in range(2):
        product_data = ProductCreate(
            name=fake.word(),
            price=fake.pyfloat(positive=True),
            stock=fake.random_int(),
            category_ids=[category_b.id],
        )
        create_product(session, product_data)

    result = get_products_by_category(session, category_a.id)

    assert len(result) == 3
    for product in result:
        assert category_a in product.categories
        assert category_b not in product.categories


def test_update_product(session):
    category_data = CategoryCreate(name=fake.word())
    created_category = create_category(session, category_data)

    product_data = ProductCreate(
        name=fake.word(), price=fake.pyfloat(positive=True), stock=fake.random_int(),
        category_ids=[created_category.id],
    )
    created_product = create_product(session, product_data)

    new_price = fake.pyfloat(positive=True)
    update_data = ProductUpdate(price=new_price)

    updated_data = update_product(session, created_product.id, update_data)

    assert updated_data.name == product_data.name
    assert updated_data.price == new_price
    assert updated_data.stock == product_data.stock