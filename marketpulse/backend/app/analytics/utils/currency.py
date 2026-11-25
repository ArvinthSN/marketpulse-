from abc import ABC, abstractmethod
from datetime import datetime


class FXRateProvider(ABC):
    @abstractmethod
    def get_rate(self, base_currency: str, quote_currency: str, timestamp: datetime) -> float | None:
        raise NotImplementedError


class NullFXRateProvider(FXRateProvider):
    def get_rate(self, base_currency: str, quote_currency: str, timestamp: datetime) -> float | None:
        if base_currency == quote_currency:
            return 1.0
        return None
