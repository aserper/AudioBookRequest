from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlmodel import Session, text

from app.internal.env_settings import Settings, DatabaseType


def create_database_engine() -> Engine:
    """Create database engine based on configuration."""
    settings = Settings()
    database_url = settings.get_database_url()
    
    if settings.db.type == DatabaseType.POSTGRESQL:
        # PostgreSQL-specific engine configuration
        return create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    else:
        # SQLite-specific engine configuration
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )


# Initialize the global engine
engine = create_database_engine()


def get_session() -> Generator[Session, None, None]:
    """Get a database session with appropriate configuration for the database type."""
    settings = Settings()
    
    with Session(engine) as session:
        if settings.db.type == DatabaseType.SQLITE:
            # Enable foreign keys for SQLite
            session.execute(text("PRAGMA foreign_keys=ON"))  # pyright: ignore[reportDeprecated]
        yield session


# TODO: couldn't get a single function to work with FastAPI and allow for session creation wherever
@contextmanager
def open_session() -> Generator[Session, None, None]:
    """Open a database session with appropriate configuration for the database type."""
    settings = Settings()
    
    with Session(engine) as session:
        if settings.db.type == DatabaseType.SQLITE:
            # Enable foreign keys for SQLite
            session.execute(text("PRAGMA foreign_keys=ON"))  # pyright: ignore[reportDeprecated]
        yield session
