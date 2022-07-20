from logging import getLogger

from discord import FFmpegPCMAudio
from discord.ext import commands
from youtube_dl import YoutubeDL

import embeds as e

logger = getLogger('discord')

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

instances = {}  # music instances (connected voice channels)


class MusicInstance:
    def __init__(self, client, voice_channel) -> None:
        self.client = client
        self.voice_channel = voice_channel
        self.voice_client = None
        self.queue = []

    def play_next(self):
        song_data = self.queue.pop(0)
        url = song_data['source']
        title = song_data['title']

        self.voice_client.play(
            FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda: self.play_next()
        )
        embed = e.music[e.CURRENTLY_PLAYING].copy()
        embed.description = title

    async def play_music(self, ctx) -> None:
        song_data = self.queue.pop(0)
        url = song_data['source']
        title = song_data['title']

        if self.voice_client is None:
            self.voice_client = await self.voice_channel.connect()
        if not self.voice_client.is_connected():
            self.voice_client = await self.voice_channel.connect()

        self.voice_client.play(
            FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda: self.play_next()
        )
        embed = e.music[e.CURRENTLY_PLAYING].copy()
        embed.description = title
        await ctx.send(embed=embed)


class MoriohChoRadio(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    def _search(self, query: str) -> dict:
        """Search YouTube for specified query."""
        ydl = YoutubeDL(YDL_OPTIONS)
        try:
            # I'm taking only one result, later I can take like 10 entries
            result = ydl.extract_info(f'ytsearch:{query}', download=False)
            song = result['entries'][0]
        except Exception as err:
            # for now I want to know which errors it can catch
            logger.error(f'Unhandled exception: {err}')
            return {}
        return {'source': song['formats'][0]['url'], 'title': song['title']}

    # Commands -------------------------------------------------------------- #
    @commands.command()
    async def play(self, ctx, *args):
        """Plays a song with the given title or link."""
        # get text from command and send error if empty
        query = ' '.join(args)
        if query == '':
            await ctx.send(embed=e.music[e.EMPTY_QUERY])
            return

        # get voice channel and send error if user not connected
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send(embed=e.music[e.USER_NOT_CONNECTED])
            return

        key = str(ctx.guild.id)
        song_data = self._search(query)
        if key not in instances.keys():
            instances[key] = MusicInstance(self.client, voice_channel)

        instances[key].queue.append(song_data)
        await instances[key].play_music(ctx)

    @commands.command()
    async def queue(self, ctx):
        """Shows songs in music queue."""
        key = str(ctx.guild.id)
        if key not in instances.keys():
            await ctx.send(embed=e.music[e.NOT_CONNECTED])
        else:
            embed = e.music[e.QUEUE].copy()
            if len(instances[key].queue) == 0:
                embed.add_field(name='-')
            else:
                for i, entry in enumerate(instances[key].queue[:5]):
                    embed.add_field(
                        name=f'{i + 1}. {entry["title"]}', inline=False
                    )
            await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx):
        """Stops currently played music and clear queue."""
        key = str(ctx.guild.id)
        if key not in instances.keys():
            await ctx.send(embed=e.music[e.NOT_CONNECTED])
        else:
            instances[key].voice_client.stop()
            instances[key].queue = []
            await ctx.send(embed=e.music[e.CLEARED])

    @commands.command()
    async def leave(self, ctx):
        """Kicks the bot from voice channel and delete music instance."""
        key = str(ctx.guild.id)
        if key not in instances.keys():
            await ctx.send(embed=e.music[e.NOT_CONNECTED])
        else:
            await instances[key].voice_client.disconnect()
            del instances[key]


def setup(client):
    client.add_cog(MoriohChoRadio(client))
