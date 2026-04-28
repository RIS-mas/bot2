from __future__ import annotations

import discord
from discord.ext import commands

from utils.embed_factory import make_embed
from utils.storage import JsonStore

DEFAULT_PRICE_CATALOG: dict[str, dict[str, float | str]] = {
    "RAIDS (EASY)": {
        "1-5": "12M",
        "5-10": "25M",
        "10-15": "49.5M",
    },
    "RAIDS (ADVANCED)": {
        "1-5": "25M",
        "5-7": "35M",
        "7-12": "60.5M",
    },
    "LAW RAIDS": {
        "Per Raid": "5M",
    },
    "TRIALS / RACE": {
        "1 Trial": "35M",
        "2 Trials": "65M",
        "3 Trials": "101M",
        "4 Trials": "132M",
        "Max Race": "198M",
    },
    "SEA EVENTS": {
        "Mirage": "71.5M",
        "Sea Beast": "3M",
        "Prehistoric": "77M",
        "Leviathan": "198M",
        "Ship Raids": "4M",
        "Kitsune": "88M",
    },
    "BOSSES": {
        "Darkbeard": "50M",
        "Cake Prince": "40M",
        "Rip Indra": "60.5M",
        "Dough King": "77M",
        "Tyrant": "30M",
    },
    "SWORDS": {
        "True Triple Katana": "100M (per sword)",
        "Tushita": "90M",
        "Yama": "90M",
        "Cursed Dual Katana": "170M",
    },
    "BELI (MONEY)": {
        "1M": "18M",
        "2M": "28M",
        "3.5M": "38M",
        "10M": "88M",
        "30M": "363M",
        "60M": "495M",
    },
    "MASTERY": {
        "To 300": "104.5M",
        "To 600": "203.5M",
    },
    "BOUNTY": {
        "Raging Demon": "121M",
        "500K": "143M",
        "1M": "286M",
        "2M": "572M",
    },
    "OTHER SERVICES": {
        "Level Farm": "1M per level",
        "Soul Guitar": "165M",
        "Cursed Dual Katana (Service)": "170.5M",
        "Draco Trial": "104.5M",
        "Blue Gear": "200M",
    },
    "ADDITIONAL": {
        "Priority Service": "+20%",
        "Custom services": "On Request",
    },
}


def _normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


class Pricing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.store = JsonStore("data/prices.json", default={})
        self.custom_prices: dict[str, str] = self.store.load()

    def _save(self) -> None:
        self.store.save(self.custom_prices)

    def _catalog_map(self) -> dict[str, str]:
        merged: dict[str, str] = {}
        for services in DEFAULT_PRICE_CATALOG.values():
            for service, price in services.items():
                merged[_normalize(service)] = str(price)

        for service, price in self.custom_prices.items():
            merged[_normalize(service)] = str(price)
        return merged

    @staticmethod
    def _split_service_price(raw: str) -> tuple[str, str] | tuple[None, None]:
        parts = raw.rsplit(" ", 1)
        if len(parts) != 2:
            return None, None
        service_name, price = parts[0].strip(), parts[1].strip()
        if not service_name or not price:
            return None, None
        return service_name, price

    @commands.command(name="pricelist")
    async def pricelist(self, ctx: commands.Context) -> None:
        embed = make_embed("⟢ ENLIGHTEN COMMUNITY ⟣", "BLOX FRUITS SERVICE PRICE LIST")

        for category, services in DEFAULT_PRICE_CATALOG.items():
            lines = [f"• {service} → {price}" for service, price in services.items()]
            embed.add_field(name=f"◆ {category}", value="\n".join(lines), inline=False)

        if self.custom_prices:
            custom_lines = [f"• {service} → {price}" for service, price in sorted(self.custom_prices.items())]
            embed.add_field(name="◆ CUSTOM / OVERRIDES", value="\n".join(custom_lines), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="price")
    async def price(self, ctx: commands.Context, *, service_name: str) -> None:
        lookup = self._catalog_map()
        normalized = _normalize(service_name)
        price = lookup.get(normalized)

        if price is None:
            embed = make_embed("Price Lookup Error", f"Service `{service_name}` not found.")
            await ctx.send(embed=embed)
            return

        embed = make_embed("Service Price", f"**{service_name}** costs **{price}**")
        await ctx.send(embed=embed)

    @commands.command(name="services")
    async def services(self, ctx: commands.Context) -> None:
        all_services = sorted(self._catalog_map().keys())
        readable = "\n".join(f"• {name.title()}" for name in all_services)
        embed = make_embed("Services", readable)
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command(name="setprice")
    async def setprice(self, ctx: commands.Context, *, service_and_price: str) -> None:
        service_key, price = self._split_service_price(service_and_price)
        if not service_key or not price:
            embed = make_embed("Invalid Input", "Usage: `>setprice <service name> <price>`")
            await ctx.send(embed=embed)
            return

        previous = self.custom_prices.get(service_key)
        self.custom_prices[service_key] = price
        self._save()

        if previous is None:
            description = f"Added custom service **{service_key}** at **{price}**"
        else:
            description = f"Updated custom service **{service_key}** from **{previous}** to **{price}**"

        embed = make_embed("Price Updated", description)
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command(name="updateprice")
    async def updateprice(self, ctx: commands.Context, *, service_and_price: str) -> None:
        service_key, new_price = self._split_service_price(service_and_price)
        if not service_key or not new_price:
            embed = make_embed("Invalid Input", "Usage: `>updateprice <service name> <new_price>`")
            await ctx.send(embed=embed)
            return

        if service_key not in self.custom_prices:
            embed = make_embed("Update Failed", f"Custom service `{service_key}` does not exist.")
            await ctx.send(embed=embed)
            return

        old_price = self.custom_prices[service_key]
        self.custom_prices[service_key] = new_price
        self._save()
        embed = make_embed("Price Updated", f"**{service_key}**: **{old_price}** → **{new_price}**")
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command(name="removeprice")
    async def removeprice(self, ctx: commands.Context, service: str) -> None:
        service_key = service.strip()
        removed = self.custom_prices.pop(service_key, None)
        if removed is None:
            embed = make_embed("Remove Failed", f"Custom service `{service_key}` not found.")
            await ctx.send(embed=embed)
            return

        self._save()
        embed = make_embed("Service Removed", f"Removed custom service **{service_key}** from overrides.")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pricing(bot))
