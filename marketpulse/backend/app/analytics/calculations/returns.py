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
    valid = _deduplicate_sessions(records)
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


def prior_trading_session(records: list[tuple[datetime, float]], target: datetime, tolerance_days: int) -> float | None:
    valid = _deduplicate_sessions(records)
    candidates = [(timestamp, price) for timestamp, price in valid if timestamp <= target]
    if not candidates:
        return None
    timestamp, price = candidates[-1]
    if abs(target - timestamp) > timedelta(days=tolerance_days):
        return None
    return price


def performance_for_period(records: list[tuple[datetime, float]], period: str, now: datetime, tolerance_days: int = 10) -> float | None:
    valid = _deduplicate_sessions(records)
    if not valid:
        return None

    current_timestamp, current = valid[-1]
    if period == '1D':
        if len(valid) < 2:
            return None
        reference = valid[-2][1]
    elif period == 'YTD':
        prior_year_start = datetime(now.year - 1, 1, 1, tzinfo=now.tzinfo)
        prior_year_end = datetime(now.year, 1, 1, tzinfo=now.tzinfo)
        prior_year_sessions = [(timestamp, price) for timestamp, price in valid if prior_year_start <= timestamp < prior_year_end]
        if not prior_year_sessions:
            return None
        reference = prior_year_sessions[-1][1]
    elif period == 'ALL':
        if len(valid) < 2:
            return None
        reference = valid[0][1]
    else:
        calendar_days = {'1W': 7, '1M': 31, '3M': 92, '6M': 183, '1Y': 365, '3Y': 1095, '5Y': 1825}
        if period not in calendar_days:
            return None
        target = now - timedelta(days=calendar_days[period])
        reference = prior_trading_session(valid, target, tolerance_days)

    return calculate_return(current, reference)


def _deduplicate_sessions(records: list[tuple[datetime, float]]) -> list[tuple[datetime, float]]:
    deduplicated: dict[datetime, float] = {}
    for timestamp, price in sorted(records, key=lambda item: item[0]):
        if price is not None and isfinite(price) and price > 0:
            if timestamp not in deduplicated:
                deduplicated[timestamp] = price
    return sorted(deduplicated.items())
