import asyncio
from datetime import datetime

import discord
from discord.ext import commands

import config
from utils import FakeMember, safe_cancel


class TempMuteFEAT(commands.Cog):
    """
    Feature responsavel por cuidar de toda a parte de tempmute.
    Desde desmutar no horário certo até manipulação da database.
    """
    def __init__(self, bot):
        self.bot = bot
        self.current_mutes = dict()
        self._started = asyncio.Event()
        # Eu prefiro usar task pois assim eu posso cancelar e iniciar
        # sem ativar hooks.
        self.task = self.bot.loop.create_task(self.watch_for_mutes())

    def cog_unload(self):
        self._started.clear()
        self.task.cancel()
        self.task = None

    async def restart(self):
        if self.task and not self.task.done():
            await safe_cancel(self.task)
        self.task = self.bot.loop.create_task(self.watch_for_mutes())

    async def collect_mutes(self):
        await self.bot.wait_until_ready()

        helper_dict = {}
        async for doc in self.bot.mutes_col.all():
            date = doc.unmute_date
            member_id = doc._id  # pylint: disable=protected-access

            if date <= datetime.utcnow():
                await self._unmute(member_id)
            else:
                helper_dict[date] = helper_dict.get(date, []) + [member_id]

        self.current_mutes = helper_dict

    async def watch_for_mutes(self):
        if not self._started.is_set():
            await self.collect_mutes()
            self._started.set()

        for date, members in sorted(self.current_mutes.items()):
            await discord.utils.sleep_until(date)
            del self.current_mutes[date]
            await self._unmute(*members)

        self.current_mutes = {}
        await asyncio.sleep(0)  # Necessário para outras tasks rodarem.

    async def mute(self, date, *members, **data):
        await self._started.wait()

        current = self.current_mutes
        current[date] = current.get(date, [])
        for member_id in members:
            current[date].append(member_id)

        await self.restart()

        for member_id in members:
            member_doc = await self.bot.mutes_col.new(member_id)
            member_doc.update(unmute_date=date, **data)
            await member_doc.sync()

    async def _unmute(self, *members):
        guild = self.bot.get_guild(config.guild_id)
        mute_role = guild.get_role(config.mute_role)

        for member_id in members:
            member = guild.get_member(member_id)

            await self.remove_member_from_unmute_queue(member_id)

            if member:
                await member.remove_roles(mute_role, reason=f'Por {guild.me}')
            else:
                member = FakeMember(member_id, guild)

            self.bot.dispatch('mod_action', 'unmute', guild.me, member)

            await self.bot.mutes_col.delete(member_id)

    async def remove_member_from_unmute_queue(self, member):
        for date, muted_members in self.current_mutes.items():
            await asyncio.sleep(0)
            if member in muted_members:
                muted_members.remove(member)
                if muted_members:
                    self.current_mutes[date] = muted_members
                else:
                    del self.current_mutes[date]
                break


def setup(bot):
    bot.add_cog(TempMuteFEAT(bot))
