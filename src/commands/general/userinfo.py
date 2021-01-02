from datetime import datetime

import discord
from discord.ext import commands

import config


class UserinfoCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_staff(self, member):
        return any(c for c in member.roles if c.id == config.staff_id)

    @commands.command('userinfo')
    async def _userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        fmt = (
            '\N{PERSONAL COMPUTER} **Id:** {0.id}\n'
            '\N{SPIRAL CALENDAR PAD} **Conta criada há:** {1}\n'
            '\N{DOOR} **Entrou no servidor há:** {2}\n'
            '<:staff:784316055996727327> **Faz parte da staff:** {3}\n'
        )

        relative_creation = self.bot.format_delta(datetime.utcnow() - member.created_at)
        relative_join = self.bot.format_delta(datetime.utcnow() - member.joined_at)
        member_is_staff = 'Sim' if self.is_staff(member) else 'Não'
        member_warns_count = 0

        embed = discord.Embed(color=config.main_color)
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)

        if self.is_staff(ctx.author):
            fmt += '\N{HEAVY EXCLAMATION MARK SYMBOL} **Warns:** {4}'
            member_warns = await self.bot.warns_col.find(member.id)
            if member_warns:
                member_warns_count = member_warns.count

        embed.description = fmt.format(
            member,
            relative_creation,
            relative_join,
            member_is_staff,
            member_warns_count
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UserinfoCMD(bot))
