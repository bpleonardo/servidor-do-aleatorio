import discord
from discord.ext import commands

import config
from bot import Bot
from utils.context import CustomContext
from . import update_overwrites


class LockCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command('lock')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def _lock(self, ctx: CustomContext):
        everyone_role = ctx.guild.get_role(ctx.guild.id)
        await update_overwrites(ctx, everyone_role, send_messages=False)
        embed = discord.Embed(
            color=config.main_color,
            description=f'{config.emotes[9]} Canal bloqueado. Use /unlock para desbloquear.'
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LockCMD(bot))
