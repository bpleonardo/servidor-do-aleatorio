from discord.ext import commands
from discord.utils import find

import config


class VipRoleFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_premium(self, member):
        return bool(find(lambda r: r.id in config.premium_roles.values(), member.roles))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return

        before_is_premium = self.is_premium(before)
        after_is_premium = self.is_premium(after)
        if before_is_premium and after_is_premium:
            # Ainda é vip.
            return

        vip_role = before.guild.get_role(config.vip_role)

        if before_is_premium and not after_is_premium:
            # Não é mais vip.
            return await after.remove_roles(vip_role, reason='Não é mais vip.')
        if not before_is_premium and after_is_premium:
            # Virou vip.
            return await after.add_roles(vip_role, reason='Se tornou vip.')


def setup(bot):
    bot.add_cog(VipRoleFEAT(bot))
