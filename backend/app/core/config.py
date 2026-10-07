from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

class Settings(BaseSettings):
    app_name: str = "Adaptive Agentic RAG API"
    app_version: str = "0.1.0"
    max_upload_size_mb: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 200
    allowed_extensions: str = "pdf,txt,md,docx"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_extension_set(self) -> set[str]:
        return {x.strip().lower().lstrip(".") for x in self.allowed_extensions.split(",") if x.strip()}

settings = Settings()
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
