from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

BASE_TITLE = "⟢ ENLIGHTEN COMMUNITY ⟣"
BASE_SUBTITLE = "BLOX FRUITS SERVICE PRICE LIST"
BASE_DESCRIPTION = "Use the buttons below to navigate categories."
FOOTER_TEXT = "ENLIGHTEN COMMUNITY SERVICE"

CATEGORY_DATA: dict[str, str] = {
    "Raids": (
        "◆ **RAIDS (EASY)**\n"
        "• 1–5 → 12M\n"
        "• 5–10 → 25M\n"
        "• 10–15 → 49.5M\n\n"
        "◆ **RAIDS (ADVANCED)**\n"
        "• 1–5 → 25M\n"
        "• 5–7 → 35M\n"
        "• 7–12 → 60.5M\n\n"
        "◆ **LAW RAIDS**\n"
        "• Per Raid → 5M"
    ),
    "Trials": (
        "• 1 Trial → 35M\n"
        "• 2 Trials → 65M\n"
        "• 3 Trials → 101M\n"
        "• 4 Trials → 132M\n"
        "• Max Race → 198M"
    ),
    "Sea Events": (
        "• Mirage → 71.5M\n"
        "• Sea Beast → 3M\n"
        "• Prehistoric → 77M\n"
        "• Leviathan → 198M\n"
        "• Ship Raids → 4M\n"
        "• Kitsune → 88M"
    ),
    "Bosses": (
        "• Darkbeard → 50M\n"
        "• Cake Prince → 40M\n"
        "• Rip Indra → 60.5M\n"
        "• Dough King → 77M\n"
        "• Tyrant → 30M"
    ),
    "Swords": (
        "• True Triple Katana → 100M (per sword)\n"
        "• Tushita → 90M\n"
        "• Yama → 90M\n"
        "• Cursed Dual Katana → 170M"
    ),
    "Beli": (
        "• 1M → 18M\n"
        "• 2M → 28M\n"
        "• 3.5M → 38M\n"
        "• 10M → 88M\n"
        "• 30M → 363M\n"
        "• 60M → 495M"
    ),
    "Mastery": "• To 300 → 104.5M\n• To 600 → 203.5M",
    "Bounty": (
        "• Raging Demon → 121M\n"
        "• 500K → 143M\n"
        "• 1M → 286M\n"
        "• 2M → 572M"
    ),
    "Other": (
        "◆ **OTHER SERVICES**\n"
        "• Level Farm → 1M per level\n"
        "• Soul Guitar → 165M\n"
        "• Cursed Dual Katana (Service) → 170.5M\n"
        "• Draco Trial → 104.5M\n"
        "• Blue Gear → 200M\n\n"
        "◆ **ADDITIONAL**\n"
        "• Priority Service → +20%\n"
        "• Custom services → On Request"
    ),
}


def make_pricelist_embed(category: str | None = None) -> discord.Embed:
    embed = discord.Embed(title=BASE_TITLE, color=discord.Color.blurple())
    if category is None:
        embed.add_field(name=BASE_SUBTITLE, value=BASE_DESCRIPTION, inline=False)
    else:
        embed.add_field(name=f"{BASE_SUBTITLE} — {category.upper()}", value=CATEGORY_DATA[category], inline=False)

    embed.set_footer(text=FOOTER_TEXT)
    return embed


class PriceListView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the command user can use these buttons.",
                ephemeral=True,
            )
            return False
        return True

    async def _update(self, interaction: discord.Interaction, category: str) -> None:
        embed = make_pricelist_embed(category)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Raids", emoji="⚔️", style=discord.ButtonStyle.primary, row=0)
    async def raids_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Raids")

    @discord.ui.button(label="Trials", emoji="🧬", style=discord.ButtonStyle.secondary, row=0)
    async def trials_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Trials")

    @discord.ui.button(label="Sea Events", emoji="🌊", style=discord.ButtonStyle.success, row=0)
    async def sea_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Sea Events")

    @discord.ui.button(label="Bosses", emoji="👑", style=discord.ButtonStyle.danger, row=0)
    async def bosses_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Bosses")

    @discord.ui.button(label="Swords", emoji="🗡️", style=discord.ButtonStyle.primary, row=1)
    async def swords_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Swords")

    @discord.ui.button(label="Beli", emoji="💰", style=discord.ButtonStyle.secondary, row=1)
    async def beli_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Beli")

    @discord.ui.button(label="Mastery", emoji="📘", style=discord.ButtonStyle.success, row=1)
    async def mastery_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Mastery")

    @discord.ui.button(label="Bounty", emoji="🎯", style=discord.ButtonStyle.danger, row=1)
    async def bounty_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Bounty")

    @discord.ui.button(label="Other", emoji="🧩", style=discord.ButtonStyle.primary, row=2)
    async def other_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._update(interaction, "Other")


class PriceListUI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pricelist", description="Show the interactive Blox Fruits service price list.")
    async def pricelist(self, interaction: discord.Interaction) -> None:
        view = PriceListView(author_id=interaction.user.id)
        await interaction.response.send_message(embed=make_pricelist_embed(), view=view)
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PriceListUI(bot))
