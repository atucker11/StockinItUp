from io import BytesIO

import discord
import matplotlib

from ..models import PricePoint


matplotlib.use("Agg")
from matplotlib import pyplot as plt


class ChartService:
    def build_file(self, symbol: str, points: list[PricePoint]) -> discord.File | None:
        if len(points) < 2:
            return None
        x = list(range(len(points)))
        y = [point.close for point in points]
        figure = plt.figure(figsize=(6, 2))
        axis = figure.add_subplot(111)
        axis.plot(x, y, linewidth=2)
        axis.set_title(f"{symbol} price trend")
        axis.set_xticks([])
        axis.grid(True, alpha=0.2)
        buffer = BytesIO()
        figure.tight_layout()
        figure.savefig(buffer, format="png", dpi=160)
        plt.close(figure)
        buffer.seek(0)
        return discord.File(buffer, filename=f"{symbol.lower()}_sparkline.png")
