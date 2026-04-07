from datetime import UTC, datetime

from src.models import NewsItem
from src.services.trending_service import TrendingService


class DummyNewsService:
    async def get_market_news(self):
        return [
            NewsItem(
                symbol='MARKET',
                title='Apple and Tesla rally after upbeat outlook',
                summary='NVIDIA also gains in tech trade.',
                publisher='Reuters',
                url='https://example.com/1',
                published_at=datetime.now(UTC),
                related_symbols=[],
            )
        ]


def test_trending_service_falls_back_to_text_extraction():
    service = TrendingService(DummyNewsService())
    ranked = __import__('asyncio').run(service.compute('24h'))
    symbols = [row['symbol'] for row in ranked]
    assert 'AAPL' in symbols
    assert 'TSLA' in symbols
