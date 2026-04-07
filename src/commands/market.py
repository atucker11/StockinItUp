import logging

import discord
from discord import app_commands
from discord.ext import commands

from ..models import CompareSnapshot
from ..utils.formatters import build_sentiment_embed, build_stock_embed, news_line, pct


log = logging.getLogger(__name__)


_TIMEFRAME_CHOICES = [
    app_commands.Choice(name="24h", value="24h"),
    app_commands.Choice(name="7d", value="7d"),
    app_commands.Choice(name="30d", value="30d"),
    app_commands.Choice(name="90d", value="90d"),
    app_commands.Choice(name="1y", value="1y"),
    app_commands.Choice(name="2y", value="2y"),
    app_commands.Choice(name="5y", value="5y"),
]

_DETAIL_CHOICES = [
    app_commands.Choice(name="brief", value="brief"),
    app_commands.Choice(name="full", value="full"),
]

_MODE_CHOICES = [
    app_commands.Choice(name="conservative", value="conservative"),
    app_commands.Choice(name="bold", value="bold"),
]


class MarketCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="stock", description="Analyze a ticker with price, news, sentiment and recommendation.")
    @app_commands.describe(ticker="Ticker symbol", timeframe="Analysis window", detail="Output detail", mode="Recommendation style")
    @app_commands.choices(timeframe=_TIMEFRAME_CHOICES, detail=_DETAIL_CHOICES, mode=_MODE_CHOICES)
    async def stock(
        self,
        interaction: discord.Interaction,
        ticker: str,
        timeframe: str = "30d",
        detail: str = "brief",
        mode: str = "conservative",
    ) -> None:
        await interaction.response.defer(thinking=True)
        try:
            symbol = ticker.upper().strip()
            snapshot = await self.bot.market_data_service.get_snapshot(symbol, timeframe)
            items = await self.bot.news_service.get_symbol_news(symbol, timeframe)
            sentiment = self.bot.sentiment_service.summarize(items)
            agreements = self.bot.agreement_service.compute(items)
            recommendation = self.bot.recommendation_service.build(snapshot, sentiment, agreements, mode)
            embed = build_stock_embed(snapshot, sentiment, agreements, recommendation, detail)
            points = await self.bot.market_data_service.get_price_series(symbol, timeframe)
            chart = self.bot.chart_service.build_file(symbol, points)
            if chart:
                embed.set_image(url=f"attachment://{chart.filename}")
                await interaction.followup.send(embed=embed, file=chart)
            else:
                await interaction.followup.send(embed=embed)
        except Exception as error:
            log.exception("/stock failed for %s", ticker, exc_info=error)
            await interaction.followup.send(
                f"Could not load stock data for {ticker.upper().strip()}. Please verify the ticker and API setup.",
                ephemeral=True,
            )

    @app_commands.command(name="sentiment", description="Show sentiment counters and headline balance for a ticker.")
    @app_commands.describe(ticker="Ticker symbol", timeframe="Analysis window")
    @app_commands.choices(timeframe=_TIMEFRAME_CHOICES)
    async def sentiment(self, interaction: discord.Interaction, ticker: str, timeframe: str = "30d") -> None:
        await interaction.response.defer(thinking=True)
        try:
            symbol = ticker.upper().strip()
            items = await self.bot.news_service.get_symbol_news(symbol, timeframe)
            sentiment = self.bot.sentiment_service.summarize(items)
            agreements = self.bot.agreement_service.compute(items)
            embed = build_sentiment_embed(symbol, sentiment, agreements)
            await interaction.followup.send(embed=embed)
        except Exception as error:
            log.exception("/sentiment failed for %s", ticker, exc_info=error)
            await interaction.followup.send(
                f"Could not load sentiment data for {ticker.upper().strip()}. Please verify the ticker and API setup.",
                ephemeral=True,
            )

    @app_commands.command(name="compare", description="Compare two tickers over the same timeframe.")
    @app_commands.describe(ticker1="First ticker", ticker2="Second ticker", timeframe="Analysis window")
    @app_commands.choices(timeframe=_TIMEFRAME_CHOICES)
    async def compare(self, interaction: discord.Interaction, ticker1: str, ticker2: str, timeframe: str = "1y") -> None:
        await interaction.response.defer(thinking=True)
        try:
            left = await self.bot.market_data_service.compare(ticker1.upper().strip(), timeframe)
            right = await self.bot.market_data_service.compare(ticker2.upper().strip(), timeframe)
            embed = discord.Embed(title=f"Compare {left.symbol} vs {right.symbol}")
            embed.add_field(name=left.symbol, value=self._compare_block(left), inline=True)
            embed.add_field(name=right.symbol, value=self._compare_block(right), inline=True)
            embed.set_footer(text="Informational only. Not financial advice.")
            await interaction.followup.send(embed=embed)
        except Exception as error:
            log.exception("/compare failed for %s and %s", ticker1, ticker2, exc_info=error)
            await interaction.followup.send("Could not compare those tickers right now.", ephemeral=True)

    @app_commands.command(name="trending", description="Show the most-mentioned trending tickers from recent market news.")
    @app_commands.describe(timeframe="Trending window")
    @app_commands.choices(timeframe=_TIMEFRAME_CHOICES)
    async def trending(self, interaction: discord.Interaction, timeframe: str = "24h") -> None:
        await interaction.response.defer(thinking=True)
        try:
            ranked = await self.bot.trending_service.compute(timeframe)
            embed = discord.Embed(title=f"Trending tickers in the last {timeframe}")
            if not ranked:
                embed.description = "No trending tickers found for the selected window."
            for index, row in enumerate(ranked[:10], start=1):
                headlines = "\n".join(news_line(item) for item in row["headlines"])
                value = f"{row['why']}\n\n{headlines}".strip()
                if len(value) > 1000:
                    value = value[:997] + "..."
                embed.add_field(
                    name=f"{index}. {row['symbol']} | score {row['score']}",
                    value=value,
                    inline=False,
                )
            embed.set_footer(text="Informational only. Not financial advice.")
            await interaction.followup.send(embed=embed)
        except Exception as error:
            log.exception("/trending failed", exc_info=error)
            await interaction.followup.send("Could not load trending tickers right now.", ephemeral=True)

    watchlist = app_commands.Group(name="watchlist", description="Manage your personal stock watchlist.")

    @watchlist.command(name="add", description="Add a ticker to your watchlist.")
    async def watchlist_add(self, interaction: discord.Interaction, ticker: str) -> None:
        if not interaction.guild_id:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return
        symbol = ticker.upper().strip()
        await self.bot.watchlist_store.add(interaction.guild_id, interaction.user.id, symbol)
        await interaction.response.send_message(f"Added {symbol} to your watchlist.", ephemeral=True)

    @watchlist.command(name="remove", description="Remove a ticker from your watchlist.")
    async def watchlist_remove(self, interaction: discord.Interaction, ticker: str) -> None:
        if not interaction.guild_id:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return
        symbol = ticker.upper().strip()
        await self.bot.watchlist_store.remove(interaction.guild_id, interaction.user.id, symbol)
        await interaction.response.send_message(f"Removed {symbol} from your watchlist.", ephemeral=True)

    @watchlist.command(name="summary", description="Show your watchlist.")
    async def watchlist_summary(self, interaction: discord.Interaction) -> None:
        if not interaction.guild_id:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return
        symbols = await self.bot.watchlist_store.list_for_user(interaction.guild_id, interaction.user.id)
        embed = discord.Embed(title=f"{interaction.user.display_name}'s watchlist")
        embed.description = "\n".join(f"• {symbol}" for symbol in symbols) if symbols else "Your watchlist is empty."
        embed.set_footer(text="Informational only. Not financial advice.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def _compare_block(self, snapshot: CompareSnapshot) -> str:
        return (
            f"Return: {pct(snapshot.total_return)}\n"
            f"Volatility: {snapshot.volatility:.2f}\n"
            f"Max drawdown: {pct(snapshot.max_drawdown)}\n"
            f"Trend: {snapshot.trend}"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MarketCog(bot))
