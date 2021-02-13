"""Variáveis de configuração não secretas."""
from typing import Set, Tuple

from discord import Status
from pytz import timezone

prefix = '/'

main_color = 0xe65545

owners = [
    380441229416071170,
    315599918075215872,
]

guild_id = 645380629717975070
staff_id = 809898511075508284
modlog_channel = 809920608904937512
modlog_staff_channel = 809927462091882527
errors_channel = 809927477946089523
vip_role = 809895870354423819
premium_roles = {
    'subs': 750087054255456346,
    'members': 744607011664298074,
    'booster': 677330776391680031
}
members_role = 770099851907563540
verification_category = 809890142767939634

mute_role = 771097010391875584

intents = ['guilds', 'members', 'emojis', 'guild_messages', 'guild_reactions']

tz = timezone('America/Sao_Paulo')

emotes = [
    '<:1_:784299984316661801>', '<:2_:784299993775210526>',
    '<:3_:784300009050603532>', '<:4_:784300018575736872>',
    '<:5_:784300032324403200>', '<:6_:784300050822070322>',
    '<:7_:784300066994913301>', '<:8_:784300077933527070>',
    '<:9_:784300090655375370>', '<:ponto:784304042259251200>'
]

presences: Set[Tuple[Status, int, str]] = {
    #   Jogando: 0
    #   Transmitindo: 1
    #   Ouvindo: 2
    #   Assistindo: 3
    (Status.dnd, 3, 'youtube.com/alelixo'),
    (Status.dnd, 2, 'algumas denuncias.'),
    (Status.dnd, 3, 'discord.gg/ZTzrbrs'),
}

del Set, Status, Tuple, timezone
