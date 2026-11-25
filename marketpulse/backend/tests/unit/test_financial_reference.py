from datetime import datetime
import pytest
from app.analytics.calculations.returns import performance_for_period


@pytest.fixture
def trading_sessions():
    return [
        (datetime(2023, 12, 29), 100.0),
        (datetime(2024, 1, 2), 101.0),
        (datetime(2024, 1, 31), 104.0),
        (datetime(2024, 3, 29), 109.0),
        (datetime(2024, 6, 28), 115.0),
        (datetime(2024, 12, 31), 120.0),
        (datetime(2025, 1, 2), 126.0),
    ]


def test_reference_1d(trading_sessions):
    assert performance_for_period(trading_sessions, '1D', datetime(2025, 1, 2)) == pytest.approx(5.0)


def test_reference_ytd(trading_sessions):
    assert performance_for_period(trading_sessions, 'YTD', datetime(2025, 1, 2)) == pytest.approx(5.0)


def test_duplicate_sessions_use_one_observation():
    records = [(datetime(2025, 1, 2), 100), (datetime(2025, 1, 2), 110), (datetime(2025, 1, 3), 120)]
    assert performance_for_period(records, '1D', datetime(2025, 1, 3)) == pytest.approx(20.0)


def test_zero_reference_returns_null():
    assert performance_for_period([(datetime(2025, 1, 2), 0), (datetime(2025, 1, 3), 100)], '1D', datetime(2025, 1, 3)) is None


def test_missing_history_returns_null():
    assert performance_for_period([(datetime(2025, 1, 3), 100)], '1D', datetime(2025, 1, 3)) is None
