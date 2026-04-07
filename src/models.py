from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


SentimentLabel = Literal["bullish", "bearish", "neutral"]


@dataclass(slots=True)
class NewsItem:
    symbol: str
    title: str
    summary: str
    publisher: str
    url: str
    published_at: datetime
    related_symbols: list[str] = field(default_factory=list)
    sentiment_score: float = 0.0
    sentiment_label: SentimentLabel = "neutral"


@dataclass(slots=True)
class PricePoint:
    timestamp: datetime
    close: float


@dataclass(slots=True)
class PriceSnapshot:
    symbol: str
    current_price: float
    returns: dict[str, float]
    range_low: float
    range_high: float
    trend: str
    volatility: float
    max_drawdown: float


@dataclass(slots=True)
class SentimentSummary:
    positive: int
    negative: int
    neutral: int
    average_score: float
    top_bullish: list[NewsItem]
    top_bearish: list[NewsItem]


@dataclass(slots=True)
class AgreementCluster:
    claim: str
    score: float
    level: str
    source_count: int
    sources: list[str]
    warning_labels: list[str]
    explanation: str
    items: list[NewsItem]


@dataclass(slots=True)
class Recommendation:
    mode: str
    label: str
    confidence: int
    reasons: list[str]
    assumptions: list[str]
    citations: list[NewsItem]


@dataclass(slots=True)
class CompareSnapshot:
    symbol: str
    total_return: float
    volatility: float
    max_drawdown: float
    trend: str
