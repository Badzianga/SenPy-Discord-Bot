from os import listdir

from discord.ext import commands


class Admin(commands.Cog):
    """
    Simple cog with commands to load/unload other cogs. These commands are
    allowed only for owner.
    """
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        try:
            self.client.load_extension(f'cogs.{cog}')
            print(f'Extension {cog} loaded successfully.')
            await ctx.send(f'Extension {cog} loaded successfully.')
        except commands.ExtensionAlreadyLoaded:
            print(f'Extension {cog} is already loaded.')
            await ctx.send(f'Extension {cog} is already loaded.')
        except commands.ExtensionNotFound:
            print(f'Extension {cog} doesn\'t exist.')
            await ctx.send(f'Extension {cog} doesn\'t exist.')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        if cog == 'admin':
            print('Can\'t unload admin extension!')
            await ctx.send('Can\'t unload admin extension!')
            return
        try:
            self.client.unload_extension(f'cogs.{cog}')
            print(f'Extension {cog} unloaded successfully.')
            await ctx.send(f'Extension {cog} unloaded successfully.')
        except commands.ExtensionNotLoaded:
            cogs = [filename[:-3] for filename in listdir('./cogs')]
            if cog in cogs:
                print(f'Extension {cog} is already unloaded.')
                await ctx.send(f'Extension {cog} is already unloaded.')
            else:
                print(f'Extension {cog} is doesn\'t exist.')
                await ctx.send(f'Extension {cog} is doesn\'t exist.')


def setup(client):
    client.add_cog(Admin(client))
