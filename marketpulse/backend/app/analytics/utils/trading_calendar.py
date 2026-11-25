from datetime import datetime, timedelta


def is_reference_close(records: list[tuple[datetime, float]], target: datetime, tolerance_days: int) -> bool:
    if not records:
        return False
    closest = min(records, key=lambda item: abs(item[0] - target))[0]
    return abs(closest - target) <= timedelta(days=tolerance_days)
