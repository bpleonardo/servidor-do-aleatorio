from datetime import datetime

from discord.ext import commands

from bot import Bot


class OnReadyFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.ready_at = datetime.utcnow()

        ready_fmt = self.bot.ready_at.strftime('%d/%m/%Y %H:%M:%S')

        # Estou usando essa lista para armazenar o maior valor
        # para poder criar um "-" de tamanho variável.
        texts = [
            'Logado como:',
            f'  Tag: {self.bot.user}',
            f'  ID: {self.bot.user.id}',
            '',
            'Iniciado em:',
            f'  UTC: {ready_fmt}',
        ]

        size = len(max(texts, key=len))

        print('{:-^{}}'.format(' Online ', size))
        for txt in texts:
            print(txt)
        print('-' * size)


def setup(bot):
    bot.add_cog(OnReadyFEAT(bot))
