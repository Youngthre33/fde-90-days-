from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TICKET_",
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
    )

    port: int = Field(
        default=8001,
        ge=1,
        le=65535,
    )

    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
    ] = "info"

    db_host: str = "127.0.0.1"
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str = "ticket_app"
    db_user: str = "postgres"
    db_password: str = Field(default="", repr=False)
    staff_token: str = Field(default="", repr=False)
    admin_token: str = Field(default="", repr=False)

settings = Settings()
