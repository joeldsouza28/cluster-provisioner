import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    github_client_id: str = ""
    github_client_secret: str = ""
    # Current environment
    environment: str = "dev"

    db_url: str = ""

    log_level: LogLevel = LogLevel.INFO


settings = Settings()
