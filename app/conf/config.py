from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    # Project
    VERSION: Optional[str] = '0.1.0'
    DEBUG: Optional[bool] = False
    PAGINATION_MAX_SIZE: Optional[int] = 25

    DOMAIN: Optional[str] = 'localhost:8000'
    ENABLE_SSL: Optional[bool] = False
    SITE_URL: Optional[str] = 'http://localhost'
    ROOT_PATH: Optional[str] = ""
    ROOT_PATH_IN_SERVERS: Optional[bool] = True
    OPENAPI_URL: Optional[str] = '/openapi.json'

    API_V1_STR: Optional[str] = "/api/v1"

    SERVER_NAME: Optional[str] = 'localhost'
    SERVER_HOST: Optional[AnyHttpUrl] = 'http://localhost'
    BACKEND_CORS_ORIGINS: Optional[List[str]] = []

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: Optional[str] = 'project_name'

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    MULTI_TENANCY_DB: Optional[bool] = True
    DATABASE_NAME: Optional[str] = None

    @field_validator("DATABASE_NAME")
    def validate_database_name(cls, v: Optional[str], info):
        data = info.data
        multi_tenancy_db = data.get('MULTI_TENANCY_DB')
        if not multi_tenancy_db and not v:
            raise ValueError("When IS_MULTI_TENANT_DB is false DATABASE_NAME required")

    TEST_DATABASE_NAME: Optional[str] = "test"

    TIME_ZONE: Optional[str] = "Asia/Ashgabat"
    USE_TZ: Optional[bool] = True
    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding='utf-8',
        extra="ignore"
    )


class JWTSettings(BaseSettings):
    # Security
    JWT_SECRET_KEY: Optional[str] = 'change_this'
    # JWT
    JWT_PUBLIC_KEY: Optional[str] = None
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = "HS256"  # "RS256"
    JWT_VERIFY: Optional[bool] = True
    JWT_VERIFY_EXPIRATION: Optional[bool] = True
    JWT_LEEWAY: Optional[int] = 0
    JWT_ARGUMENT_NAME: Optional[str] = 'token'
    JWT_EXPIRATION_MINUTES: Optional[int] = 60 * 24
    JWT_ALLOW_REFRESH: Optional[bool] = True
    JWT_REFRESH_EXPIRATION_MINUTES: Optional[int] = 60 * 24 * 30 * 12
    JWT_AUTH_HEADER_NAME: Optional[str] = 'Authorization'
    JWT_AUTH_COOKIE_NAME: Optional[str] = 'Authorization'
    JWT_GIT_HEADER_NAME: Optional[str] = 'X-IDToken'  # Google id token header name
    JWT_GIT_COOKIE_NAME: Optional[str] = 'X-IDToken'  # Google id token cookie name
    JWT_AUTH_HEADER_PREFIX: str = 'Bearer'
    JWT_AUDIENCE: Optional[str] = 'client'

    # Helper functions
    JWT_PASSWORD_VERIFY: Optional[str] = 'app.utils.security.verify_password'
    JWT_PASSWORD_HANDLER: Optional[str] = 'app.utils.security.get_password_hash'
    JWT_PAYLOAD_HANDLER: Optional[str] = 'app.utils.security.jwt_payload'
    JWT_ENCODE_HANDLER: Optional[str] = 'app.utils.security.jwt_encode'
    JWT_DECODE_HANDLER: Optional[str] = 'app.utils.security.jwt_decode'
    JWT_ISSUER: Optional[str] = 'backend'

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding='utf-8',
        extra="ignore"
    )


class StructureSettings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    MEDIA_DIR: Optional[str] = 'media'  # Without end slash
    MEDIA_URL: Optional[str] = '/media/'

    STATIC_DIR: Optional[str] = 'static'
    STATIC_URL: Optional[str] = '/static/'

    TEMPLATES: Optional[dict] = {
        'DIR': 'templates'
    }

    TEMP_PATH: Optional[str] = 'register-service/'

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding='utf-8',
        extra="ignore"
    )


settings = Settings()
jwt_settings = JWTSettings()
structure_settings = StructureSettings()
