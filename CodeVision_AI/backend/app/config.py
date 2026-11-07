from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / '.env'), extra='ignore')
    hindsight_base_url: str = 'https://api.hindsight.vectorize.io'
    hindsight_api_key: str = ''
    groq_api_key: str = ''
    groq_model: str = 'openai/gpt-oss-20b'
    database_path: str = 'backend/data/codevision.sqlite3'
    frontend_origin: str = 'http://localhost:5173'

    @property
    def database_file(self) -> Path:
        path = Path(self.database_path)
        return path if path.is_absolute() else ROOT / path

settings = Settings()
