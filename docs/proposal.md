# Proposal for TonyToeTap

## Recommended architecture

- Python
- `discord.py` slash commands
- `aiohttp` for async API calls
- SQLite for watchlists and light persistence
- Modular service layer for market data, news, sentiment, agreement scoring, recommendations and embeds
- Caching layer to reduce API pressure
- Railway or Render deployment

## Phase 1 free data sources

Primary:
- Finnhub for company news, market news, quotes and candles

Optional add-on:
- Alpha Vantage for future enrichment and optional data diversification

## What Phase 1 can reliably do

- Pull historical price data
- Compute 1D / 1W / 1M / 3M / 6M / 1Y / 5Y returns where available
- Build trend, volatility and drawdown summaries
- Pull recent news per ticker
- Detect trending tickers from recent article flow
- Count bullish, bearish and neutral headline balance
- Produce both conservative and bold recommendation outputs
- Compute an agreement score with source weighting and warning labels
- Keep the project modular for premium-source upgrades later

## How most-mentioned stocks are computed

- Pull recent market news over the selected window
- Extract related tickers from provider metadata
- Weight each mention by source quality and recency
- Deduplicate repeated headlines
- Rank symbols by weighted mention score
- Return the top names with a short explanation and key headlines

## How agreement score works

For each major claim cluster:
- Similar headlines are grouped together
- Unique publishers are counted
- Higher-trust publishers receive higher weights
- Claims with only one or two unique publishers are flagged
- Rumor language triggers an explicit warning label
- Output includes source list and a short explanation of why the warning was triggered

## Sentiment classification and cost control

Phase 1 uses a lightweight local sentiment layer on headlines and short summaries, so there is no per-request LLM cost. If needed later, it can be upgraded to a stronger ML or LLM classifier behind a feature flag.

## Engineering approach

- Secure environment variables
- Async requests with timeouts
- Caching to reduce duplicate fetches
- Modular providers so premium APIs can be added later
- Ready for scheduled posting and public-server hardening

## Phase 2 premium upgrade path

Possible premium add-ons:
- Bloomberg
- Morningstar
- Seeking Alpha
- MarketWatch

Those would require valid subscriptions or licensed commercial access depending on the source and usage rights. The codebase is structured so these can be added as separate provider modules without rewriting the command layer.
