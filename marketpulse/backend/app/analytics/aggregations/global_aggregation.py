from app.analytics.aggregations.sector_aggregation import weighted_average, equal_weighted


def global_return(country_items: list[dict]) -> dict:
    return {
        'market_cap_weighted': weighted_average([(item.get('market_cap'), item.get('return_percentage')) for item in country_items]),
        'equal_weighted': equal_weighted([item.get('return_percentage') for item in country_items]),
    }
