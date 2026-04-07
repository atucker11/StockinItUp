# Stock Research Discord Bot

A modular Phase 1 Discord bot for private servers that posts trending stock news, supports on-demand ticker research, computes agreement scores, labels weakly supported claims, and returns both bold and conservative recommendation styles.

## Included

- Slash commands with `discord.py`
- Price history, returns, volatility, drawdown and trend description
- Market news and company news ingestion
- Trending ticker detection from incoming articles
- Sentiment classification with lightweight local scoring
- Agreement scoring with source weighting and warning labels
- Watchlist storage with SQLite
- Embed formatting and optional sparkline chart images
- Railway-ready project layout
- Setup guide, admin guide, and client proposal

## Phase 1 data approach

The default implementation is built around Finnhub for market and company news plus historical candle/quote data, with Alpha Vantage kept as an optional add-on for premium-quality extensions and future source diversification.

Before production use, review each provider's license and plan limits carefully.

## Quick start

1. Create a Discord bot application and invite it with the `applications.commands` and `bot` scopes.
2. Copy `.env.example` to `.env`.
3. Add your Discord token and API keys.
4. Install dependencies:
   `pip install -r requirements.txt`
5. Start the bot:
   `python -m src.main`

## Commands

- `/trending timeframe:24h`
- `/stock ticker:AAPL timeframe:30d detail:brief mode:conservative`
- `/sentiment ticker:AAPL timeframe:30d`
- `/compare ticker1:AAPL ticker2:MSFT timeframe:1y`
- `/watchlist add ticker:AAPL`
- `/watchlist remove ticker:AAPL`
- `/watchlist summary`

## Notes

This package is intentionally modular so premium providers can be added later without rewriting command handlers.

Every output should include an informational disclaimer and only brief original summaries with links to original publishers.
