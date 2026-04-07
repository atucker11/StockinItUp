# Setup Guide

## 1. Discord

Create a bot application in the Discord Developer Portal and invite it with:
- `bot`
- `applications.commands`

## 2. Environment variables

Copy `.env.example` to `.env` and fill in:
- `DISCORD_TOKEN`
- `FINNHUB_API_KEY`
- `ALPHA_VANTAGE_API_KEY` if you want the optional add-on
- `DISCORD_GUILD_ID` if you want instant guild-level command sync while testing

## 3. Install

```bash
pip install -r requirements.txt
```

## 4. Run locally

```bash
python -m src.main
```

## 5. Railway deploy

- Create a new Railway project
- Add the environment variables
- Deploy from the repo root
- Start command: `python -m src.main`

## 6. Notes

- Review provider licenses before public or commercial rollout
- Keep summaries short and link to original sources
- The bot already includes the disclaimer footer in embeds
