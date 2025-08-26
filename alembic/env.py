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
# PostgreSQL Compatibility Note:
# All migration files have been updated to use sa.String() instead of 
# sqlmodel.sql.sqltypes.AutoString() to ensure consistent column types
# between SQLite and PostgreSQL deployments. This prevents foreign key
# constraint issues where columns might be interpreted as different types
# (e.g., VARCHAR vs BYTEA) in different database contexts.
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
            logger.info(f"PostgreSQL connection: {settings.db.postgresql.host}:{settings.db.postgresql.port}/{settings.db.postgresql.database}")
            
            return create_engine(
                database_url,
                poolclass=pool.NullPool,  # Use NullPool for migrations to avoid connection issues
                echo=False,
                # PostgreSQL-specific connection arguments
                connect_args={
                    "options": "-c timezone=utc",  # Set timezone for consistency
                    "application_name": "AudioBookRequest-Migration",
                }
            )
        else:
            # SQLite-specific engine configuration for migrations
            logger.info("Configuring SQLite engine for migrations")
            # Ensure SQLite directory exists
            sqlite_path = settings.get_sqlite_path()
            pathlib.Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"SQLite database path: {sqlite_path}")
            
            return create_engine(
                database_url,
                poolclass=pool.NullPool,  # Use NullPool for migrations to avoid connection issues
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20,  # Increase timeout for migrations
                },
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
        
        # Test database connection before proceeding
        logger.info("Testing database connection...")
        with engine.connect() as test_conn:
            if settings.db.type == DatabaseType.POSTGRESQL:
                # Verify PostgreSQL connection and version
                result = test_conn.execute("SELECT version()")
                version_info = result.fetchone()[0]
                logger.info(f"PostgreSQL version: {version_info}")
            else:
                # Verify SQLite connection
                result = test_conn.execute("SELECT sqlite_version()")
                version_info = result.fetchone()[0]
                logger.info(f"SQLite version: {version_info}")
        
        logger.info("Database connection successful, proceeding with migrations...")
        
        with engine.connect() as connection:
            # Configure context based on database type
            context_config = {
                "connection": connection,
                "target_metadata": target_metadata,
            }
            
            # Database-specific configuration
            if settings.db.type == DatabaseType.SQLITE:
                context_config["render_as_batch"] = True
                logger.info("Running migrations with SQLite batch mode")
            else:
                logger.info("Running migrations for PostgreSQL with standard mode")
                # PostgreSQL-specific settings
                context_config["compare_type"] = True  # Enable type comparison for PostgreSQL
                context_config["compare_server_default"] = True  # Compare server defaults
            
            context.configure(**context_config)

            with context.begin_transaction():
                context.run_migrations()
        
        logger.info("All migrations completed successfully")
        
    except ImportError as e:
        if "psycopg2" in str(e):
            logger.error("PostgreSQL dependencies not installed. Run: uv sync --group postgresql")
            logger.error("Or ensure psycopg2-binary is installed for PostgreSQL support")
        else:
            logger.error(f"Import error during migration: {e}")
        raise
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        # Provide specific troubleshooting for common PostgreSQL issues
        if "could not connect to server" in str(e).lower():
            logger.error("PostgreSQL connection failed. Check that PostgreSQL server is running and connection settings are correct.")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            logger.error("Database does not exist. Create the database first or check database configuration.")
        elif "foreign key constraint" in str(e).lower():
            logger.error("Foreign key constraint issue. This may indicate a migration compatibility problem.")
            if "incompatible types" in str(e).lower():
                logger.error("HINT: This error often occurs when column types don't match between referenced tables.")
                logger.error("Check that both the referencing and referenced columns use compatible data types.")
                logger.error("For PostgreSQL, ensure string columns use consistent types (VARCHAR, not mixed with BYTEA).")
        elif "column" in str(e).lower() and "does not exist" in str(e).lower():
            logger.error("Column does not exist error. The migration may be trying to reference a non-existent column.")
            logger.error("This could indicate that migrations are being applied out of order or a previous migration failed.")
        raise


run_migrations()
