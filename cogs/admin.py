from logging import getLogger
from os import listdir

from discord.ext import commands

logger = getLogger('discord')


class Admin(commands.Cog):
    """
    Simple cog with commands to manage other cogs. These commands are allowed
    only for bot owner.
    """
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        try:
            self.client.load_extension(f'cogs.{cog}')
            logger.info(f'Extension {cog} loaded successfully.')
            await ctx.send(f'Extension {cog} loaded successfully.')

        except commands.ExtensionAlreadyLoaded:
            logger.info(f'Extension {cog} is already loaded.')
            await ctx.send(f'Extension {cog} is already loaded.')

        except commands.ExtensionNotFound:
            logger.info(f'Extension {cog} doesn\'t exist.')
            await ctx.send(f'Extension {cog} doesn\'t exist.')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        if cog == 'admin':
            logger.info('Can\'t unload admin extension!')
            await ctx.send('Can\'t unload admin extension!')
            return

        try:
            self.client.unload_extension(f'cogs.{cog}')
            logger.info(f'Extension {cog} unloaded successfully.')
            await ctx.send(f'Extension {cog} unloaded successfully.')

        except commands.ExtensionNotLoaded:
            cogs = [filename[:-3] for filename in listdir('./cogs')]
            if cog in cogs:
                logger.info(f'Extension {cog} is already unloaded.')
                await ctx.send(f'Extension {cog} is already unloaded.')
            else:
                logger.info(f'Extension {cog} is doesn\'t exist.')
                await ctx.send(f'Extension {cog} is doesn\'t exist.')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        if cog == 'admin':
            logger.info('Can\'t reload admin extension!')
            await ctx.send('Can\'t reload admin extension!')
            return

        try:
            self.client.unload_extension(f'cogs.{cog}')
            self.client.load_extension(f'cogs.{cog}')
            logger.info(f'Extension {cog} reloaded successfully.')
            await ctx.send(f'Extension {cog} reloaded successfully.')

        except commands.ExtensionNotLoaded:
            cogs = [filename[:-3] for filename in listdir('./cogs')]
            if cog in cogs:
                self.client.load_extension(f'cogs.{cog}')
                logger.info(f'Extension {cog} reloaded successfully.')
                await ctx.send(f'Extension {cog} reloaded successfully.')
            else:
                logger.info(f'Extension {cog} is doesn\'t exist.')
                await ctx.send(f'Extension {cog} is doesn\'t exist.')

    @commands.command()
    @commands.is_owner()
    async def clear_logs(self, ctx):
        with open('discord.log', 'w'):
            logger.info('Cleared logs.')


def setup(client):
    client.add_cog(Admin(client))
