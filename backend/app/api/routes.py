"""
Endpoints de la API.
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.job import create_job, get_job, list_jobs
from app.tasks.worker import process_transcription

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Sube un video, lo guarda en disco y encola la transcripción.
    Retorna el job_id para hacer polling.
    """
    if not file.filename:
        raise HTTPException(400, "Nombre de archivo requerido")

    # Validar extensión
    allowed = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".mp3", ".wav", ".m4a", ".ogg", ".flac"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"Formato no soportado: {suffix}. Formatos: {', '.join(sorted(allowed))}")

    job_id = uuid.uuid4().hex[:12]

    # Guardar archivo
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    ext = suffix or ".mp4"
    safe_filename = f"{job_id}{ext}"
    file_path = settings.upload_dir / safe_filename

    content = await file.read()
    file_path.write_bytes(content)

    # Crear job y encolar
    create_job(job_id, file.filename)
    process_transcription.delay(safe_filename, job_id)

    return JSONResponse({
        "job_id": job_id,
        "status": "pending",
        "original_filename": file.filename,
    })


@router.get("/jobs")
async def get_jobs():
    """Lista todos los jobs."""
    jobs = list_jobs()
    return JSONResponse([j.to_dict() for j in jobs])


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Obtiene el estado y resultado de un job."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, "Job no encontrado")
    return JSONResponse(job.to_dict())
