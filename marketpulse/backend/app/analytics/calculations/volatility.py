import math


def daily_returns(prices: list[float]) -> list[float]:
    returns = []
    for previous, current in zip(prices, prices[1:]):
        if previous is not None and current is not None and previous > 0:
            returns.append((current - previous) / previous)
    return returns


def historical_volatility(prices: list[float], window: int, annualization_factor: float = 252.0) -> float | None:
    if window < 2:
        return None
    returns = daily_returns(prices[-(window + 1):])
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((value - mean) ** 2 for value in returns) / (len(returns) - 1)
    return math.sqrt(variance) * math.sqrt(annualization_factor) * 100.0
