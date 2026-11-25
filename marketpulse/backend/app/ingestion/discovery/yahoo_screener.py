from app.ingestion.discovery.base import UniverseDiscoveryProvider
from app.ingestion.discovery.schemas import DiscoveredInstrument


class YahooScreenerDiscovery(UniverseDiscoveryProvider):
    """Explicit, coverage-unknown Yahoo screener adapter.

    Yahoo Finance does not guarantee that screener results represent a complete
    exchange universe. Discovery completeness is therefore always reported as
    partial until backed by a separately maintained exchange instrument list.
    """

    def discover(self, country_code: str | None = None, exchange_code: str | None = None, limit: int = 100) -> list[DiscoveredInstrument]:
        raise NotImplementedError(
            'Yahoo screener discovery is not enabled; use an exchange instrument CSV/JSON import and record its source'
        )
