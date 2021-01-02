from discord.ext import commands
from jishaku.cog import JishakuBase, jsk  # type: ignore # pylint: disable=unused-import
from jishaku.metacog import GroupCogMeta
from jishaku.modules import ExtensionConverter

import config


def is_owner(ctx):
    return ctx.author.id in config.owners


class Jishaku(JishakuBase, metaclass=GroupCogMeta, command_parent=jsk):
    async def cog_check(self, ctx):
        """Isso definirá quem consegue usar o jishaku."""
        if not is_owner(ctx):
            raise commands.NotOwner("Este comando é apenas para desenvolvedores.")
        return True


class OwnerCMDS(commands.Cog, name='Donos', command_attrs={'hidden': True}):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload')
    @commands.check(is_owner)
    async def _reload_command(self, ctx, *extensions: ExtensionConverter):
        """Alias para "jishaku reload"."""
        jsk_reload = self.bot.get_command('jishaku reload')
        await jsk_reload(ctx, *extensions)


def setup(bot):
    bot.add_cog(Jishaku(bot=bot))
    bot.add_cog(OwnerCMDS(bot))
