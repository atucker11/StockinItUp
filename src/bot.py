import logging

import discord
from discord import app_commands
from discord.ext import commands

from .cache import AsyncTTLCache
from .config import settings
from .providers.alpha_vantage import AlphaVantageClient
from .providers.finnhub import FinnhubClient
from .providers.http import HTTPClient
from .services.agreement_service import AgreementService
from .services.chart_service import ChartService
from .services.market_data_service import MarketDataService
from .services.news_service import NewsService
from .services.recommendation_service import RecommendationService
from .services.sentiment_service import SentimentService
from .services.trending_service import TrendingService
from .storage.watchlist_store import WatchlistStore


log = logging.getLogger(__name__)


class StockResearchBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.cache = AsyncTTLCache()
        self.http_client = HTTPClient()
        self.finnhub = FinnhubClient(self.http_client, self.cache)
        self.alpha_vantage = AlphaVantageClient(self.http_client, self.cache)
        self.news_service = NewsService(self.finnhub)
        self.sentiment_service = SentimentService()
        self.agreement_service = AgreementService()
        self.market_data_service = MarketDataService(self.finnhub)
        self.recommendation_service = RecommendationService()
        self.trending_service = TrendingService(self.news_service)
        self.chart_service = ChartService()
        self.watchlist_store = WatchlistStore()
        self.tree.on_error = self.on_app_command_error

    async def setup_hook(self) -> None:
        await self.http_client.start()
        await self.watchlist_store.init()
        await self.load_extension("src.commands.market")
        if settings.discord_guild_id:
            guild = discord.Object(id=settings.discord_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %s guild commands", len(synced))
        else:
            synced = await self.tree.sync()
            log.info("Synced %s global commands", len(synced))

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        log.exception("App command failed", exc_info=error)
        message = "The command failed to run. Please verify the API keys and try again."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    async def close(self) -> None:
        await self.http_client.close()
        await super().close()
