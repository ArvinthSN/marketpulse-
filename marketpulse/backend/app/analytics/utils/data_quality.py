from datetime import datetime, timedelta


def freshness_status(last_observation: datetime | None, stale_after: timedelta, calculated_at: datetime) -> tuple[str, bool]:
    if last_observation is None:
        return 'UNAVAILABLE', True
    is_stale = calculated_at - last_observation > stale_after
    return ('STALE' if is_stale else 'AVAILABLE'), is_stale
