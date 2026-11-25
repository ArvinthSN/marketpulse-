from abc import ABC, abstractmethod
from app.ingestion.discovery.schemas import DiscoveredInstrument


class UniverseDiscoveryProvider(ABC):
    @abstractmethod
    def discover(self, country_code: str | None = None, exchange_code: str | None = None, limit: int = 100) -> list[DiscoveredInstrument]:
        raise NotImplementedError
