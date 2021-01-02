from datetime import datetime
from typing import Union

import pytz
import discord
from discord.ext import commands

import config
from bot import Bot
from utils.context import CustomContext


class WarnsCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command('warns')
    async def _warns(self, ctx: CustomContext, member: Union[discord.Member, discord.User] = None):
        await ctx.trigger_typing()

        if not member:
            member = ctx.author

        member_warns = await self.bot.warns_col.find(member.id)

        embed = discord.Embed(color=config.main_color)
        embed.set_author(name=f'Warns de {member.display_name}', icon_url=member.avatar_url)

        if isinstance(member, discord.User):
            embed.set_footer(text='* membro não está no servidor.')

        if not member_warns:
            embed.description = 'Nenhum warn. Obrigado \N{HEAVY BLACK HEART}'
            return await ctx.send(embed=embed)

        count = member_warns.count
        embed.description = f'{count} warn{"s" if count != 1 else ""}.'
        fmt = '**- Horário do warn:** {}\n**- Motivo do warn**: {}'
        for key, warn in enumerate(member_warns.info):
            date: datetime = warn['date'].replace(tzinfo=pytz.UTC)
            date = date.astimezone(config.tz)

            formatted = date.strftime('%d/%m/%Y às %H:%M')
            embed.add_field(
                name=f'{key+1}º warn.',
                value=fmt.format(formatted, warn['reason']),
                inline=False
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(WarnsCMD(bot))
