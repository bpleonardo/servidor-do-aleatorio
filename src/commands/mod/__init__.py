from asyncio import TimeoutError
from typing import List

import discord

import config
from utils import safe_cancel


def can_do_action(ctx, member):
    """
    Checa se um membro pode executar uma ação sobre outro.
    Caso não possa, retornará um texto explicativo.

    Parameters
    ----------
    ctx: :class:`discord.ext.commands.Context`
    member: :class:`discord.Member`

    Returns
    -------
    typing.Optional[:class:`str`]
        O motivo do membro não poder executar.
        Pronto para ser enviado.
    """
    result = None

    if not getattr(member, 'guild', None):
        return None

    if member.top_role.position >= ctx.author.top_role.position:
        result = f'**{member.display_name}** tem um cargo mais alto do que você.'

    if ctx.author == ctx.guild.owner:
        result = None

    if member.top_role.position >= ctx.me.top_role.position:
        result = f'**{member.display_name}** tem um cargo mais alto do que eu.'

    if member == ctx.guild.owner:
        result = f'**{member.display_name}** é o dono do servidor.'

    if ctx.author == member:
        result = 'Esse é você.'

    if member == ctx.me:
        result = 'Esse sou eu.'

    return result


class ReasonAsker():
    """Classe criada para diminuir a complexidade."""
    SEP = f'\n{"─" * 18}\n'
    PONTO = config.emotes[9]

    def __init__(self, reasons: List[str]):
        self.reasons = reasons
        self.reasons.append('Outro')

        self.buttons = dict(zip(config.emotes, self.reasons))

        self.embed = discord.Embed(color=config.main_color)

        formatted_desc = '\n'.join(
            f'{button} {self.PONTO} **{reason.title()}**'
            for button, reason in self.buttons.items()
        )
        description = formatted_desc.replace('\n', self.SEP).strip('\n')

        self.embed.description = f'{self.SEP} {description} {self.SEP}'

    def reaction_check(self, ctx):
        def inner(reaction, user):
            return all((
                user == ctx.author,
                reaction.message.channel == ctx.channel,
                str(reaction.emoji) in self.buttons
            ))
        return inner

    def message_check(self, ctx):
        def inner(message):
            return all((
                message.channel == ctx.channel,
                message.author == ctx.author,
                message.content
            ))
        return inner

    async def add_buttons(self, message):
        for button in self.buttons:
            await message.add_reaction(button)

    async def run(self, ctx, embed_title):
        embed = self.embed.copy()
        embed.title = embed_title

        msg = await ctx.send(embed=embed)

        task = ctx.bot.loop.create_task(self.add_buttons(msg))

        try:
            reaction, _ = await ctx.bot.wait_for(
                'reaction_add',
                check=self.reaction_check(ctx),
                timeout=30
            )
        except TimeoutError:
            await msg.delete()
            return None, None
        finally:
            await safe_cancel(task)

        await msg.clear_reactions()

        if str(reaction.emoji) == list(self.buttons.keys())[-1]:
            # Outro
            embed.description = f'{self.PONTO} Digite o motivo.'
            await msg.edit(embed=embed)

            try:
                message = await ctx.bot.wait_for(
                    'message',
                    check=self.message_check(ctx),
                    timeout=30
                )
            except TimeoutError:
                await msg.delete()
                return None, None

            return msg, message.content.title()

        return msg, self.buttons[str(reaction.emoji)].title()


async def update_overwrites(ctx, target, **new_overwrites):
    channel = ctx.channel

    overwrites = dict(channel.overwrites_for(target))

    overwrites.update(new_overwrites)
    new_over = discord.PermissionOverwrite(**overwrites)

    return await channel.set_permissions(
        target,
        overwrite=new_over,
        reason=f'Por {ctx.author}'
    )
