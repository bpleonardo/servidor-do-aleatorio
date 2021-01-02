# pylint: disable=too-few-public-methods

from discord.ext import commands

from . import parse_time


class RelativeTime(commands.Converter):
    """Retorna um timedelta representando o tempo especificado."""
    async def convert(self, _, argument):
        parsed = parse_time(argument)

        if parsed.total_seconds() == 0:
            raise commands.BadArgument('Insira uma data válida.')

        return parsed
