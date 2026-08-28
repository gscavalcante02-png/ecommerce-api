
from sqlmodel import Session, select

from schemas.user import UserCreate
from models.user import User

from core.security import hash_password


def create_user(session: Session, user_data: UserCreate) -> User:
    """
    Create a new user, hashing the raw password before persisting it.
    """
    user_dict = user_data.model_dump()

    raw_password = user_dict.pop("password")
    user_dict["hashed_password"] = hash_password(raw_password)

    db_user = User(**user_dict)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user


def get_user_by_id(session: Session, user_id: int) -> User | None:
    """
    Retrieve a single user by their unique ID.
    """
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Retrieve a single user by their email address.
    """
    # SQL: SELECT * FROM user WHERE email = email
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Retrieve a list of users with pagination support.
    """
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_user(session: Session, db_user: User, user_data: dict) -> User | None:
    """
    Fetches the user by ID and updates its attributes if found.
    """
    for key, value in user_data.items():
        if value is not None:
            setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(session: Session, db_user: User) -> bool:
    """
    Fetches the user by ID and deletes it if found.
    """
    session.delete(db_user)
    session.commit()
    return True
