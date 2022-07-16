import logging
from logging.handlers import RotatingFileHandler
from os import getenv, listdir

from discord.ext import commands
from dotenv import load_dotenv


# Logger -------------------------------------------------------------------- #
def setup_logger() -> logging.Logger:
    """Sets up discord logger and adds streamhandler and filehandler to it."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logformat = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )

    filehandler = RotatingFileHandler(
        filename='discord.log',
        maxBytes=(5 * 1024 * 1024),
        encoding='utf-8'
    )
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(logformat)

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.INFO)
    streamhandler.setFormatter(logformat)

    logger.addHandler(streamhandler)
    logger.addHandler(filehandler)

    return logger


# Main function ------------------------------------------------------------- #
def main():
    logger = setup_logger()
    load_dotenv()

    client = commands.Bot(command_prefix='`')
    client.remove_command('help')

    for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f'Loaded extension: {filename[:-3]}')

    client.run(getenv('TOKEN'))


if __name__ == '__main__':
    main()
