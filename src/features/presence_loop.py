from itertools import cycle

import discord
from discord.ext import commands, tasks

import config


class PresenceLoopFEAT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.presence_cycle = cycle(config.presences)
        self.update_presence.start()  # pylint: disable=no-member

    @tasks.loop(minutes=2)
    async def update_presence(self):
        status, activity_type, name = next(self.presence_cycle)

        activity = discord.Activity(
            name=name,
            type=activity_type,
            url='https://twitch.tv/aleatoriotv'
        )

        await self.bot.change_presence(status=status, activity=activity)

    @update_presence.before_loop
    async def wait_for_ready(self):
        await self.bot.wait_until_ready()

    @update_presence.after_loop
    async def reset_presence(self):
        if not self.bot.is_closed():
            await self.bot.change_presence()


def setup(bot):
    bot.add_cog(PresenceLoopFEAT(bot))
