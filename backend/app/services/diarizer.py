"""
Servicio de diarización (quién habla cuándo) con pyannote-audio.
Requiere token de Hugging Face con acceso a pyannote/speaker-diarization-3.1.
"""
from pathlib import Path
from pyannote.audio import Pipeline
from app.config import settings


_pipeline: Pipeline | None = None


def get_pipeline() -> Pipeline:
    global _pipeline
    if _pipeline is None:
        if not settings.hf_token:
            raise RuntimeError(
                "HF_TOKEN no configurado. Se requiere token de Hugging Face "
                "con acceso a pyannote/speaker-diarization-3.1"
            )
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=settings.hf_token,
        )
    return _pipeline


def diarize(audio_path: Path) -> list[dict]:
    """
    Ejecuta diarización sobre el audio.
    Retorna: [{"start": 0.0, "end": 5.2, "speaker": "SPEAKER_00"}, ...]
    """
    pipeline = get_pipeline()
    diarization = pipeline(str(audio_path))

    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        results.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker,
        })

    return results
