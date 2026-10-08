from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    storage_dir: Path = Path("./storage/notes")
    languagetool_url: str = "https://api.languagetool.org/v2/check"
    languagetool_timeout: float = 10.0
    use_mock_grammar: bool = False


settings = Settings()
