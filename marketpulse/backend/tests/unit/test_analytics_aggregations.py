from app.analytics.aggregations.sector_aggregation import weighted_average, equal_weighted
from app.analytics.calculations.breadth import breadth
from app.analytics.calculations.market_cap import market_cap_from_inputs
from app.analytics.calculations.volume import relative_volume
from app.analytics.calculations.volatility import historical_volatility


def test_weighted_and_equal_sector_returns():
    assert weighted_average([(100, 10), (300, 20)]) == 17.5
    assert equal_weighted([10, None, 20]) == 15


def test_breadth_excludes_missing():
    result = breadth([1.0, -2.0, 0.0, None])
    assert result['advancing'] == 1
    assert result['declining'] == 1
    assert result['unchanged'] == 1
    assert result['excluded_unavailable'] == 1


def test_market_cap_missing_shares_is_null():
    result = market_cap_from_inputs(100, None, 'USD')
    assert result.value is None
    assert result.warning == 'missing_price_or_shares_outstanding'


def test_relative_volume():
    assert relative_volume(200, [100, 100, 100]) == 2


def test_volatility_needs_enough_observations():
    assert historical_volatility([100], 20) is None
