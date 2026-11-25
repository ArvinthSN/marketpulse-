from datetime import datetime
from sqlalchemy.orm import Session
from app.models.entities import AnalyticsJobRun


class AnalyticsJobService:
    def __init__(self, db: Session):
        self.db = db

    def start(self, scope_type: str, scope_value: str | None, periods: list[str]):
        job = AnalyticsJobRun(scope_type=scope_type, scope_value=scope_value,
                              status='running', periods=','.join(periods), started_at=datetime.utcnow())
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def complete(self, job_id: int, records_processed: int = 0, failed: int = 0, error_summary: str | None = None):
        job = self.db.get(AnalyticsJobRun, job_id)
        if job is None:
            raise ValueError(f'Analytics job not found: {job_id}')
        job.status = 'partial' if failed else 'completed'
        job.records_processed = records_processed
        job.failed = failed
        job.error_summary = error_summary
        job.finished_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return job
