# Admin Guide

## Recommended channels

- `#market-trending`
- `#stock-research`
- `#watchlists`

## Permissions

Keep the bot in a private server first. For a future public server, add:
- command cooldowns
- stricter per-user rate limits
- role-based access for heavy commands
- a scheduled task channel for automatic trending posts

## Commands

- `/trending timeframe:24h`
- `/stock ticker:AAPL timeframe:30d detail:brief mode:conservative`
- `/sentiment ticker:AAPL timeframe:30d`
- `/compare ticker1:AAPL ticker2:MSFT timeframe:1y`
- `/watchlist add ticker:AAPL`
- `/watchlist remove ticker:AAPL`
- `/watchlist summary`

## Agreement score behavior

The bot clusters similar headlines, counts unique publishers, weights higher-trust sources more heavily, and adds warning labels when source support is weak or rumor language appears.

## Disclaimer

All outputs are informational only and not financial advice.
