from abc import ABC, abstractmethod


class AsyncMarketDataProvider(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def subscribe(self, symbols: list[str]) -> None: ...

    @abstractmethod
    async def unsubscribe(self, symbols: list[str]) -> None: ...

    @abstractmethod
    async def get_quote(self, symbol: str) -> dict | None: ...

    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> list[dict]: ...

    @abstractmethod
    async def health_check(self) -> dict: ...
