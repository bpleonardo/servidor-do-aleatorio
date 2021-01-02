import discord
from discord.ext import commands

import config
from . import update_overwrites


class UnlockCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('unlock')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def _unlock(self, ctx):
        everyone_role = ctx.guild.get_role(ctx.guild.id)
        await update_overwrites(ctx, everyone_role, send_messages=None)
        embed = discord.Embed(
            color=config.main_color,
            description=f'{config.emotes[9]} Canal desbloqueado. Use /lock para bloquear.'
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UnlockCMD(bot))
