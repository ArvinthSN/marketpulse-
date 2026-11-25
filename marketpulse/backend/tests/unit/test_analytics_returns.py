from datetime import datetime
from app.analytics.calculations.returns import calculate_return, performance_for_period


def test_return_calculation():
    assert calculate_return(110, 100) == 10


def test_missing_reference_is_null():
    assert calculate_return(110, None) is None


def test_one_day_return_uses_previous_session():
    now = datetime(2026, 1, 10)
    records = [(datetime(2026, 1, 8), 100), (datetime(2026, 1, 9), 105)]
    assert performance_for_period(records, '1D', now) == 5


def test_all_period_uses_oldest_observation():
    records = [(datetime(2020, 1, 2), 50), (datetime(2026, 1, 2), 100)]
    assert performance_for_period(records, 'ALL', datetime(2026, 1, 2)) == 100
