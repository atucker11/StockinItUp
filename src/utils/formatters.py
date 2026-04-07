from datetime import datetime

import discord

from ..models import AgreementCluster, NewsItem, PriceSnapshot, Recommendation, SentimentSummary


def pct(value: float) -> str:
    return f"{value * 100:+.2f}%"


def usd(value: float) -> str:
    return f"${value:,.2f}"


def dt(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


def news_line(item: NewsItem) -> str:
    return f"[{item.title}]({item.url}) — {item.publisher} ({dt(item.published_at)})"


def build_stock_embed(
    snapshot: PriceSnapshot,
    sentiment: SentimentSummary,
    agreements: list[AgreementCluster],
    recommendation: Recommendation,
    detail: str,
) -> discord.Embed:
    embed = discord.Embed(title=f"{snapshot.symbol} Research Snapshot")
    returns_lines = [f"{key}: {pct(value)}" for key, value in snapshot.returns.items()]
    embed.add_field(
        name="Price Snapshot",
        value=(
            f"Current: {usd(snapshot.current_price)}\\n"
            f"Range: {usd(snapshot.range_low)} — {usd(snapshot.range_high)}\\n"
            f"Trend: {snapshot.trend}\\n"
            f"Volatility: {snapshot.volatility:.2f}\\n"
            f"Max drawdown: {pct(snapshot.max_drawdown)}\\n"
            + "\\n".join(returns_lines[:7])
        ),
        inline=False,
    )
    embed.add_field(
        name="Sentiment Counters",
        value=(
            f"Positive: {sentiment.positive}\\n"
            f"Negative: {sentiment.negative}\\n"
            f"Neutral: {sentiment.neutral}\\n"
            f"Average score: {sentiment.average_score:+.2f}"
        ),
        inline=False,
    )
    agreement_lines = []
    for cluster in agreements[:3]:
        warning = " | ".join(cluster.warning_labels) if cluster.warning_labels else "No warning"
        agreement_lines.append(
            f"{cluster.claim}\\nAgreement: {cluster.source_count} sources ({cluster.level})\\n{warning}"
        )
    embed.add_field(
        name="Agreement Score",
        value="\\n\\n".join(agreement_lines) if agreement_lines else "No major claims clustered.",
        inline=False,
    )
    recommendation_text = (
        f"{recommendation.mode.title()} mode: {recommendation.label}\\n"
        f"Confidence: {recommendation.confidence}/100\\n"
        + "\\n".join(f"• {reason}" for reason in recommendation.reasons)
    )
    if detail == "full" and recommendation.assumptions:
        recommendation_text += "\\n\\nAssumptions\\n" + "\\n".join(f"• {item}" for item in recommendation.assumptions)
    embed.add_field(name="Recommendation", value=recommendation_text, inline=False)
    citations = recommendation.citations[:5]
    embed.add_field(
        name="Citations",
        value="\\n".join(news_line(item) for item in citations) if citations else "No source links available.",
        inline=False,
    )
    embed.set_footer(text="Informational only. Not financial advice.")
    return embed


def build_sentiment_embed(symbol: str, sentiment: SentimentSummary, agreements: list[AgreementCluster]) -> discord.Embed:
    embed = discord.Embed(title=f"{symbol} Sentiment Overview")
    embed.add_field(
        name="Counters",
        value=(
            f"Positive: {sentiment.positive}\\n"
            f"Negative: {sentiment.negative}\\n"
            f"Neutral: {sentiment.neutral}\\n"
            f"Average score: {sentiment.average_score:+.2f}"
        ),
        inline=False,
    )
    bullish = "\\n".join(news_line(item) for item in sentiment.top_bullish[:3]) or "No bullish headlines found."
    bearish = "\\n".join(news_line(item) for item in sentiment.top_bearish[:3]) or "No bearish headlines found."
    embed.add_field(name="Top 3 Bullish", value=bullish, inline=False)
    embed.add_field(name="Top 3 Bearish", value=bearish, inline=False)
    agreement_text = "\\n\\n".join(
        f"{cluster.claim}\\nAgreement: {cluster.source_count} sources ({cluster.level})"
        for cluster in agreements[:3]
    ) or "No clustered claims."
    embed.add_field(name="Agreement", value=agreement_text, inline=False)
    embed.set_footer(text="Informational only. Not financial advice.")
    return embed
