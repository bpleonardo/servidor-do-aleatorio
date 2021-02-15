import discord
from discord.ext import commands

from bot import Bot
from utils.context import CustomContext


class UnwarnCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command(name='unwarn')
    @commands.has_permissions(manage_messages=True)
    async def _unwarn(self, ctx: CustomContext, member: discord.User, index: int = None):
        member_warns = await self.bot.warns_col.find(member.id)

        if not member_warns:
            return await ctx.send('Este membro não possui nenhum warn.')

        if member_warns.count == 1:
            reason = member_warns.info[0]['reason']
            await member_warns.delete()
        else:
            if index is None:
                return await ctx.send('Este membro possui mais de um warn. Por favor especifique '
                                      'qual quer remover.')

            try:
                reason = member_warns.info[max(0, index - 1)]['reason']
                del member_warns.data['info'][max(0, index - 1)]
            except IndexError:
                return await ctx.send('Warn não encontrado. Certifique-se que digitou o número '
                                      'correto.')

            await member_warns.sync()

        await ctx.send(f'Removido warn {index if index else 1} com o motivo "{reason}"')

        self.bot.dispatch(
            'mod_action',
            'unwarn',
            ctx.author,
            member,
            reason,
            index=index if index else 1
        )


def setup(bot):
    bot.add_cog(UnwarnCMD(bot))
