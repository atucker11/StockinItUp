import re


_COMPANY_ALIASES = {
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "NVIDIA": "NVDA",
    "TESLA": "TSLA",
    "AMAZON": "AMZN",
    "ALPHABET": "GOOGL",
    "GOOGLE": "GOOGL",
    "META": "META",
    "NETFLIX": "NFLX",
    "AMD": "AMD",
    "ADVANCED MICRO DEVICES": "AMD",
    "PALANTIR": "PLTR",
    "BERKSHIRE": "BRK.B",
    "JPMORGAN": "JPM",
    "COINBASE": "COIN",
    "ROBINHOOD": "HOOD",
    "SUPER MICRO": "SMCI",
    "MICROSTRATEGY": "MSTR",
    "MARATHON DIGITAL": "MARA",
    "RIVIAN": "RIVN",
    "SOFI": "SOFI",
    "INTEL": "INTC",
    "QUALCOMM": "QCOM",
    "SHOPIFY": "SHOP",
    "UBER": "UBER",
    "AIRBNB": "ABNB",
    "SNOWFLAKE": "SNOW",
    "SALESFORCE": "CRM",
    "PAYPAL": "PYPL",
    "BLOCK": "SQ",
}


_STOPWORDS = {
    "A",
    "AI",
    "AN",
    "AND",
    "ARE",
    "AT",
    "BE",
    "BY",
    "CEO",
    "CFO",
    "COO",
    "ETF",
    "FOR",
    "FROM",
    "HOW",
    "IN",
    "INTO",
    "IS",
    "IT",
    "ITS",
    "MAY",
    "NEW",
    "NOT",
    "NOW",
    "OF",
    "ON",
    "OR",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "SAYS",
    "SO",
    "THE",
    "TO",
    "US",
    "USD",
    "WILL",
    "WITH",
}


def normalize_symbol(value: str) -> str:
    return value.strip().upper().replace("$", "")


def split_related_symbols(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts = re.split(r"[,\s]+", raw)
    return [normalize_symbol(part) for part in parts if part.strip()]


def likely_us_equity(symbol: str) -> bool:
    if not symbol:
        return False
    if "." in symbol or "-" in symbol:
        return False
    if not 1 <= len(symbol) <= 5:
        return False
    return symbol.isalpha()


def extract_symbols_from_text(text: str) -> list[str]:
    if not text:
        return []
    normalized_text = f" {text.upper()} "
    found: list[str] = []
    seen: set[str] = set()
    for name, ticker in _COMPANY_ALIASES.items():
        if f" {name} " in normalized_text and ticker not in seen:
            found.append(ticker)
            seen.add(ticker)
    for match in re.findall(r"(?<![A-Za-z])\$?[A-Z]{1,5}(?![A-Za-z])", text):
        symbol = normalize_symbol(match)
        if symbol in _STOPWORDS:
            continue
        if likely_us_equity(symbol) and symbol not in seen:
            found.append(symbol)
            seen.add(symbol)
    return found
