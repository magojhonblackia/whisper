"""
Servicio de transcripción con faster-whisper.
"""
import time
from pathlib import Path
from faster_whisper import WhisperModel
from app.config import settings


_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(
            settings.model_size,
            device=settings.model_device,
            compute_type=settings.model_compute_type,
            num_workers=2,
            cpu_threads=0,  # usar todos los cores disponibles
        )
    return _model


def transcribe(audio_path: Path) -> list[dict]:
    """
    Transcribe un archivo de audio.
    Retorna lista de segmentos: [{"start": 0.0, "end": 2.5, "text": "..."}]
    """
    model = get_model()
    segments, info = model.transcribe(
        str(audio_path),
        language="es",
        beam_size=5,
        vad_filter=True,  # filtra silencios
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    results = []
    for seg in segments:
        results.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })

    return results
