from __future__ import annotations

import logging
from typing import Dict

import discord
from discord.ext import commands

from utils.embed_factory import make_embed
from utils.storage import JsonStore

LOGGER = logging.getLogger(__name__)


class InviteTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.invite_cache: Dict[int, Dict[str, int]] = {}
        self.invite_data_store = JsonStore("data/invite_data.json", default={})
        self.invite_data: dict[str, str] = self.invite_data_store.load()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.refresh_all_invites()

    async def refresh_all_invites(self) -> None:
        for guild in self.bot.guilds:
            await self.refresh_guild_invites(guild)
        LOGGER.info("Invite cache initialized for %s guild(s).", len(self.bot.guilds))

    async def refresh_guild_invites(self, guild: discord.Guild) -> None:
        try:
            invites = await guild.invites()
            self.invite_cache[guild.id] = {invite.code: invite.uses or 0 for invite in invites}
        except discord.Forbidden:
            LOGGER.warning("Missing permission to read invites in guild %s (%s)", guild.name, guild.id)
        except discord.HTTPException as exc:
            LOGGER.warning("Failed to fetch invites for guild %s (%s)", guild.id, exc)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.refresh_guild_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        guild_cache = self.invite_cache.setdefault(invite.guild.id, {})
        guild_cache[invite.code] = invite.uses or 0

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        guild_cache = self.invite_cache.setdefault(invite.guild.id, {})
        guild_cache.pop(invite.code, None)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        guild = member.guild
        old_cache = self.invite_cache.get(guild.id, {}).copy()
        inviter_id: int | None = None
        current_invites: list[discord.Invite] = []

        try:
            current_invites = await guild.invites()
            current_map = {invite.code: invite.uses or 0 for invite in current_invites}
        except discord.Forbidden:
            LOGGER.warning("Cannot track invites in guild %s due to missing permissions.", guild.id)
            current_map = old_cache
        except discord.HTTPException as exc:
            LOGGER.warning("Invite fetch failed on join in guild %s (%s)", guild.id, exc)
            current_map = old_cache

        used_code = None
        for code, new_uses in current_map.items():
            old_uses = old_cache.get(code, 0)
            if new_uses > old_uses:
                used_code = code
                break

        if used_code and current_invites:
            invite_obj = discord.utils.get(current_invites, code=used_code)
            if invite_obj and invite_obj.inviter:
                inviter_id = invite_obj.inviter.id
        else:
            try:
                vanity = await guild.vanity_invite()
                if vanity and vanity.uses and vanity.code:
                    old_vanity_uses = old_cache.get(vanity.code, vanity.uses)
                    if vanity.uses > old_vanity_uses:
                        LOGGER.info(
                            "Member %s likely joined via vanity URL in guild %s.",
                            member.id,
                            guild.id,
                        )
            except (discord.Forbidden, discord.HTTPException):
                pass

        if inviter_id is not None:
            self.invite_data[str(member.id)] = str(inviter_id)
            self.invite_data_store.save(self.invite_data)
            LOGGER.info("Tracked inviter: member=%s inviter=%s", member.id, inviter_id)
        else:
            LOGGER.info("Could not determine inviter for member %s in guild %s", member.id, guild.id)

        self.invite_cache[guild.id] = current_map

    @commands.command(name="invitedby")
    async def invitedby(self, ctx: commands.Context, user: discord.Member) -> None:
        inviter_id = self.invite_data.get(str(user.id))
        if inviter_id is None:
            embed = make_embed("Invite Info", "No inviter data found")
            await ctx.send(embed=embed)
            return

        inviter = ctx.guild.get_member(int(inviter_id)) if ctx.guild else None
        inviter_display = inviter.mention if inviter else f"<@{inviter_id}>"
        embed = make_embed("Invite Info", f"{user.mention} was invited by {inviter_display}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InviteTracker(bot))
