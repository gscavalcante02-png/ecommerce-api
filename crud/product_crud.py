from sqlmodel import Session, update
from models.product import Product 


def deduct_stock(session: Session, product_id: int, quantity: int) -> bool:
    statement = (
        update(Product)
        .where(Product.id == product_id, Product.stock >= quantity)
        .values(stock=Product.stock - quantity)
    )

    result = session.exec(statement)
    session.commit()

    return result.rowcount > 0