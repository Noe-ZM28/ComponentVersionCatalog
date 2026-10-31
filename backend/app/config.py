from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Component Version Catalog"
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'component_version_catalog.db').as_posix()}"
    storage_path: str = str(PROJECT_ROOT / "storage" / "files")

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()