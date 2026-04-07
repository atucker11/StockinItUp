from statistics import mean

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from ..models import NewsItem, SentimentSummary


class SentimentService:
    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer()

    def score_items(self, items: list[NewsItem]) -> list[NewsItem]:
        scored: list[NewsItem] = []
        for item in items:
            compound = self.analyzer.polarity_scores(f"{item.title}. {item.summary}")["compound"]
            if compound >= 0.2:
                label = "bullish"
            elif compound <= -0.2:
                label = "bearish"
            else:
                label = "neutral"
            item.sentiment_score = compound
            item.sentiment_label = label
            scored.append(item)
        return scored

    def summarize(self, items: list[NewsItem]) -> SentimentSummary:
        scored = self.score_items(items)
        bullish = [item for item in scored if item.sentiment_label == "bullish"]
        bearish = [item for item in scored if item.sentiment_label == "bearish"]
        neutral = [item for item in scored if item.sentiment_label == "neutral"]
        average_score = mean([item.sentiment_score for item in scored]) if scored else 0.0
        top_bullish = sorted(bullish, key=lambda item: item.sentiment_score, reverse=True)
        top_bearish = sorted(bearish, key=lambda item: item.sentiment_score)
        return SentimentSummary(
            positive=len(bullish),
            negative=len(bearish),
            neutral=len(neutral),
            average_score=average_score,
            top_bullish=top_bullish[:3],
            top_bearish=top_bearish[:3],
        )
