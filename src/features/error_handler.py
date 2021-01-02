import traceback
import re

import discord
from discord.ext import commands

import config
from utils import get_data


def get_exception(e: Exception, size: int = 3):
    tb = traceback.extract_tb(e.__traceback__)[-size:]
    exc = ''.join(traceback.format_list(tb))

    # Por algum motivo ele não retorna o erro em si,
    # então tenho que inserir manualmente.
    exc += f'{e.__class__.__name__}: {e}'
    return exc


ignored_errors = (
    commands.CommandNotFound,
)


class ErrorHandlerFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: commands.CommandError):  # noqa
        original = error.__cause__

        if isinstance(error, ignored_errors):
            return
        if isinstance(original, ignored_errors):
            return

        if isinstance(error, commands.BadArgument):
            msg = str(error)

            match = re.findall(r'"([\w\d]+)"', str(error))
            if len(match) == 2:
                msg = f'Não foi possivel converter "{match[0]}" para "{match[1]}".'
            elif msg.endswith('not found.'):
                msg = f'**{match[0]}** não encontrado.'

            return await ctx.send(msg)

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
            perm = get_data('permissions.json')[error.missing_perms[0]]

            msg = f'Você precisa da permissão **{perm.title()}** para executar esse comando.'
            return await ctx.send(msg)

        if isinstance(error, commands.BotMissingPermissions):
            perm = get_data('permissions.json')[error.missing_perms[0]]

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
        embed.add_field(name=(original or error).__class__.__name__, value=exc)

        await self.bot.get_channel(config.errors_channel).send(embed=embed)
        await ctx.send('Um erro aconteceu. Ele já foi reportado :)')


def setup(bot):
    bot.add_cog(ErrorHandlerFEAT(bot))
