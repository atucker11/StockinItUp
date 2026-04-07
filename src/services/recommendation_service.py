from ..models import AgreementCluster, PriceSnapshot, Recommendation, SentimentSummary


class RecommendationService:
    def build(
        self,
        snapshot: PriceSnapshot,
        sentiment: SentimentSummary,
        agreements: list[AgreementCluster],
        mode: str,
    ) -> Recommendation:
        price_score = self._price_score(snapshot)
        sentiment_score = self._sentiment_score(sentiment)
        agreement_score = self._agreement_score(agreements)
        composite = (price_score * 0.35) + (sentiment_score * 0.35) + (agreement_score * 0.30)
        if mode == "bold":
            if composite >= 0.2:
                label = "Buy"
            elif composite <= -0.15:
                label = "Avoid"
            else:
                label = "Hold"
            confidence = min(95, max(35, int(55 + composite * 60)))
        else:
            if composite >= 0.3:
                label = "Buy"
            elif composite <= -0.25:
                label = "Avoid"
            else:
                label = "Hold"
            confidence = min(85, max(30, int(50 + composite * 40)))
        reasons = self._reasons(snapshot, sentiment, agreements, mode)
        assumptions = self._assumptions(agreements, mode)
        citations = []
        for cluster in agreements[:3]:
            citations.extend(cluster.items[:2])
        return Recommendation(
            mode=mode,
            label=label,
            confidence=confidence,
            reasons=reasons[:6],
            assumptions=assumptions,
            citations=citations[:5],
        )

    def _price_score(self, snapshot: PriceSnapshot) -> float:
        one_month = snapshot.returns.get("1M", 0.0)
        three_month = snapshot.returns.get("3M", 0.0)
        one_year = snapshot.returns.get("1Y", 0.0)
        drawdown_penalty = abs(min(snapshot.max_drawdown, 0.0))
        score = (one_month * 0.8) + (three_month * 1.0) + (one_year * 0.6) - (drawdown_penalty * 0.8)
        return max(-1.0, min(1.0, score))

    def _sentiment_score(self, sentiment: SentimentSummary) -> float:
        total = sentiment.positive + sentiment.negative + sentiment.neutral
        if total == 0:
            return 0.0
        balance = (sentiment.positive - sentiment.negative) / total
        return max(-1.0, min(1.0, balance + sentiment.average_score))

    def _agreement_score(self, agreements: list[AgreementCluster]) -> float:
        if not agreements:
            return 0.0
        top = agreements[:3]
        level_points = {"High": 0.35, "Medium": 0.15, "Low": -0.1}
        total = 0.0
        for cluster in top:
            total += level_points.get(cluster.level, 0.0)
            if cluster.warning_labels:
                total -= 0.08 * len(cluster.warning_labels)
        return max(-1.0, min(1.0, total))

    def _reasons(
        self,
        snapshot: PriceSnapshot,
        sentiment: SentimentSummary,
        agreements: list[AgreementCluster],
        mode: str,
    ) -> list[str]:
        reasons = [
            f"Price trend reads as {snapshot.trend.lower()} with 1Y return at {snapshot.returns.get('1Y', 0.0) * 100:+.2f}%.",
            f"Headline mix shows {sentiment.positive} bullish vs {sentiment.negative} bearish articles.",
            f"Current max drawdown over the loaded window is {snapshot.max_drawdown * 100:+.2f}%.",
        ]
        if agreements:
            top = agreements[0]
            reasons.append(f"Top news driver has {top.source_count} distinct sources and a {top.level.lower()} agreement score.")
            if top.warning_labels:
                reasons.append("At least one major claim still has a weak-confirmation warning.")
        if mode == "bold":
            reasons.append("Bold mode assumes the recent narrative persists and no hidden negative catalyst breaks the trend.")
        else:
            reasons.append("Conservative mode discounts thinly confirmed stories and weights downside risk more heavily.")
        return reasons

    def _assumptions(self, agreements: list[AgreementCluster], mode: str) -> list[str]:
        assumptions = []
        if agreements:
            for cluster in agreements[:3]:
                assumptions.append(f"{cluster.claim}: {cluster.explanation}")
        if mode == "bold":
            assumptions.append("Momentum and news flow remain supportive in the near term.")
        else:
            assumptions.append("Conflicting headlines can reverse quickly, so conviction stays capped.")
        return assumptions
