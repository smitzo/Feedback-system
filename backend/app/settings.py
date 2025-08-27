from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEEDBACK_", env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./feedback.db"
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    secure_cookies: bool = False
    session_seconds: int = Field(default=28800, ge=300, le=86400)
    aggregate_minimum: int = Field(default=3, ge=3, le=100)
    login_attempts: int = Field(default=8, ge=3, le=50)
    login_window_seconds: int = Field(default=900, ge=60, le=3600)

    @model_validator(mode="after")
    def production_safety(self):
        if self.environment == "production":
            if not self.secure_cookies:
                raise ValueError("Production requires secure cookies")
            if not self.allowed_origins or any(
                not x.startswith("https://") for x in self.allowed_origins
            ):
                raise ValueError("Production requires explicit HTTPS origins")
            if self.database_url.endswith(":memory:"):
                raise ValueError("Production requires durable database storage")
        if any(x == "*" or x.endswith("/") for x in self.allowed_origins):
            raise ValueError("Origins must be explicit and have no trailing slash")
        return self
