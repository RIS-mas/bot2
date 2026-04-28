from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.constants import COMMAND_PREFIX
from utils.embed_factory import make_embed

load_dotenv()

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOGGER = logging.getLogger("enlighten_bot")


class EnlightenBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )

    async def setup_hook(self) -> None:
        for ext in ("cogs.invites", "cogs.pricing", "cogs.tools", "cogs.pricelist_ui"):
            await self.load_extension(ext)
            LOGGER.info("Loaded extension: %s", ext)
        await self.tree.sync()
        LOGGER.info("Application commands synced.")

    async def on_ready(self) -> None:
        LOGGER.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "unknown")


bot = EnlightenBot()


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.CommandNotFound):
        embed = make_embed("Error", "Unknown command. Use `>help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        embed = make_embed("Permission Denied", "You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = make_embed("Missing Argument", f"Missing argument: `{error.param.name}`")
    elif isinstance(error, commands.BadArgument):
        embed = make_embed("Invalid Input", "Please check your argument types and try again.")
    elif isinstance(error, commands.CommandOnCooldown):
        embed = make_embed("Cooldown", f"Try again in `{error.retry_after:.1f}` seconds.")
    else:
        LOGGER.exception("Unhandled command error", exc_info=error)
        embed = make_embed("Unexpected Error", "Something went wrong while processing that command.")

    await ctx.send(embed=embed)


async def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable.")

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot shutdown requested by user.")
