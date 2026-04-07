from datetime import UTC, datetime

from ..models import CompareSnapshot, PricePoint, PriceSnapshot
from ..providers.finnhub import FinnhubClient
from ..utils.dates import extended_price_window, timeframe_to_days, return_windows
from ..utils.tickers import normalize_symbol


class MarketDataService:
    def __init__(self, finnhub: FinnhubClient) -> None:
        self.finnhub = finnhub

    async def get_price_series(self, symbol: str, timeframe: str) -> list[PricePoint]:
        start, end = extended_price_window(timeframe)
        payload = await self.finnhub.get_candles(normalize_symbol(symbol), start, end)
        closes = payload.get("c", [])
        timestamps = payload.get("t", [])
        points: list[PricePoint] = []
        for timestamp, close in zip(timestamps, closes):
            if close is None:
                continue
            points.append(PricePoint(timestamp=datetime.fromtimestamp(timestamp, UTC), close=float(close)))
        if points:
            return points
        quote = await self.finnhub.get_quote(normalize_symbol(symbol))
        current = quote.get("c") or quote.get("pc")
        if not current:
            return []
        quote_time = int(quote.get("t") or end.timestamp())
        point = PricePoint(timestamp=datetime.fromtimestamp(quote_time, UTC), close=float(current))
        return [point]

    async def get_snapshot(self, symbol: str, timeframe: str) -> PriceSnapshot:
        points = await self.get_price_series(symbol, timeframe)
        if not points:
            raise ValueError(f"No market data available for {symbol}")
        closes = [point.close for point in points]
        current_price = closes[-1]
        returns = self._returns_from_series(points)
        range_low = min(closes)
        range_high = max(closes)
        volatility = self._volatility(closes)
        drawdown = self._max_drawdown(closes)
        trend = self._trend_description(closes, timeframe_to_days(timeframe))
        return PriceSnapshot(
            symbol=normalize_symbol(symbol),
            current_price=current_price,
            returns=returns,
            range_low=range_low,
            range_high=range_high,
            trend=trend,
            volatility=volatility,
            max_drawdown=drawdown,
        )

    async def compare(self, symbol: str, timeframe: str) -> CompareSnapshot:
        snapshot = await self.get_snapshot(symbol, timeframe)
        total_return = snapshot.returns.get("1Y")
        if total_return is None:
            total_return = next(iter(snapshot.returns.values()), 0.0)
        return CompareSnapshot(
            symbol=snapshot.symbol,
            total_return=total_return,
            volatility=snapshot.volatility,
            max_drawdown=snapshot.max_drawdown,
            trend=snapshot.trend,
        )

    def _returns_from_series(self, points: list[PricePoint]) -> dict[str, float]:
        closes = [point.close for point in points]
        returns: dict[str, float] = {}
        for label, days in return_windows().items():
            if len(closes) <= days:
                continue
            past = closes[-days - 1]
            present = closes[-1]
            if past == 0:
                continue
            returns[label] = (present / past) - 1
        return returns

    def _volatility(self, closes: list[float]) -> float:
        if len(closes) < 2:
            return 0.0
        returns = []
        for previous, current in zip(closes, closes[1:]):
            if previous == 0:
                continue
            returns.append((current / previous) - 1)
        if not returns:
            return 0.0
        mean_value = sum(returns) / len(returns)
        variance = sum((value - mean_value) ** 2 for value in returns) / len(returns)
        return variance ** 0.5

    def _max_drawdown(self, closes: list[float]) -> float:
        peak = closes[0]
        max_drawdown = 0.0
        for close in closes:
            if close > peak:
                peak = close
            if peak:
                drawdown = (close / peak) - 1
                max_drawdown = min(max_drawdown, drawdown)
        return max_drawdown

    def _trend_description(self, closes: list[float], timeframe_days: int) -> str:
        if len(closes) < 3:
            return "Insufficient data"
        sample = closes[-min(len(closes), max(timeframe_days, 20)):]
        delta = (sample[-1] / sample[0]) - 1 if sample[0] else 0
        volatility = self._volatility(sample)
        if delta >= 0.2:
            direction = "Strong uptrend"
        elif delta >= 0.05:
            direction = "Moderate uptrend"
        elif delta <= -0.2:
            direction = "Strong downtrend"
        elif delta <= -0.05:
            direction = "Moderate downtrend"
        else:
            direction = "Sideways"
        if volatility >= 0.04:
            return f"{direction} with high volatility"
        if volatility >= 0.02:
            return f"{direction} with moderate volatility"
        return f"{direction} with low volatility"
