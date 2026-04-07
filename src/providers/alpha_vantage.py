from ..cache import AsyncTTLCache
from ..config import settings
from .http import HTTPClient


class AlphaVantageClient:
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, http: HTTPClient, cache: AsyncTTLCache) -> None:
        self.http = http
        self.cache = cache

    async def _get(self, params: dict) -> dict:
        merged = {"apikey": settings.alpha_vantage_api_key, **params}
        async with self.http.session.get(self.base_url, params=merged) as response:
            response.raise_for_status()
            return await response.json()

    async def get_news_sentiment(self, symbol: str, limit: int = 20) -> dict:
        if not settings.alpha_vantage_api_key:
            return {}
        key = f"av:news-sentiment:{symbol}:{limit}"
        return await self.cache.get_or_set(
            key,
            settings.cache_ttl_seconds,
            lambda: self._get({"function": "NEWS_SENTIMENT", "tickers": symbol, "limit": str(limit)}),
        )
