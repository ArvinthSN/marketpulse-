def average_volume(volumes: list[float]) -> float | None:
    valid = [value for value in volumes if value is not None and value >= 0]
    return sum(valid) / len(valid) if valid else None


def relative_volume(current_volume: float | None, historical_volumes: list[float]) -> float | None:
    average = average_volume(historical_volumes)
    if current_volume is None or average is None or average == 0:
        return None
    return current_volume / average


def volume_change_percentage(current_volume: float | None, previous_volume: float | None) -> float | None:
    if current_volume is None or previous_volume is None or previous_volume == 0:
        return None
    return ((current_volume - previous_volume) / previous_volume) * 100.0
