from collections import defaultdict
from datetime import UTC

from ..config import settings
from ..models import NewsItem
from ..services.news_service import NewsService
from ..utils.dates import now_utc, timeframe_to_days
from ..utils.tickers import extract_symbols_from_text, likely_us_equity


_SOURCE_WEIGHTS = {
    "reuters": 1.0,
    "associated press": 1.0,
    "bloomberg": 0.95,
    "marketwatch": 0.8,
    "cnbc": 0.85,
    "benzinga": 0.65,
    "motley fool": 0.55,
}


class TrendingService:
    def __init__(self, news_service: NewsService) -> None:
        self.news_service = news_service

    def _source_weight(self, publisher: str) -> float:
        normalized = publisher.lower()
        for key, value in _SOURCE_WEIGHTS.items():
            if key in normalized:
                return value
        return 0.6

    def _recency_weight(self, item: NewsItem, window_days: int) -> float:
        hours_old = (now_utc() - item.published_at.astimezone(UTC)).total_seconds() / 3600
        max_hours = max(window_days * 24, 1)
        decay = max(0.3, 1 - (hours_old / max_hours))
        return decay

    def _symbols_for_item(self, item: NewsItem) -> list[str]:
        symbols = [symbol for symbol in item.related_symbols if likely_us_equity(symbol)]
        if symbols:
            return list(dict.fromkeys(symbols))
        text = f"{item.title} {item.summary}"
        return [symbol for symbol in extract_symbols_from_text(text) if likely_us_equity(symbol)]

    async def compute(self, timeframe: str) -> list[dict]:
        news = await self.news_service.get_market_news()
        window_days = timeframe_to_days(timeframe)
        now = now_utc()
        scores = defaultdict(float)
        articles = defaultdict(list)
        for item in news:
            if (now - item.published_at).days > window_days:
                continue
            symbols = self._symbols_for_item(item)
            if not symbols:
                continue
            for symbol in set(symbols):
                weight = self._source_weight(item.publisher) * self._recency_weight(item, window_days)
                scores[symbol] += weight
                articles[symbol].append(item)
        ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
        output = []
        for symbol, score in ranked[: settings.max_tickers_in_trending]:
            related = sorted(articles[symbol], key=lambda item: item.published_at, reverse=True)
            headlines = related[:3]
            why = self._why_trending(headlines)
            output.append({
                "symbol": symbol,
                "score": round(score, 2),
                "why": why,
                "headlines": headlines,
            })
        return output

    def _why_trending(self, items: list[NewsItem]) -> str:
        if not items:
            return "No recent headlines found."
        publishers = ", ".join(sorted({item.publisher for item in items[:3]}))
        latest = items[0].title
        return f"Recent multi-source mentions led by: {latest} | Sources: {publishers}"
