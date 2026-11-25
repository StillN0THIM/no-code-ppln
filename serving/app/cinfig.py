from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServingSettings(BaseSettings):
    mlflow_tracking_uri: str = "http://localhost:5000"
    model_name: str = "sample_model"

    model_config = SettingsConfigDict(env_prefix="SERVING_", env_file=".env")


settings = ServingSettings()