from datetime import UTC, datetime

from src.services.market_data_service import MarketDataService


class DummyFinnhub:
    async def get_candles(self, symbol, start, end):
        return {'c': [], 't': [], 's': 'no_data'}

    async def get_quote(self, symbol):
        return {'c': 123.45, 't': int(datetime.now(UTC).timestamp())}


def test_market_data_service_falls_back_to_quote():
    service = MarketDataService(DummyFinnhub())
    points = __import__('asyncio').run(service.get_price_series('AAPL', '30d'))
    assert len(points) == 1
    assert points[0].close == 123.45
