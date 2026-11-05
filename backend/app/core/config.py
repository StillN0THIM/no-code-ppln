from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mlflow_tracking_url="http://localhost:5000"
    postgres_dsn: str= "postgressql://mlops:mlops@localhost:5432/mlops"
    cors_allowed_origins: list[str] = ["http://localhost:5173"]
    model_config = SettingsConfigDict(env_prefix="MLOPS_",env_file=".env")

settings = Settings()