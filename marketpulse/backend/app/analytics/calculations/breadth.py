def breadth(returns: list[float | None]) -> dict:
    valid = [value for value in returns if value is not None]
    advancing = sum(value > 0 for value in valid)
    declining = sum(value < 0 for value in valid)
    unchanged = sum(value == 0 for value in valid)
    total = len(valid)
    ratio = advancing / declining if declining else None
    return {
        'advancing': advancing,
        'declining': declining,
        'unchanged': unchanged,
        'advance_decline_ratio': ratio,
        'advance_decline_difference': advancing - declining,
        'percentage_advancing': advancing / total * 100 if total else None,
        'percentage_declining': declining / total * 100 if total else None,
        'valid_observation_count': total,
        'excluded_unavailable': len(returns) - len(valid),
    }
