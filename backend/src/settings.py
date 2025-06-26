import sys
from enum import Enum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve()


class APISettings(BaseModel):
    title: str = 'Numismatist'
    description: str = 'API for numismatist backend'
    version: str = '0.0.1'
    port: Annotated[int, Field(default=8000, ge=1, le=65535)]
    cors_origins: Annotated[list[str], Field(default=['*'])]


class DatabaseSettings(BaseModel):
    host: str
    port: Annotated[int, Field(ge=1, le=65535)]
    user: str
    password: str
    name: str
    debug: bool = False
    pool_size: Annotated[int, Field(default=100, gt=0)]
    max_overflow: Annotated[int, Field(default=50, ge=0)]

    @property
    def dsn(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class AccessTokenSettings(BaseModel):
    lifetime_seconds: Annotated[int, Field(default=3600, ge=300, le=86400)]  # must be 5 min - 24 hours
    reset_password_token_secret: str
    verification_token_secret: str


class LogLevel(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'


class LoggerSettings(BaseModel):
    level: LogLevel = LogLevel.DEBUG


class Settings(BaseSettings):
    access_token: AccessTokenSettings
    api: APISettings = APISettings()
    database: DatabaseSettings
    logger: LoggerSettings = LoggerSettings()

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / '.env',), env_nested_delimiter='__', env_prefix='', case_sensitive=False
    )


try:
    settings = Settings()
except Exception as e:
    if isinstance(e, ValidationError):
        for err in e.errors():
            loc = '.'.join(str(p) for p in err['loc'])
            msg = err['msg']
            print(f'Missing or invalid setting: {loc} → {msg}', file=sys.stderr)
    else:
        print(f'Configuration error: {e}', file=sys.stderr)

    sys.exit(1)