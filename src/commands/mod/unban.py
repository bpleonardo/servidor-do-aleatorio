import discord
from discord.ext import commands

import config
from bot import Bot
from utils.context import CustomContext


class UnbanCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command('unban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _unban(self, ctx: CustomContext, member: discord.User):
        embed = discord.Embed(
            description=f'Deseja realmente desbanir {member}?',
            color=config.main_color
        )
        confirm = await ctx.prompt(embed=embed)

        if not confirm:
            return await ctx.send('Ok. Cancelando.')

        try:
            await ctx.guild.unban(member.id, reason=f'Por {ctx.author}')
        except discord.NotFound:
            return await ctx.send(f'{member.name} não está banido.')

        await ctx.send(f'{member.name} desbanido.')

        self.bot.dispatch('mod_action', 'unban', ctx.author, member)


def setup(bot):
    bot.add_cog(UnbanCMD(bot))
