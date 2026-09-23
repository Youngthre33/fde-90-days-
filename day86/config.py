from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TICKET_",
        env_file="day86/.env",
        env_file_encoding="utf-8",
    )

    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
    )

    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
    ] = "info"


settings = Settings()
