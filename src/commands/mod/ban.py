from typing import Union
import discord
from discord.ext import commands

import config
from utils import get_data
from . import ReasonAsker, can_do_action


class BanCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.asker = ReasonAsker(get_data('reasons.json')['ban'])

    @commands.command('ban')
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _ban(self, ctx, member: Union[discord.Member, discord.User]):
        missing_perms = can_do_action(ctx, member)
        if missing_perms:
            return await ctx.send(missing_perms)

        msg, reason = await self.asker.run(ctx, f'Banir {member.display_name} com o motivo:')

        if not msg:
            return

        await ctx.guild.ban(member, reason=f'Por {ctx.author} | {reason}')

        txt = f'{config.emotes[9]} {member} banido(a) por {reason}.'
        embed = discord.Embed(description=txt, color=config.main_color)
        await msg.edit(embed=embed)

        self.bot.dispatch('mod_action', 'ban', ctx.author, member, reason)


def setup(bot):
    bot.add_cog(BanCMD(bot))
