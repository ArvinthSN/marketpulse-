from datetime import datetime, timedelta
from bisect import bisect_left
from math import isfinite


def calculate_return(current: float | None, reference: float | None) -> float | None:
    if current is None or reference is None or reference == 0:
        return None
    if not isfinite(current) or not isfinite(reference):
        return None
    return ((current - reference) / reference) * 100.0


def closest_observation(records: list[tuple[datetime, float]], target: datetime, tolerance_days: int = 10) -> float | None:
    valid = [(ts, price) for ts, price in records if price is not None and isfinite(price) and price > 0]
    if not valid:
        return None
    times = [ts for ts, _ in valid]
    position = bisect_left(times, target)
    candidates = []
    if position < len(valid):
        candidates.append(valid[position])
    if position > 0:
        candidates.append(valid[position - 1])
    nearest = min(candidates, key=lambda item: abs(item[0] - target))
    if abs(nearest[0] - target) > timedelta(days=tolerance_days):
        return None
    return nearest[1]


def performance_for_period(records: list[tuple[datetime, float]], period: str, now: datetime, tolerance_days: int = 10) -> float | None:
    valid = sorted((ts, price) for ts, price in records if price is not None and isfinite(price) and price > 0)
    if len(valid) < 2:
        return None
    current = valid[-1][1]
    if period == '1D':
        reference = valid[-2][1]
    elif period == 'YTD':
        target = datetime(now.year - 1, 12, 31, tzinfo=now.tzinfo)
        reference = closest_observation(valid, target, 31)
    else:
        calendar_days = {'1W': 7, '1M': 31, '3M': 92, '6M': 183, '1Y': 365, '3Y': 1095, '5Y': 1825, 'ALL': 36500}
        if period == 'ALL':
            reference = valid[0][1]
        else:
            if period not in calendar_days:
                return None
            reference = closest_observation(valid, now - timedelta(days=calendar_days[period]), tolerance_days)
    return calculate_return(current, reference)
