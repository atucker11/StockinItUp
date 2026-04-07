from datetime import UTC, datetime, timedelta

from src.models import NewsItem
from src.services.agreement_service import AgreementService


def test_low_confirmation_warning_when_only_one_publisher():
    now = datetime.now(UTC)
    items = [
        NewsItem(
            symbol="AAPL",
            title="Apple beats earnings estimates on strong iPhone demand",
            summary="Apple reported strong quarterly results.",
            publisher="Reuters",
            url="https://example.com/1",
            published_at=now,
        ),
        NewsItem(
            symbol="AAPL",
            title="Apple beats earnings estimates on strong iPhone demand",
            summary="Another version of the same report.",
            publisher="Reuters",
            url="https://example.com/2",
            published_at=now - timedelta(minutes=10),
        ),
    ]
    clusters = AgreementService().compute(items)
    assert clusters
    assert "⚠️ Low Confirmation — limited independent coverage" in clusters[0].warning_labels
