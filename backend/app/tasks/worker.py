"""
Tareas asíncronas con Celery para procesar transcripciones.
"""
from pathlib import Path
from celery import Celery
from celery.signals import worker_ready
from app.config import settings
from app.services.audio import extract_audio, get_audio_duration
from app.services.transcriber import transcribe
from app.services.diarizer import diarize
from app.services.aligner import align


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Inicializa la DB cuando el worker arranca."""
    from app.models.job import init_db
    init_db()

celery_app = Celery(
    "transcriber",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_concurrency=1,  # un solo job a la vez por la CPU vieja
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def process_transcription(self, video_filename: str, job_id: str):
    """
    Pipeline completo:
    1. Extraer audio del video
    2. Transcribir con faster-whisper
    3. Diarizar con pyannote
    4. Alinear y asignar hablantes
    """
    from app.models.job import update_job_status

    video_path = settings.upload_dir / video_filename

    try:
        update_job_status(job_id, "extracting_audio")
        audio_path = extract_audio(video_path)
        duration = get_audio_duration(audio_path)

        update_job_status(job_id, "transcribing", {"duration_seconds": duration})
        transcription = transcribe(audio_path)

        update_job_status(job_id, "diarizing")
        diarization = diarize(audio_path)

        update_job_status(job_id, "aligning")
        result = align(transcription, diarization)

        update_job_status(job_id, "completed", {"segments": result})

        return {"status": "completed", "segments_count": len(result)}

    except Exception as exc:
        update_job_status(job_id, "failed", error=str(exc))
        # No reintentar errores de código (TypeError, ValueError, etc.)
        if isinstance(exc, (TypeError, ValueError, RuntimeError)):
            raise
        raise self.retry(exc=exc, countdown=60)
