from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# Import settings from core.config
from core.config import settings

# Create the SQLModel engine using the property from settings
engine = create_engine(settings.database_url, echo=True)


def init_db() -> None:
    """Import all models so SQLModel registers them before creating tables in PostgreSQL."""

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency function to yield database sessions per request."""
    with Session(engine) as session:
        yield session
