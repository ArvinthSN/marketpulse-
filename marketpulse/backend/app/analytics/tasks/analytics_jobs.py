from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import AnalyticsJobRun


class AnalyticsJobService:
    def __init__(self, db: Session):
        self.db = db

    def start(self, scope_type: str, scope_value: str | None, periods: list[str]):
        existing = self.db.scalar(select(AnalyticsJobRun).where(
            AnalyticsJobRun.scope_type == scope_type,
            AnalyticsJobRun.scope_value == scope_value,
            AnalyticsJobRun.status.in_(('running', 'partial')),
        ).order_by(AnalyticsJobRun.started_at.desc()).limit(1))
        if existing:
            raise ValueError('An analytics job is already running or resumable for this scope')
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
        job.status = 'failed' if failed and records_processed == 0 else ('partial' if failed else 'completed')
        job.records_processed = records_processed
        job.failed = failed
        job.error_summary = error_summary
        job.finished_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return job

    def snapshot(self, entity_type: str, entity_id: str, period: str, reporting_currency: str,
                 result: dict, source_observation_at: datetime | None = None, coverage: dict | None = None):
        from app.models.entities import AnalyticsSnapshot
        import json
        existing = self.db.scalar(select(AnalyticsSnapshot).where(
            AnalyticsSnapshot.entity_type == entity_type,
            AnalyticsSnapshot.entity_id == entity_id,
            AnalyticsSnapshot.period == period,
            AnalyticsSnapshot.reporting_currency == reporting_currency,
        ).order_by(AnalyticsSnapshot.calculated_at.desc()).limit(1))
        if existing:
            existing.calculated_at = datetime.utcnow()
            existing.source_observation_at = source_observation_at
            existing.coverage_json = json.dumps(coverage or {})
            existing.result_json = json.dumps(result)
        else:
            self.db.add(AnalyticsSnapshot(entity_type=entity_type, entity_id=entity_id,
                period=period, reporting_currency=reporting_currency, methodology_version='phase2.1',
                calculated_at=datetime.utcnow(), source_observation_at=source_observation_at,
                coverage_json=json.dumps(coverage or {}), result_json=json.dumps(result)))
        self.db.commit()
