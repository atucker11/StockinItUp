from datetime import UTC, datetime, timedelta


_TIMEFRAME_DAYS = {
    "24h": 1,
    "7d": 7,
    "30d": 30,
    "90d": 90,
    "1y": 365,
    "2y": 730,
    "5y": 1825,
}


_RETURN_WINDOWS = {
    "1D": 1,
    "1W": 7,
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "5Y": 1825,
}


def now_utc() -> datetime:
    return datetime.now(UTC)


def timeframe_to_days(timeframe: str) -> int:
    normalized = timeframe.lower()
    if normalized not in _TIMEFRAME_DAYS:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    return _TIMEFRAME_DAYS[normalized]


def timeframe_window(timeframe: str) -> tuple[datetime, datetime]:
    end = now_utc()
    start = end - timedelta(days=timeframe_to_days(timeframe))
    return start, end


def extended_price_window(timeframe: str) -> tuple[datetime, datetime]:
    end = now_utc()
    start = end - timedelta(days=max(timeframe_to_days(timeframe), 1825))
    return start, end


def return_windows() -> dict[str, int]:
    return dict(_RETURN_WINDOWS)
