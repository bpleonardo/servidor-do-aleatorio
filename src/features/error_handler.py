import re
from typing import Tuple

import discord
from discord.ext import commands

import config
from bot import Bot
from utils import get_data, get_exception
from utils.context import CustomContext


ignored_errors: Tuple[discord.DiscordException] = (
    commands.CommandNotFound,
)


class ErrorHandlerFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CustomContext, error: commands.CommandError):  # noqa
        original = error.__cause__

        if isinstance(error, ignored_errors):
            return
        if isinstance(original, ignored_errors):
            return

        if isinstance(error, commands.BadArgument):
            if str(error).endswith('not found.'):
                name = re.search(r'(?:.+) "(.+)" (?:(not found.))', str(error)).group(1)
                return await ctx.send(f'**{name}** não encontrado.')

            if str(error).startswith('Could not convert'):
                name, value = re.findall(
                    r'(?:(Could not convert)) "(.+)" into "(.+)"',
                    str(error)
                )[0][1:3]

                return await ctx.send(f'Não foi possível converter **{name}** em **{value}**')

            return await ctx.send(str(error))

        if isinstance(error, commands.BadUnionArgument):
            # Código do BadUnionArgument
            def _get_name(x):
                try:
                    return x.__name__
                except AttributeError:
                    return x.__class__.__name__

            to_string = [_get_name(x) for x in error.converters]
            if len(to_string) > 2:
                fmt = '{}, ou {}'.format(', '.join(to_string[:-1]), to_string[-1])
            else:
                fmt = ' ou '.join(to_string)

            return await ctx.send(f'Não foi possivel converter "{error.param.name}" para {fmt}.')

        if isinstance(error, commands.MissingPermissions):
            perm = get_data('permissions.json')[str(error.missing_perms[0])]

            msg = f'Você precisa da permissão **{perm.title()}** para executar esse comando.'
            return await ctx.send(msg)

        if isinstance(error, commands.BotMissingPermissions):
            perm = get_data('permissions.json')[str(error.missing_perms[0])]

            msg = f'Eu preciso da permissão **{perm.title()}** para executar esse comando.'
            return await ctx.send(msg)

        if isinstance(error, commands.CheckFailure):
            # Não podemos colocar na li
            return await ctx.send(error)

        if isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.send(f'Você já está executando o comando {ctx.command.name}.')

        exc = get_exception(original or error)
        msg = (
            f'Invocação: {ctx.message.content}\n'
            f'Canal: {ctx.channel.mention}\n'
            f'Membro: {ctx.author.mention}'
        )

        embed = discord.Embed(title='Erro!', description=msg, color=ctx.author.id >> 22 & 0xFFFFFF)
        embed.add_field(name=(original or error).__class__.__name__, value=f'```py\n{exc}```')

        await self.bot.get_channel(config.errors_channel).send(embed=embed)
        await ctx.send('Um erro aconteceu. Ele já foi reportado :)')


def setup(bot):
    bot.add_cog(ErrorHandlerFEAT(bot))
