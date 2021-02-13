import re
import json
import asyncio
from datetime import timedelta
from functools import partial
from typing import Dict, Any
import traceback

import humanize
from discord import Object, Asset, Guild


_time_pattern = (
    r'(?:(?P<days>\d{1,3})(?:dias?|d))?'
    r'(?:(?P<hours>\d{1,2})(?:horas?|h))?'
    r'(?:(?P<minutes>\d{1,2})(?:minutos?|m))?'
    r'(?:(?P<seconds>\d{1,2})(?:segundos?|s))?'
)


def parse_time(time: str):
    """Converte uma string para timedelta.

    Parameters
    ----------
    time: :class:`str`
        A string para converter, deve estar no formato:
            0d0h0m0s
            0dia0hora0minuto0segundo
            0dias0horas0minutos0segundos

    Returns
    -------
    :class:`timedelta`
        O timedelta representando o tempo passado.
    """
    parsed_time = re.search(_time_pattern.replace(' ', ''), time.lower(), re.VERBOSE)

    times_dict = parsed_time.groupdict()

    for key, value in times_dict.items():
        if isinstance(value, str):
            times_dict[key] = int(value)
        else:
            times_dict[key] = 0

    return timedelta(**times_dict)


__data_cache = {}


def get_data(name: str) -> Dict[str, Any]:
    from_cache = __data_cache.get(name)
    if from_cache:
        return from_cache
    with open(f'src/data/{name}') as f:
        if name.endswith('.json'):
            __data_cache[name] = json.load(f)
        else:
            __data_cache[name] = f.read()
    return __data_cache[name]


async def safe_cancel(task: asyncio.Task):
    """Cancela uma task sem dar CancelledError."""
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


format_delta = partial(humanize.precisedelta, format='%d', minimum_unit='minutes')


class FakeMember(Object):
    """Usado pelo modlog."""

    def __init__(self, id_: int, guild: Guild):
        super().__init__(id_)
        self._guild = guild

    @property
    def mention(self):
        return str(self.id)

    @property
    def roles(self):
        return []

    @property
    def guild(self):
        return self._guild

    @property
    def avatar_url(self):
        # pylint: disable=protected-access
        return Asset(self._guild._state, '/embed/avatars/0.png')

    def __str__(self):
        return str(self.id)


def get_exception(e: Exception, size: int = 3):
    tb = traceback.extract_tb(e.__traceback__)[-size:]
    exc = ''.join(traceback.format_list(tb))

    # Por algum motivo ele não retorna o erro em si,
    # então tenho que inserir manualmente.
    exc += f'{e.__class__.__name__}: {e}'
    return exc
