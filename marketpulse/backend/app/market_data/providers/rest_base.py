from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.market_data.providers.base import AsyncMarketDataProvider


class RestMarketDataProvider(AsyncMarketDataProvider):
    """Shared HTTP lifecycle, transient-error retry and provider-neutral helpers."""

    provider_name = "rest"
    base_url = ""
    
    def __init__(self, api_key: str, timeout: float = 15.0, retries: int = 2):
        if not api_key:
            raise ValueError(f"{self.provider_name} API key is not configured")
        self.api_key = api_key
        self.timeout = timeout
        self.retries = max(0, retries)
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Accept": "application/json"},
            )

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        await self.connect()
        assert self._client is not None
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = await self._client.get(path, params=params)
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict) and payload.get("status") == "error":
                    raise RuntimeError(str(payload.get("message") or payload))
                if isinstance(payload, dict) and payload.get("code") and payload.get("status") == "error":
                    raise RuntimeError(str(payload.get("message") or payload))
                return payload
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_error = exc
                retryable = not isinstance(exc, httpx.HTTPStatusError) or (
                    exc.response.status_code == 429 or exc.response.status_code >= 500
                )
                if not retryable or attempt >= self.retries:
                    raise
                retry_after = 0.0
                if isinstance(exc, httpx.HTTPStatusError):
                    try:
                        retry_after = min(float(exc.response.headers.get("Retry-After", "0")), 10.0)
                    except ValueError:
                        retry_after = 0.0
                await asyncio.sleep(max(retry_after, 0.25 * (2 ** attempt)))
        assert last_error is not None
        raise last_error

    async def subscribe(self, symbols: list[str]) -> None:
        raise NotImplementedError(f"{self.provider_name} REST adapter is snapshot-only")

    async def unsubscribe(self, symbols: list[str]) -> None:
        return None

    async def get_quotes(self, symbols: list[str]) -> list[dict]:
        quotes = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        return quotes

    async def get_history(self, symbol: str, *, start: str, end: str,
                          interval: str = "1day") -> list[dict]:
        raise NotImplementedError

    async def get_company(self, symbol: str) -> dict | None:
        raise NotImplementedError

    async def health_check(self) -> dict:
        return {"provider": self.provider_name, "configured": True,
                "streaming": False, "state": "configured"}
