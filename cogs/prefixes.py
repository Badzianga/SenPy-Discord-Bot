import json
from logging import getLogger
from os import listdir

from discord.ext import commands

import embeds as e

logger = getLogger('discord')


class PrefixManager(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    # Listeners ------------------------------------------------------------- #
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Create prefixes.json file if it doesn't exist. Then set default prefix
        for guilds added during bot absence and clear guilds deleted during bot
        absence.
        """
        # create file
        if 'prefixes.json' not in listdir():
            with open('prefixes.json', 'w') as f:
                json.dump({}, f)
            logger.info('Created prefixes.json')

        # load prefixes
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        # set default prefix for guilds added during bot absence
        for guild in self.client.guilds:
            if str(guild.id) not in prefixes.keys():
                prefixes[str(guild.id)] = '`'
                logger.info(f'Set default prefix for guild {guild.id}')

        # delete unused guild ids (removed guilds during bot absence)
        client_guild_ids = set([str(guild.id) for guild in self.client.guilds])
        to_delete = []
        for guild_id in prefixes.keys():
            if guild_id not in client_guild_ids:
                to_delete.append(guild_id)
        # deleting keys during iteration throws RuntimeError
        for guild_id in to_delete:
            del prefixes[guild_id]
            logger.info(f'Deleted guild {guild_id} from prefixes')

        # save prefixes
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
    async def change_prefix(self, ctx, prefix: str):
        """Change guild prefix."""

        # prefix should only be one character
        if len(prefix) != 1:
            await ctx.send(embed=e.prefixes[e.TOO_SHORT])
            return

        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

        # send embed message with new prefix
        embed = e.prefixes[e.CHANGED]
        embed.description += prefix
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(PrefixManager(client))
