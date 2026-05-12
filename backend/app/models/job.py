"""
Modelo de jobs con SQLAlchemy + PostgreSQL.
"""
import json
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import create_engine, Column, String, Text, text as sa_text
from sqlalchemy.orm import Session, declarative_base
from app.config import settings

Base = declarative_base()

engine = create_engine(settings.database_url)


class JobStatus(str, Enum):
    pending = "pending"
    extracting_audio = "extracting_audio"
    transcribing = "transcribing"
    diarizing = "diarizing"
    aligning = "aligning"
    completed = "completed"
    failed = "failed"


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    original_filename = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    job_metadata = Column("metadata", Text, nullable=True)
    error = Column(Text, nullable=True)

    def to_dict(self):
        meta = None
        if self.job_metadata:
            try:
                meta = json.loads(self.job_metadata)
            except (json.JSONDecodeError, TypeError):
                meta = None
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": meta,
            "error": self.error,
        }


def init_db():
    """Crea las tablas si no existen."""
    Base.metadata.create_all(engine)
    # Migración: si la tabla jobs se acaba de crear pero no tiene columnas correctas
    with engine.connect() as conn:
        conn.execute(sa_text("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                error TEXT
            )
        """))
        conn.commit()


def get_session() -> Session:
    return Session(engine)


def create_job(job_id: str, filename: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    model = JobModel(
        id=job_id,
        original_filename=filename,
        status=JobStatus.pending.value,
        created_at=now,
        updated_at=now,
    )
    with get_session() as session:
        session.add(model)
        session.commit()
    return model.to_dict()


def update_job_status(job_id: str, status: str, metadata: dict | None = None, error: str | None = None):
    now = datetime.now(timezone.utc).isoformat()
    with get_session() as session:
        job = session.query(JobModel).filter(JobModel.id == job_id).first()
        if job:
            job.status = status
            job.updated_at = now
            if metadata is not None:
                job.job_metadata = json.dumps(metadata)
            if error is not None:
                job.error = error
            session.commit()


def get_job(job_id: str) -> dict | None:
    with get_session() as session:
        job = session.query(JobModel).filter(JobModel.id == job_id).first()
        if job is None:
            return None
        return job.to_dict()


def list_jobs(limit: int = 50) -> list[dict]:
    with get_session() as session:
        jobs = (
            session.query(JobModel)
            .order_by(JobModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [j.to_dict() for j in jobs]
