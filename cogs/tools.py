from __future__ import annotations

import discord
from discord.ext import commands

from utils.constants import COMMISSION_RATE, TAX_RATE
from utils.embed_factory import make_embed
from utils.storage import JsonStore


class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vouch_store = JsonStore("data/vouches.json", default={})
        self.vouches: dict[str, list[str]] = self.vouch_store.load()

    def _save_vouches(self) -> None:
        self.vouch_store.save(self.vouches)

    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name="commission")
    async def commission(self, ctx: commands.Context, user: discord.Member, price: float) -> None:
        commission_earned = price * COMMISSION_RATE
        embed = make_embed("Commission Earned")
        embed.add_field(name="Customer", value=user.mention, inline=False)
        embed.add_field(name="Service Price", value=f"${price:,.2f}", inline=True)
        embed.add_field(name="Commission Rate", value="7.5%", inline=True)
        embed.add_field(name="Commission Earned", value=f"${commission_earned:,.2f}", inline=False)
        await ctx.send(embed=embed)

    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name="tax_to_pay")
    async def tax_to_pay(self, ctx: commands.Context, user: discord.Member, price: float) -> None:
        tax_amount = price * TAX_RATE
        total_to_pay = price + tax_amount

        embed = make_embed("Tax To Pay")
        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Base Price", value=f"${price:,.2f}", inline=True)
        embed.add_field(name="Tax (10%)", value=f"${tax_amount:,.2f}", inline=True)
        embed.add_field(name="Total to Pay", value=f"${total_to_pay:,.2f}", inline=False)
        await ctx.send(embed=embed)

    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name="tax_paid")
    async def tax_paid(self, ctx: commands.Context, user: discord.Member, price: float) -> None:
        tax_amount = price * TAX_RATE
        final_amount = price - tax_amount

        embed = make_embed("Tax Paid")
        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Base Price", value=f"${price:,.2f}", inline=True)
        embed.add_field(name="Tax (10%)", value=f"${tax_amount:,.2f}", inline=True)
        embed.add_field(name="Final Amount Received", value=f"${final_amount:,.2f}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="calc")
    async def calc(self, ctx: commands.Context, amount: float) -> None:
        embed = make_embed("Calculation", f"Amount entered: **${amount:,.2f}**")
        await ctx.send(embed=embed)

    @commands.command(name="vouch")
    async def vouch(self, ctx: commands.Context, user: discord.Member, *, text: str) -> None:
        entries = self.vouches.setdefault(str(user.id), [])
        entries.append(f"{ctx.author.id}:{text}")
        self._save_vouches()

        embed = make_embed("Vouch Added", f"Vouch saved for {user.mention}.")
        await ctx.send(embed=embed)

    @commands.command(name="vouches")
    async def vouches_cmd(self, ctx: commands.Context, user: discord.Member) -> None:
        entries = self.vouches.get(str(user.id), [])
        if not entries:
            embed = make_embed("Vouches", f"No vouches found for {user.mention}.")
            await ctx.send(embed=embed)
            return

        formatted = []
        for idx, entry in enumerate(entries[:15], start=1):
            author_id, _, text = entry.partition(":")
            formatted.append(f"{idx}. <@{author_id}>: {text}")

        embed = make_embed("Vouches", "\n".join(formatted))
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context) -> None:
        embed = make_embed("Help", "Available commands")
        embed.add_field(name=">commission @user <price>", value="Calculate 7.5% commission.", inline=False)
        embed.add_field(name=">tax_to_pay @user <price>", value="Add 10% tax to the base price.", inline=False)
        embed.add_field(name=">tax_paid @user <price>", value="Deduct 10% tax from base price.", inline=False)
        embed.add_field(name=">invitedby @user", value="Show inviter for a user.", inline=False)
        embed.add_field(name=">pricelist / >price <service>", value="View service pricing.", inline=False)
        embed.add_field(name=">setprice / >updateprice / >removeprice", value="Admin price management.", inline=False)
        embed.add_field(name=">services", value="List available services.", inline=False)
        embed.add_field(name=">vouch @user <text>", value="Leave a vouch.", inline=False)
        embed.add_field(name=">vouches @user", value="See user vouches.", inline=False)
        embed.add_field(name=">calc <amount>", value="Simple amount display.", inline=False)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tools(bot))
