import json
import logging
from logging.handlers import RotatingFileHandler
from os import getenv, listdir

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv


# Logger -------------------------------------------------------------------- #
def setup_logger(config: dict) -> logging.Logger:
    """Sets up discord logger and adds streamhandler and filehandler to it."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logformat = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )

    if config['LoggingFileHandler']:
        filehandler = RotatingFileHandler(
            filename='discord.log',
            maxBytes=(config['LogFileSizeInMegabytes'] * 1024 * 1024),
            encoding='utf-8'
        )
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(logformat)
        logger.addHandler(filehandler)

    if config['LoggingStreamHandler']:
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(logging.INFO)
        streamhandler.setFormatter(logformat)
        logger.addHandler(streamhandler)

    return logger


# Intents ------------------------------------------------------------------- #
def get_intents() -> Intents:
    # I don't use all intents from Intents.default() so I'm creating my own
    # set of intents
    intents = Intents().none()
    intents.guild_messages = True
    intents.guild_reactions = True
    intents.guilds = True
    intents.voice_states = True
    return intents


# Custom prefixes ----------------------------------------------------------- #
def get_prefix(_, message) -> str:
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


# Main function ------------------------------------------------------------- #
def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    logger = setup_logger(config)
    load_dotenv()

    client = commands.Bot(command_prefix=get_prefix, intents=get_intents())
    client.remove_command('help')

    for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            if filename[:-3] in config['BlacklistedCogs']:
                logger.info(f'Skipped extension: {filename[:-3]}')
                continue
            client.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f'Loaded extension: {filename[:-3]}')

    client.run(getenv('TOKEN'))


if __name__ == '__main__':
    main()
