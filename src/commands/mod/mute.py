import asyncio
from datetime import datetime

import discord
from discord.ext import commands

import config
from bot import Bot
from utils import get_data, parse_time, format_delta
from utils.context import CustomContext
from . import ReasonAsker, can_do_action


def message_check(ctx: CustomContext):
    def inner(message: discord.Message):
        from_the_right_place = all((
            message.author == ctx.author,
            message.channel == ctx.channel,
        ))
        has_the_correct_content = any((
            message.content.lower() in ('p', 'cancelar'),
            parse_time(message.content).total_seconds()
        ))

        return from_the_right_place and has_the_correct_content

    return inner


class MuteCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.asker = ReasonAsker(get_data('reasons.json')['mute'])

    @commands.command('mute')
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx: CustomContext, member: discord.Member):
        mute_role = ctx.guild.get_role(config.mute_role)

        if mute_role in member.roles:
            return await ctx.send('Este membro já está mutado.')

        missing_perms = can_do_action(ctx, member)
        if missing_perms:
            return await ctx.send(missing_perms)

        if mute_role.position >= ctx.me.top_role.position:
            return await ctx.send(f'O cargo {mute_role} está acima do meu cargo.')

        msg, reason = await self.asker.run(ctx, f'Silenciar {member.display_name} com o motivo:')

        if not msg:
            return

        tempmute_cog = self.bot.get_cog('TempMuteFEAT')

        embed = discord.Embed(title='Qual o tempo do mute?', color=config.main_color)
        embed.set_footer(text='Digite cancelar para sair.')
        embed.add_field(
            name='Exemplos:',
            value=f'{config.emotes[9]} 1s _(1 segundo)_\n'
                  f'{config.emotes[9]} 1m _(1 minuto)_\n'
                  f'{config.emotes[9]} 1h _(1 hora)_\n'
                  f'{config.emotes[9]} 1d _(1 dia)_\n'
                  f'{config.emotes[9]} P _(Permanente)_'
        )
        await msg.edit(embed=embed)

        try:
            answer = await self.bot.wait_for('message', check=message_check(ctx))
        except asyncio.TimeoutError:
            return await msg.delete()
        if answer.content.lower() == 'cancelar':
            return await msg.delete()
        if answer.content.lower() != 'p':
            date = datetime.utcnow() + parse_time(answer.content)

            info = {'staff': ctx.author.id, 'reason': reason}
            await tempmute_cog.mute(date, member.id, info=info)

        await member.add_roles(mute_role, reason=f'Por {ctx.author} | {reason}')

        embed = discord.Embed(
            description=f'{config.emotes[9]} {member.display_name} mutado(a) por {reason}.',
            color=config.main_color
        )
        await msg.edit(embed=embed)

        duration = 'Permanente.'
        if answer.content.lower() != 'p':
            duration = format_delta(parse_time(answer.content))

        self.bot.dispatch('mod_action', 'mute', ctx.author, member, reason, duration=duration)


def setup(bot):
    bot.add_cog(MuteCMD(bot))
