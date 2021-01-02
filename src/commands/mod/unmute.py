import discord
from discord.ext import commands

import config
from bot import Bot
from utils.context import CustomContext
from . import can_do_action


class UnmuteCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command('unmute')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def _unmute(self, ctx: CustomContext, member: discord.Member):
        mute_role = ctx.guild.get_role(config.mute_role)
        if mute_role not in member.roles:
            return await ctx.send('Este membro não está mutado.')

        missing_perms = can_do_action(ctx, member)
        if missing_perms:
            return await ctx.send(missing_perms)

        await member.remove_roles(mute_role, reason=f'Por {ctx.author}')

        tempmute_cog = self.bot.get_cog('TempMuteFEAT')

        await tempmute_cog.remove_member_from_unmute_queue(member.id)
        await self.bot.mutes_col.delete(member.id)
        await tempmute_cog.restart()

        await ctx.send(f'{member.display_name} desmutado.')

        self.bot.dispatch('mod_action', 'unmute', ctx.author, member)


def setup(bot):
    bot.add_cog(UnmuteCMD(bot))
