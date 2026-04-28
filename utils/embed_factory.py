from __future__ import annotations

from datetime import datetime, UTC

import discord

from utils.constants import EMBED_COLOR, EMBED_FOOTER


def make_embed(title: str, description: str | None = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=EMBED_COLOR,
        timestamp=datetime.now(UTC),
    )
    embed.set_footer(text=EMBED_FOOTER)
    return embed
