import pathlib
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from app.internal import models
from app.internal.env_settings import Settings, DatabaseType

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger(__name__)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = models.BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_engine():
    """Create database engine using the settings configuration."""
    try:
        settings = Settings()
        database_url = settings.get_database_url()
        
        # Override the URL in the alembic config for consistency
        config.set_main_option("sqlalchemy.url", database_url)
        
        if settings.db.type == DatabaseType.POSTGRESQL:
            # PostgreSQL-specific engine configuration for migrations
            logger.info("Configuring PostgreSQL engine for migrations")
            return create_engine(
                database_url,
                poolclass=pool.NullPool,  # Use NullPool for migrations to avoid connection issues
                echo=False,
            )
        else:
            # SQLite-specific engine configuration for migrations
            logger.info("Configuring SQLite engine for migrations")
            # Ensure SQLite directory exists
            sqlite_path = settings.get_sqlite_path()
            pathlib.Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
            
            return create_engine(
                database_url,
                poolclass=pool.NullPool,  # Use NullPool for migrations to avoid connection issues
                connect_args={"check_same_thread": False},
                echo=False,
            )
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def run_migrations() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    try:
        settings = Settings()
        engine = get_database_engine()
        
        with engine.connect() as connection:
            # Configure context based on database type
            context_config = {
                "connection": connection,
                "target_metadata": target_metadata,
            }
            
            # SQLite needs batch mode for ALTER operations
            if settings.db.type == DatabaseType.SQLITE:
                context_config["render_as_batch"] = True
                logger.info("Running migrations with SQLite batch mode")
            else:
                logger.info("Running migrations for PostgreSQL")
            
            context.configure(**context_config)

            with context.begin_transaction():
                context.run_migrations()
        
        logger.info("Migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


run_migrations()
