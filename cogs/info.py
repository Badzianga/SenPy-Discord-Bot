from logging import getLogger
from resource import getrusage, RUSAGE_SELF
from sys import version

import discord
from discord.ext import commands

logger = getLogger('discord')


class Info(commands.Cog):
    """
    Simple cog with commands which display information about bot. For now, it's
    only latency, Python and Discord.py version and RAM usage.
    """
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Bot is ready. Hello World!')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Command doesn\'t exist.')
        else:
            logger.error(f'Error which isn\'t handled anywhere: {error}')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    @commands.command()
    async def version(self, ctx):
        await ctx.send(f'Python {version}\nDiscord.py {discord.__version__}')

    @commands.command()
    async def ram(self, ctx):
        mb = round(getrusage(RUSAGE_SELF).ru_maxrss / 1024, 2)
        await ctx.send(f'RAM usage: {mb}MB')


def setup(client):
    client.add_cog(Info(client))
