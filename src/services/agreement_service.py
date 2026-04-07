from dataclasses import dataclass

from ..models import AgreementCluster, NewsItem
from ..utils.text import compact_claim, contains_rumor_language, similarity


_SOURCE_WEIGHTS = {
    "reuters": 1.0,
    "associated press": 1.0,
    "ap": 1.0,
    "bloomberg": 0.95,
    "wall street journal": 0.95,
    "cnbc": 0.85,
    "marketwatch": 0.8,
    "benzinga": 0.65,
    "motley fool": 0.55,
    "seeking alpha": 0.7,
    "yahoo": 0.65,
}


@dataclass(slots=True)
class ClusterBucket:
    key: str
    items: list[NewsItem]


class AgreementService:
    def _source_weight(self, publisher: str) -> float:
        normalized = publisher.strip().lower()
        for name, weight in _SOURCE_WEIGHTS.items():
            if name in normalized:
                return weight
        return 0.6

    def _cluster_items(self, items: list[NewsItem]) -> list[ClusterBucket]:
        buckets: list[ClusterBucket] = []
        for item in items:
            matched = None
            for bucket in buckets:
                if similarity(bucket.items[0].title, item.title) >= 0.72:
                    matched = bucket
                    break
            if matched:
                matched.items.append(item)
            else:
                buckets.append(ClusterBucket(key=compact_claim(item.title), items=[item]))
        return buckets

    def compute(self, items: list[NewsItem]) -> list[AgreementCluster]:
        clusters: list[AgreementCluster] = []
        for bucket in self._cluster_items(items):
            unique_publishers = []
            seen_publishers = set()
            for item in bucket.items:
                publisher_key = item.publisher.lower().strip()
                if publisher_key not in seen_publishers:
                    seen_publishers.add(publisher_key)
                    unique_publishers.append(item.publisher)
            score = sum(self._source_weight(item.publisher) for item in bucket.items)
            if score >= 4.5 or len(unique_publishers) >= 5:
                level = "High"
            elif score >= 2.5 or len(unique_publishers) >= 3:
                level = "Medium"
            else:
                level = "Low"
            warnings: list[str] = []
            if len(unique_publishers) <= 2:
                warnings.append("⚠️ Low Confirmation — limited independent coverage")
            if any(contains_rumor_language(item.title + " " + item.summary) for item in bucket.items):
                warnings.append("⚠️ Unconfirmed / Rumor — verify before acting")
            duplicate_ratio = 1 - (len(unique_publishers) / max(len(bucket.items), 1))
            explanation_parts = []
            if len(unique_publishers) <= 1:
                explanation_parts.append("only 1 unique publisher")
            elif len(unique_publishers) == 2:
                explanation_parts.append("only 2 unique publishers")
            if duplicate_ratio >= 0.5:
                explanation_parts.append("headline duplicates detected")
            if warnings and not explanation_parts:
                explanation_parts.append("thin source support")
            explanation = ", ".join(explanation_parts) if explanation_parts else "multiple independent sources support this claim"
            clusters.append(
                AgreementCluster(
                    claim=bucket.key,
                    score=round(score, 2),
                    level=level,
                    source_count=len(unique_publishers),
                    sources=unique_publishers,
                    warning_labels=warnings,
                    explanation=explanation,
                    items=sorted(bucket.items, key=lambda item: item.published_at, reverse=True),
                )
            )
        clusters.sort(key=lambda cluster: (cluster.score, cluster.source_count), reverse=True)
        return clusters
