import discord
from discord.ext import commands
from pytz import utc

import config
from utils import get_data
from . import ReasonAsker, can_do_action


class WarnCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.asker = ReasonAsker(get_data('reasons.json')['warn'])

    @commands.command(name='warn')
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def _warn(self, ctx, member: discord.Member):
        missing_perms = can_do_action(ctx, member)
        if missing_perms:
            return await ctx.send(missing_perms)

        msg, reason = await self.asker.run(ctx, f'Avisar {member.display_name} com o motivo:')

        if not msg:
            return

        user_warns = await self.bot.warns_col.update(member.id, {
            '$inc': {'count': 1},
            '$push': {'info': {
                'staff': ctx.author.id,
                'reason': reason,
                'date': ctx.message.created_at.replace(tzinfo=utc),
                # TODO: Remover o timestamp
                'timestamp': ctx.message.created_at.replace(tzinfo=utc).timestamp()
            }}
        })

        txt = f'{config.emotes[9]} {member.display_name} avisado pela {user_warns.count}º vez.'
        embed = discord.Embed(description=txt, color=config.main_color)

        await msg.edit(embed=embed)

        self.bot.dispatch(
            'mod_action',
            'unwarn',
            ctx.author,
            member,
            reason,
            streak=user_warns.count
        )


def setup(bot):
    bot.add_cog(WarnCMD(bot))
