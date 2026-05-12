from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql://transcriber:transcriber@localhost:5432/transcriber"
    upload_dir: Path = Path("/data/uploads")
    audio_dir: Path = Path("/data/audio")
    model_size: str = "small"  # tiny, base, small, medium
    model_device: str = "cpu"
    model_compute_type: str = "int8"  # int8 para CPU
    hf_token: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
