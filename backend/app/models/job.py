"""
Modelo simple de jobs en SQLite (sin dependencia externa mientras no haya PostgreSQL).
Para producción se migra a PostgreSQL + SQLAlchemy.
"""
import json
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict

DB_PATH = Path(__file__).parent / "jobs.db"


class JobStatus(str, Enum):
    pending = "pending"
    extracting_audio = "extracting_audio"
    transcribing = "transcribing"
    diarizing = "diarizing"
    aligning = "aligning"
    completed = "completed"
    failed = "failed"


@dataclass
class Job:
    id: str
    original_filename: str
    status: JobStatus
    created_at: str
    updated_at: str
    metadata: dict | None = None
    error: str | None = None

    def to_dict(self):
        d = asdict(self)
        d["metadata"] = json.dumps(self.metadata) if self.metadata else None
        return d


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT,
            error TEXT
        )
    """)
    conn.commit()
    return conn


def create_job(job_id: str, filename: str) -> Job:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO jobs (id, original_filename, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (job_id, filename, JobStatus.pending.value, now, now),
    )
    conn.commit()
    conn.close()
    return Job(id=job_id, original_filename=filename, status=JobStatus.pending,
               created_at=now, updated_at=now)


def update_job_status(job_id: str, status: str, metadata: dict | None = None, error: str | None = None):
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    updates = {"status": status, "updated_at": now}
    if metadata is not None:
        updates["metadata"] = json.dumps(metadata)
    if error is not None:
        updates["error"] = error

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [job_id]
    conn.execute(f"UPDATE jobs SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_job(job_id: str) -> Job | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    d = dict(row)
    d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else None
    d["status"] = JobStatus(d["status"])
    return Job(**d)


def list_jobs(limit: int = 50) -> list[Job]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    jobs = []
    for row in rows:
        d = dict(row)
        d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else None
        d["status"] = JobStatus(d["status"])
        jobs.append(Job(**d))
    return jobs
