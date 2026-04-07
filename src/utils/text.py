import re
from difflib import SequenceMatcher


_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "after",
    "amid", "as", "by", "from", "at", "is", "are", "be", "stock", "shares", "share"
}

_RUMOR_WORDS = {"rumor", "unconfirmed", "reportedly", "allegedly", "speculation", "may", "could"}


def normalize_text(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\\s]", " ", value.lower())
    cleaned = re.sub(r"\\s+", " ", cleaned).strip()
    return cleaned


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def compact_claim(title: str) -> str:
    tokens = [token for token in normalize_text(title).split() if token not in _STOPWORDS]
    if not tokens:
        return title.strip()[:120]
    return " ".join(tokens[:10]).title()


def contains_rumor_language(text: str) -> bool:
    normalized = set(normalize_text(text).split())
    return any(word in normalized for word in _RUMOR_WORDS)
