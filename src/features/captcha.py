from secrets import choice
from asyncio import sleep, TimeoutError

from discord import PermissionOverwrite, Embed, HTTPException
from discord.utils import get
from discord.ext import commands

import config
from utils import get_data


class CaptchaFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.captchas = tuple(get_data('captchas.txt').splitlines())

    def random_case(self, s):
        return ''.join(choice((str.upper, str.lower))(c) for c in s)

    def check(self, member, channel):
        def pred(message):
            return all((
                message.author == member,
                message.channel == channel,
                message.content
            ))
        return pred

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        members_role = guild.get_role(config.members_role)

        if members_role in member.roles:
            return

        category = guild.get_channel(config.verification_category)
        name = f'captcha-{hash(member)}'

        if get(category.channels, name=name):
            txt = f'{member.mention}, por favor, não tente burlar o sistema de espera.'
            return await get(category.channels, name=name).send(txt)

        overwrites = {
            guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
            member: PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await member.guild.create_text_channel(
            name,
            overwrites=overwrites,
            category=category,
            reason=f'Verificando {member}.'
        )

        msg = await channel.send(member.mention)
        embed = Embed(title='Verificação', color=config.main_color)
        txt = (
            'Para a segurança do servidor, precisamos que você confirme que não é um robô.\n'
            'Escreva a palavra "{}" como forma de verificação.\n\n'
            '**Não** use nenhum tipo de formatação, mesmo a mensagem incluindo.\n'
            'Alguns exemplos do que não utilizar: **1**, ~~2~~, __3__, ||4||
        )

        possible_formats = ('~~', '_', '**', '__', '||')
        tries = 0
        while True:
            if tries == 10 and member not in config.owners:
                await msg.edit(content='10 tentativas incorretas. Cancelando.')
                await sleep(5)
                await channel.delete()
                try:
                    await member.kick(reason='10 tentativas.')
                except HTTPException:
                    pass
                return

            tries += 1
            if max(1, tries) % 4 == 0:
                await msg.edit(content='3 tentativas incorretas. Aguarde 1 minuto...', embed=None)
                await sleep(60)
                continue

            word = self.random_case(choice(self.captchas))
            f1 = choice(possible_formats)
            f2 = choice(possible_formats)
            zws = '\N{ZERO WIDTH SPACE}'
            embed.description = txt.format(f'{f1}{zws}{f2}{word}{f2}{zws}{f1}')
            await msg.edit(content=None, embed=embed)

            try:
                res = await self.bot.wait_for(
                    'message',
                    check=self.check(member, channel),
                    timeout=60
                )
            except TimeoutError:
                await channel.send('Você demorou demais, tente novamente.', delete_after=5)
                continue
            if res.content == word:
                break
            await channel.send('Palavra incorreta, tente novamente.', delete_after=5)
            continue

        await channel.delete()
        await member.add_roles(members_role, reason=f'{member} verificado.')


def setup(bot):
    bot.add_cog(CaptchaFEAT(bot))
