from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from functools import lru_cache
from typing import (
    Literal,
    Union,
)


class Settings(BaseSettings):
    app_name: str = "Library Catalog API"
    environment: Literal["development", "staging", "production"]
    debug: bool
    database_url: Union[PostgresDsn, str]
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
