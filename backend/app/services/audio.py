"""
Utilidades de audio: extracción de audio de video usando FFmpeg.
"""
import subprocess
import shutil
from pathlib import Path
from app.config import settings


def extract_audio(video_path: Path) -> Path:
    """
    Extrae el audio de un video a WAV mono 16kHz.
    Retorna la ruta del archivo de audio extraído.
    """
    audio_path = settings.audio_dir / f"{video_path.stem}.wav"
    settings.audio_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        shutil.which("ffmpeg") or "ffmpeg",
        "-i", str(video_path),
        "-vn",                # sin video
        "-acodec", "pcm_s16le",  # WAV PCM 16-bit
        "-ar", "16000",       # 16kHz sample rate
        "-ac", "1",           # mono
        "-y",                 # sobrescribir
        str(audio_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg falló: {result.stderr}")

    return audio_path


def get_audio_duration(audio_path: Path) -> float:
    """Obtiene la duración del audio en segundos usando FFprobe."""
    cmd = [
        shutil.which("ffprobe") or "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())
