from datetime import UTC, datetime

from ..config import settings
from ..models import NewsItem
from ..providers.finnhub import FinnhubClient
from ..utils.dates import timeframe_window
from ..utils.tickers import normalize_symbol, split_related_symbols


class NewsService:
    def __init__(self, finnhub: FinnhubClient) -> None:
        self.finnhub = finnhub

    def _to_item(self, symbol: str, payload: dict) -> NewsItem:
        published_at = datetime.fromtimestamp(payload.get("datetime", 0), UTC)
        related = split_related_symbols(payload.get("related"))
        return NewsItem(
            symbol=normalize_symbol(symbol),
            title=(payload.get("headline") or "").strip(),
            summary=(payload.get("summary") or "").strip(),
            publisher=(payload.get("source") or "Unknown").strip(),
            url=(payload.get("url") or "").strip(),
            published_at=published_at,
            related_symbols=related,
        )

    def _dedupe(self, items: list[NewsItem]) -> list[NewsItem]:
        seen: set[str] = set()
        output: list[NewsItem] = []
        for item in sorted(items, key=lambda value: value.published_at, reverse=True):
            key = f"{item.publisher.lower()}::{item.title.lower()}::{item.url.lower()}"
            if key in seen:
                continue
            if not item.title or not item.url:
                continue
            seen.add(key)
            output.append(item)
        return output

    async def get_symbol_news(self, symbol: str, timeframe: str) -> list[NewsItem]:
        start, end = timeframe_window(timeframe)
        payload = await self.finnhub.get_company_news(normalize_symbol(symbol), start, end)
        items = [self._to_item(symbol, row) for row in payload[: max(settings.default_news_limit * 2, 50)]]
        return self._dedupe(items)[: settings.default_news_limit]

    async def get_market_news(self) -> list[NewsItem]:
        payload = await self.finnhub.get_market_news()
        items = [self._to_item("MARKET", row) for row in payload]
        return self._dedupe(items)
