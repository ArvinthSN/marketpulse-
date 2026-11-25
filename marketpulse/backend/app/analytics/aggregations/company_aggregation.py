from app.analytics.calculations.returns import calculate_return


def valid_company_return(current: float | None, reference: float | None) -> float | None:
    return calculate_return(current, reference)
