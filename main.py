from os import listdir, getenv

from discord.ext import commands


def main():
    client = commands.Bot(command_prefix='`')
    client.remove_command('help')

    for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded extension: {filename[:-3]}')

    client.run(getenv('TOKEN'))


if __name__ == '__main__':
    main()
