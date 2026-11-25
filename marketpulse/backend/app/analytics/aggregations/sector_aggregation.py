def weighted_average(values: list[tuple[float, float]]) -> float | None:
    valid = [(weight, value) for weight, value in values if weight is not None and value is not None and weight >= 0]
    denominator = sum(weight for weight, _ in valid)
    if denominator <= 0:
        return None
    return sum(weight * value for weight, value in valid) / denominator


def equal_weighted(values: list[float | None]) -> float | None:
    valid = [value for value in values if value is not None]
    return sum(valid) / len(valid) if valid else None
