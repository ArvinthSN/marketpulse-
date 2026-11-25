from app.analytics.aggregations.sector_aggregation import weighted_average, equal_weighted


def country_returns(items: list[dict]) -> dict:
    market_cap_weighted = weighted_average([(item.get('market_cap'), item.get('return_percentage')) for item in items])
    equal = equal_weighted([item.get('return_percentage') for item in items])
    return {'market_cap_weighted': market_cap_weighted, 'equal_weighted': equal}
