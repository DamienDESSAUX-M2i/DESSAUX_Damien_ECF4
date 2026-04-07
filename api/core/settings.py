from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_name: str = "fake_or_real_news_predictor"
    debug: bool = False
    api_prefix: str = "/api"

    secret_key: str
    algorithm: Literal["HS256"] = "HS256"
    iterations: int = 100_000
    access_token_expire_minutes: int = 60

    database_path: str = "data/db.sqlite"

    vectorizer_path: str = "models/tf_idf_vectorizer.pkl"
    model_path: str = "models/model_dense.keras"
    threshold: float = 0.5

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_path: str = "api/log/api.log"
    log_config_path: str = "api/core/log_config.yaml"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_expire_minutes(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be > 0")
        return v

    @field_validator("iterations")
    @classmethod
    def validate_iterations(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ITERATIONS must be > 0")
        return v

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path}"

    @property
    def log_name(self) -> str:
        return Path(self.log_path).stem


@lru_cache
def get_settings() -> Settings:
    return Settings()
