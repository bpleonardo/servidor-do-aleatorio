import asyncio

from discord.ext import commands


class CustomContext(commands.Context):
    async def prompt(self, *args, **kwargs) -> bool:
        """Envia a mensagem e adiciona reações de confirmação.

        Parameters
        ----------
        *args
            Passado para o send.
        **kwargs
            Passado para o send.

        Returns
        -------
        bool
            Se o usuário selecionou sim ou não.

        Notes
        -----
        Retornara True caso o bot não tenha permissão para adicionar
        reações.
        """
        if not self.me.permissions_in(self.channel).add_reactions:
            return True

        delete_after = kwargs.pop('delete_after', True)

        msg = await self.send(*args, **kwargs)

        emojis = ['✅', '❎']

        for e in emojis:
            await msg.add_reaction(e)

        def check(reaction):
            conditions = [
                str(reaction.emoji) in emojis,
                reaction.user_id == self.author.id,
                reaction.channel_id == self.channel.id,
            ]
            if not all(conditions):
                return False
            return True

        try:
            # Eu quero usar o raw_reaction_add por não precisar do
            # objeto da mensagem, apenas o emoji reagido.
            payload = await self.bot.wait_for(
                'raw_reaction_add',
                check=check,
                timeout=30
            )
        except asyncio.TimeoutError:
            return False
        finally:
            if delete_after:
                await msg.delete()

        if str(payload.emoji) == '✅':
            return True
        if str(payload.emoji) == '❎':
            return False

        # Aqui é teoricamente impossível de chegar, por isso o
        # RuntimeError
        raise RuntimeError('O emoji é desconhecido, e passou pelo check.')
