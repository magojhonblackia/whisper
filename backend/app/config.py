from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql://transcriber:transcriber@localhost:5432/transcriber"
    upload_dir: Path = Path("./uploads")
    audio_dir: Path = Path("./audio")
    model_size: str = "small"  # tiny, base, small, medium
    model_device: str = "cpu"
    model_compute_type: str = "int8"  # int8 para CPU
    # pyannote requiere token de Hugging Face (aceptar términos en hf.co)
    hf_token: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
