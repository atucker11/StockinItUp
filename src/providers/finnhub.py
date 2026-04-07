from datetime import datetime

from ..cache import AsyncTTLCache
from ..config import settings
from ..utils.dates import now_utc
from .http import HTTPClient


class FinnhubClient:
    base_url = "https://finnhub.io/api/v1"

    def __init__(self, http: HTTPClient, cache: AsyncTTLCache) -> None:
        self.http = http
        self.cache = cache

    async def _get(self, endpoint: str, params: dict) -> dict | list:
        merged = {"token": settings.finnhub_api_key, **params}
        async with self.http.session.get(f"{self.base_url}/{endpoint}", params=merged) as response:
            response.raise_for_status()
            return await response.json()

    async def get_quote(self, symbol: str) -> dict:
        key = f"quote:{symbol}"
        return await self.cache.get_or_set(key, settings.cache_ttl_seconds, lambda: self._get("quote", {"symbol": symbol}))

    async def get_candles(self, symbol: str, start: datetime, end: datetime, resolution: str = "D") -> dict:
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": int(start.timestamp()),
            "to": int(end.timestamp()),
        }
        key = f"candles:{symbol}:{resolution}:{params['from']}:{params['to']}"
        return await self.cache.get_or_set(key, settings.cache_ttl_seconds, lambda: self._get("stock/candle", params))

    async def get_company_news(self, symbol: str, start: datetime, end: datetime) -> list[dict]:
        params = {
            "symbol": symbol,
            "from": start.date().isoformat(),
            "to": end.date().isoformat(),
        }
        key = f"company-news:{symbol}:{params['from']}:{params['to']}"
        result = await self.cache.get_or_set(key, settings.cache_ttl_seconds, lambda: self._get("company-news", params))
        return result if isinstance(result, list) else []

    async def get_market_news(self, category: str | None = None) -> list[dict]:
        category = category or settings.default_market_category
        key = f"market-news:{category}:{now_utc().strftime('%Y-%m-%d-%H')}"
        result = await self.cache.get_or_set(key, 900, lambda: self._get("news", {"category": category}))
        return result if isinstance(result, list) else []

    async def get_news_sentiment(self, symbol: str) -> dict:
        key = f"news-sentiment:{symbol}"
        result = await self.cache.get_or_set(key, settings.cache_ttl_seconds, lambda: self._get("news-sentiment", {"symbol": symbol}))
        return result if isinstance(result, dict) else {}

    async def get_stock_symbols(self, exchange: str = "US") -> list[dict]:
        key = f"symbols:{exchange}:{now_utc().strftime('%Y-%m-%d')}"
        result = await self.cache.get_or_set(key, 86400, lambda: self._get("stock/symbol", {"exchange": exchange}))
        return result if isinstance(result, list) else []
