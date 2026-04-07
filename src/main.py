from .bot import StockResearchBot
from .config import settings
from .logger import configure_logging


def main() -> None:
    configure_logging()
    bot = StockResearchBot()
    bot.run(settings.discord_token)


if __name__ == "__main__":
    main()
