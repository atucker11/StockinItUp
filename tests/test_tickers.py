from src.utils.tickers import extract_symbols_from_text


def test_extract_symbols_from_aliases_and_ticker_tokens():
    symbols = extract_symbols_from_text('Apple rises while $NVDA and Tesla lead tech rally')
    assert 'AAPL' in symbols
    assert 'NVDA' in symbols
    assert 'TSLA' in symbols
