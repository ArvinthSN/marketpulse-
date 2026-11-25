from app.analytics.tasks.analytics_jobs import AnalyticsJobService


def test_duplicate_running_job_is_rejected(db_session):
    service = AnalyticsJobService(db_session)
    first = service.start('global', None, ['1D'])
    try:
        service.start('global', None, ['1D'])
        assert False, 'duplicate running job should be rejected'
    except ValueError:
        pass
    assert first.status == 'running'
