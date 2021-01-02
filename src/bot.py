import sys
from datetime import datetime

import discord
from discord.ext import commands

import config
from utils import get_exception
from utils.context import CustomContext
from utils.database import Database


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ready_at: datetime = None  # Preenchido no on_ready

        self.db = Database('Server', kwargs.pop('mongo_uri'))
        self.warns_col = self.db.get_collection('Warns', {'count': 0, 'info': []})
        self.mutes_col = self.db.get_collection('Mutes', {'unmute_timestamp': 0, 'info': []})

    def load_all_extensions(self, extensions: list):
        """Carrega todas as extensões especificadas.

        Parameters
        ----------
        extensions: List[:class:`str`]
            As extensões para carregar.
            Serão passadas para o load_extension.
        """
        for extension in extensions:
            try:
                self.load_extension(extension)

            except commands.ExtensionFailed as e:
                orig = e.original
                print(f'{extension} -> [{orig.__class__.__name__}] {orig}')

            except commands.NoEntryPointError:
                print(f'{extension} -> Parece que a extensão não tem um setup.')

            else:
                print(f'{extension} -> Carregado.')

    async def process_commands(self, message):
        if message.author.bot and not message.author.id == self.user.id:
            return

        ctx = await self.get_context(message, cls=CustomContext)
        # if ctx.valid:
        #     await ctx.trigger_typing()
        await self.invoke(ctx)

    async def on_error(self, event_method, *args, **kwargs):
        _, error, _ = sys.exc_info()
        exc = get_exception(error)

        msg = (
            f'**Evento:** {event_method}\n'
            f'**Args:** {", ".join(map(repr, args))}\n'
            f'**kwargs:** {", ".join(["{}={}".format(k, repr(v)) for k, v in kwargs.items()])}'
        )

        embed = discord.Embed(title='Erro!', description=msg, color=config.main_color)
        embed.add_field(name=error.__class__.__name__, value=f'```py\n{exc}```')

        await self.get_channel(config.errors_channel).send(embed=embed)
