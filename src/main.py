import os
from glob import glob

import humanize
from discord import Intents

import config
from bot import Bot

if not os.getenv('IS_HOST'):
    from dotenv import load_dotenv  # pypi: python-dotenv

    load_dotenv()

intents = Intents(**{intent: True for intent in config.intents})

bot = Bot(
    command_prefix=config.prefix,
    case_insensitive=True,
    mongo_uri=os.getenv('MONGO_URI'),
    intents=intents
)

bot.remove_command('help')
humanize.activate('pt_BR')

if __name__ == '__main__':
    extensions = glob('src/features/*.py')
    extensions.extend(glob('src/commands/**/*.py'))

    for c in extensions:
        if c.endswith('__init__.py'):
            extensions.remove(c)

    # Top 10 códigos mais bonitos \/
    extensions = ['.'.join(ext.split('/')[1:])[:-3] for ext in extensions]

    bot.load_all_extensions(extensions)

    bot.run(os.environ['TOKEN'])
