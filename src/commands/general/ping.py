from discord.ext import commands


class PingCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('ping')
    async def _ping(self, ctx):
        api_ping = round(self.bot.latency * 1000, 2)

        msg = await ctx.send('\N{ZERO WIDTH SPACE}')

        _diff = msg.created_at.timestamp() - ctx.message.created_at.timestamp()
        response_time = round(_diff * 1000, 2)

        await msg.edit(content=f'Ping com a API: **{api_ping}**ms. '
                               f'Tempo de resposta: **{response_time}**ms')


def setup(bot):
    bot.add_cog(PingCMD(bot))
