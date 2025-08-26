import pathlib
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.internal.auth.login_types import LoginTypeEnum


class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class PostgreSQLSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    database: str = "audiobookrequest"
    
    def get_database_url(self) -> str:
        """Generate PostgreSQL database URL."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class DBSettings(BaseModel):
    type: DatabaseType = DatabaseType.SQLITE
    """Database type to use (sqlite or postgresql)."""
    
    sqlite_path: str = "db.sqlite"
    """Relative path to the sqlite database given the config directory. If absolute, it ignores the config dir location."""
    
    postgresql: PostgreSQLSettings = Field(default_factory=PostgreSQLSettings)
    """PostgreSQL configuration settings."""


class ApplicationSettings(BaseModel):
    debug: bool = False
    openapi_enabled: bool = False
    config_dir: str = "/config"
    port: int = 8000
    version: str = "local"
    log_level: str = "INFO"
    base_url: str = ""

    default_region: str = "us"
    """Default region used in the search"""

    force_login_type: str = ""
    """Forces the login type used. If set, the login type cannot be changed in the UI."""

    init_root_username: str = ""
    init_root_password: str = ""

    def get_force_login_type(self) -> Optional[LoginTypeEnum]:
        if self.force_login_type.strip():
            try:
                login_type = LoginTypeEnum(self.force_login_type.strip().lower())
                if login_type == LoginTypeEnum.api_key:
                    raise ValueError(
                        "API key login type is not supported for forced login type."
                    )
                return login_type
            except ValueError:
                raise ValueError(f"Invalid force login type: {self.force_login_type}")
        return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ABR_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        env_file=(".env.local", ".env"),
    )

    db: DBSettings = DBSettings()
    app: ApplicationSettings = ApplicationSettings()

    def get_sqlite_path(self) -> str:
        """Get the full path to the SQLite database file."""
        if self.db.sqlite_path.startswith("/"):
            return self.db.sqlite_path
        return str(pathlib.Path(self.app.config_dir) / self.db.sqlite_path)
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on the database type."""
        if self.db.type == DatabaseType.POSTGRESQL:
            return self.db.postgresql.get_database_url()
        else:
            sqlite_path = self.get_sqlite_path()
            return f"sqlite+pysqlite:///{sqlite_path}"
