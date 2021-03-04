from datetime import datetime

import discord
from discord.ext import commands

import config
from bot import Bot
from utils import get_data


class ModlogFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    async def _notify_staff(self, name, author, member, reason, **extra):
        embed = discord.Embed(title=f'Recebido {name.lower()}', color=config.main_color)
        embed.description = f'Staff responsável: {author.mention} ({author.id})\n'
        embed.description += f'Membro: {member.mention} ({member.id})\n'
        embed.description += f'Motivo: {reason}\n\n'
        for k, v in extra.items():
            embed.description += f'{k.capitalize()}: {v}\n'

        await self.bot.get_channel(config.modlog_staff_channel).send(embed=embed)

    @commands.Cog.listener()
    async def on_mod_action(self, name, author, member, reason=None, *, timestamp=None, **extra):
        text = '\n'.join(get_data('modlog_texts.json')[name.lower()])
        desc = text.format(P=config.emotes[9], author=author, member=member, reason=reason, **extra)

        embed = discord.Embed(
            title=name.title(),
            description=desc,
            timestamp=timestamp or datetime.utcnow(),
            color=config.main_color
        )
        embed.set_author(name=str(member), icon_url=member.avatar_url)

        await self.bot.get_channel(config.modlog_channel).send(embed=embed)
        await self._notify_staff(name, author, member, reason, **extra)


def setup(bot):
    bot.add_cog(ModlogFEAT(bot))
