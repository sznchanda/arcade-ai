import os

from functools import lru_cache
from typing import Literal

from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



# https://docs.pydantic.dev/latest/concepts/pydantic_settings/
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    WORK_DIR: Path = Path.home() / '.darkstar'
    TOOLS_DIR: Path = os.getcwd()

    # Env Config
    ENVIRONMENT: Literal['dev', 'pro'] = 'dev'

    # Env Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DATABASE: int = 0

    # Env Token
    TOKEN_SECRET_KEY: str  # 密钥 secrets.token_urlsafe(32)

    # Env Opera Log
    OPERA_LOG_ENCRYPT_SECRET_KEY: str  # 密钥 os.urandom(32), 需使用 bytes.hex() 方法转换为 str

    # FastAPI
    API_V1_STR: str = '/api/v1'
    API_ACTION_STR: str = '/action'
    TITLE: str = 'Darkstar Toolserver'
    VERSION: str = '0.1.0'
    DESCRIPTION: str = 'Darkstar Toolserver API'
    DOCS_URL: str | None = f'{API_V1_STR}/docs'
    REDOCS_URL: str | None = f'{API_V1_STR}/redocs'
    OPENAPI_URL: str | None = f'{API_V1_STR}/openapi'

#    @model_validator(mode='before')
#    @classmethod
#    def validate_openapi_url(cls, values):
#        if values['ENVIRONMENT'] == 'pro':
#            values['OPENAPI_URL'] = None
#        return values

    # Uvicorn
    UVICORN_HOST: str = '127.0.0.1'
    UVICORN_PORT: int = 8000
    UVICORN_RELOAD: bool = True

    # Static Server
    STATIC_FILES: bool = False

    # DateTime
    DATETIME_TIMEZONE: str = 'US/Pacific'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Redis
    REDIS_TIMEOUT: int = 5

    # Token
    TOKEN_ALGORITHM: str = 'HS256'  # 算法
    TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # 过期时间，单位：秒
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 刷新过期时间，单位：秒
    TOKEN_URL_SWAGGER: str = f'{API_V1_STR}/auth/swagger_login'
    TOKEN_REDIS_PREFIX: str = 'ts_token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'ts_refresh_token'
    TOKEN_EXCLUDE: list[str] = [  # JWT / RBAC 白名单
        f'{API_V1_STR}/auth/login',
    ]

    # Log
    LOG_STDOUT_FILENAME: str = 'ts_access.log'
    LOG_STDERR_FILENAME: str = 'ts_error.log'

    # Middleware
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_GZIP: bool = True
    MIDDLEWARE_ACCESS: bool = False

    # these should be set in .env
    TOKEN_SECRET_KEY: str = "secret"
    OPERA_LOG_ENCRYPT_SECRET_KEY: str = "secret"



@lru_cache
def get_settings():
    try:
        env_path = Path(os.environ["TOOLSERVE_ENV"])
    except KeyError:
        env_path = Path(__file__).parent.parent / '.env'
    return Settings(_env_file=env_path)

settings = get_settings()
