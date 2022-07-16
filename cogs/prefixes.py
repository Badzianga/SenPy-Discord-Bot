import json
from logging import getLogger
from os import listdir

from discord.ext import commands

logger = getLogger('discord')


class PrefixManager(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    # Listeners ------------------------------------------------------------- #
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Create prefixes.json file if it doesn't exist. Then set default prefix
        for guilds added during bot absence.
        """
        # create file
        if 'prefixes.json' not in listdir():
            with open('prefixes.json', 'w') as f:
                json.dump({}, f)
            logger.info('Created prefixes.json')

        # set default prefix
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        for guild in self.client.guilds:
            if str(guild.id) not in prefixes.keys():
                prefixes[str(guild.id)] = '`'
                logger.info(f'Set default prefix for guild {guild.id}')

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Add default command prefix for joined guild."""
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = '`'

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Remove guild id from prefixes dictionary."""
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        del prefixes[str(guild.id)]

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

    # Commands -------------------------------------------------------------- #
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Change guild prefix."""
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

        await ctx.send(f'Changed command prefix to {prefix}')


def setup(client):
    client.add_cog(PrefixManager(client))
