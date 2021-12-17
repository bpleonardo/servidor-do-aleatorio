from datetime import datetime

import discord
from discord.ext import commands

import config


class EmbedCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('embed')
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def _embed(self, ctx):  # noqa # pylint: disable=too-many-locals
        question_embed = discord.Embed(description='\u200b, color=config.main_color)

        msg = await ctx.send(embed=question_embed)

        async def get_resp(fields):
            def check(message):
                if not len(message.content.split(' // ')) >= fields:
                    return False
                if not message.author.id == ctx.author.id or \
                        not message.channel.id == ctx.channel.id:
                    return False
                return True

            try:
                message = await self.bot.wait_for('message', check=check, timeout=60)
            except TimeoutError:
                return [None] * fields
            final = []

            for field in message.content.split(' // '):
                field = field.strip().strip('\n')
                if field == '---':
                    final.append(None)
                else:
                    final.append(field)

            await message.delete()
            return final

        async def make_question(title, description, fields):
            description += '\n\n_Use `---` para deixar em branco._'
            question_embed.title = title
            question_embed.description = description
            await msg.edit(embed=question_embed)
            return await get_resp(fields)

        title, color, description, url = await make_question(
            'Básico',
            'Informe o título, cor, descrição e url do embed.\n\n'
            'Envie no chat usando este formato:\n\t[título] // [cor] // [descrição] // [url]',
            4
        )
        if color:
            try:
                color = int(color.replace('#', ''), 16)
            except TypeError:
                color = None

        author_name, author_icon, author_url = await make_question(
            'Autor',
            'Informe o nome, ícone e url do autor.\n\n'
            'Envie no chat usando este formato:\n\t[nome] // [ícone] // [url]',
            3
        )

        thumbnail, image_url = await make_question(
            'Imagens',
            'Informe o thumbnail e a imagem do embed.\n\n'
            'Envie no chat usando este formato:\n\t[thumbnail] // [imagem]',
            2
        )

        footer_text, timestamp, footer_icon = await make_question(
            'Footer',
            'Informe o texto, o timestamp e o ícone do footer.\n\n'
            'Envie no chat usando este formato:\n\t[texto] // '
            '[timestamp dd/mm/yyyy HH:MM] // [icon]',
            3
        )
        try:
            timestamp = datetime.strptime(timestamp, '%d/%m/%Y %H:%M').strftime('%Y/%m/%d %H:%M')
        except TypeError:
            timestamp = None

        fields = []
        indx = 0
        while True:
            indx += 1
            field_name, field_value, field_inline = await make_question(
                f'Field {indx}',
                f'Agora informe o nome, valor e se o field {indx} ficará inline.\n\n'
                'Envie no chat usando este formato:\n\t[nome] // [valor] // [inline?]',
                3
            )
            if field_inline:
                field_inline = field_inline[0] in 'SsNn'
            if not field_name or not field_value:
                break

            fields.append({
                'name': field_name,
                'value': field_value,
                'inline': field_inline
            })

        embed_dict = {
            'title': title,
            'type': 'rich',
            'description': description,
            'url': url,
            'timestamp': timestamp,
            'color': color,
            'footer': {
                'text': footer_text,
                'icon_url': footer_icon
            },
            'image': {
                'url': image_url
            },
            'thumbnail': {
                'url': thumbnail
            },
            'author': {
                'name': author_name,
                'url': author_url,
                'icon_url': author_icon
            },
            'fields': fields
        }
        embed_dict = {k: v for k, v in embed_dict.items() if v is not None}
        await msg.delete()
        await ctx.message.delete()

        if any(embed_dict.values()):
            final_embed = discord.Embed.from_dict(embed_dict)
            await ctx.send(embed=final_embed)


def setup(bot):
    bot.add_cog(EmbedCMD(bot))
