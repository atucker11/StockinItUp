from datetime import datetime

from src.models import PricePoint
from src.services.market_data_service import MarketDataService


class DummyFinnhub:
    pass


def test_max_drawdown_and_volatility_are_calculated():
    service = MarketDataService(DummyFinnhub())
    closes = [100, 120, 90, 95, 110]
    assert service._max_drawdown(closes) < 0
    assert service._volatility(closes) > 0


def test_returns_from_series():
    service = MarketDataService(DummyFinnhub())
    points = [PricePoint(timestamp=datetime(2025, 1, day + 1), close=100 + day) for day in range(28)]
    returns = service._returns_from_series(points)
    assert "1D" in returns
    assert "1W" in returns
