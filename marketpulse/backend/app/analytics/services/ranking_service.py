from app.analytics.calculations.market_cap import market_cap_from_inputs


class RankingService:
    @staticmethod
    def rank_market_caps(items: list[dict], limit: int = 100) -> list[dict]:
        ranked = [item for item in items if item.get('market_cap') is not None]
        ranked.sort(key=lambda item: item['market_cap'], reverse=True)
        return ranked[:limit]

    @staticmethod
    def rank_volume(items: list[dict], limit: int = 100) -> list[dict]:
        ranked = [item for item in items if item.get('volume') is not None]
        ranked.sort(key=lambda item: item['volume'], reverse=True)
        return ranked[:limit]
