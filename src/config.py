from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    discord_token: str = Field(default="", alias="DISCORD_TOKEN")
    discord_guild_id: int | None = Field(default=None, alias="DISCORD_GUILD_ID")
    finnhub_api_key: str = Field(default="", alias="FINNHUB_API_KEY")
    alpha_vantage_api_key: str | None = Field(default=None, alias="ALPHA_VANTAGE_API_KEY")
    request_timeout_seconds: int = Field(default=20, alias="REQUEST_TIMEOUT_SECONDS")
    cache_ttl_seconds: int = Field(default=900, alias="CACHE_TTL_SECONDS")
    default_news_limit: int = Field(default=25, alias="DEFAULT_NEWS_LIMIT")
    sqlite_path: str = Field(default="data/watchlists.db", alias="SQLITE_PATH")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    default_market_category: str = Field(default="general", alias="DEFAULT_MARKET_CATEGORY")
    exclude_penny_stocks: bool = Field(default=True, alias="EXCLUDE_PENNY_STOCKS")
    min_market_cap: int = Field(default=0, alias="MIN_MARKET_CAP")
    max_tickers_in_trending: int = Field(default=10, alias="MAX_TICKERS_IN_TRENDING")
    default_timezone: str = Field(default="UTC", alias="DEFAULT_TIMEZONE")

    @property
    def sqlite_path_obj(self) -> Path:
        path = Path(self.sqlite_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
