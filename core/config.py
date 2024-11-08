import secrets

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)

settings = Settings()  # type: ignore