from logging import getLogger

from discord import FFmpegPCMAudio
from discord.ext import commands
from syncer import sync
from youtube_dl import YoutubeDL

import embeds as e

logger = getLogger('discord')

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

instances = {}  # music instances (connected voice channels)


class MusicInstance:
    def __init__(self, client, voice_channel) -> None:
        self.client = client
        self.voice_channel = voice_channel
        self.voice_client = None  # connection with vc, used for playing songs
        self.queue = []
        self.channel = None
        self.is_playing = False  # is there a song that is currently played
        self.is_paused = False

    @sync  # I want to use await in here, but I can't call await in lambda
    async def _play_next(self) -> None:  # that's why I hope @sync will work
        """
        Gets next song from queue, plays it and sends embed with current song's
        title.
        """
        if not self.queue:
            self.is_playing = False
            return

        self.is_playing = True
        song_data = self.queue.pop(0)
        url = song_data['source']
        title = song_data['title']

        self.voice_client.play(
            FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda: self._play_next()
        )
        embed = e.music[e.CURRENTLY_PLAYING].copy()
        embed.description = title
        await self.channel.send(embed=embed)

    async def play_music(self, ctx) -> None:
        """
        Plays song for the first time. It connects to the voice channel, plays
        a song and sends an embed with current song's title.
        """
        self.is_playing = True
        song_data = self.queue.pop(0)
        url = song_data['source']
        title = song_data['title']

        if self.voice_client is None:
            self.voice_client = await self.voice_channel.connect()
        if not self.voice_client.is_connected():
            self.voice_client = await self.voice_channel.connect()

        self.voice_client.play(
            FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda: self._play_next()
        )
        embed = e.music[e.CURRENTLY_PLAYING].copy()
        embed.description = title
        message = await ctx.send(embed=embed)
        self.channel = message.channel


class MoriohChoRadio(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    def _search(self, query: str) -> dict:
        """Searches YouTube for a specified query."""
        ydl = YoutubeDL(YDL_OPTIONS)
        try:
            # I'm taking only one result, later I can take like 10 entries
            result = ydl.extract_info(f'ytsearch:{query}', download=False)
            song = result['entries'][0]
        except Exception as err:
            # for now I want to know which errors it can catch
            logger.error(f'Unhandled error in MoriohChoRadio._search: {err}')
            return {}
        return {'source': song['formats'][0]['url'], 'title': song['title']}

    # Decorators ------------------------------------------------------------ #
    def is_MusicInstance_created() -> bool:
        """
        Simple decorator that checks if MusicInstance is created for guild.
        It means that music is played even if someone kicked the bot from vc.
        """
        async def predicate(ctx) -> bool:
            return str(ctx.guild.id) in instances.keys()
        return commands.check(predicate)

    # Commands -------------------------------------------------------------- #
    @commands.command(aliases=['p'])
    async def play(self, ctx, *args):
        """Plays a song with the given title or link."""
        # get voice channel and send error if user not connected
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send(embed=e.music[e.USER_NOT_CONNECTED])
            return

        key = str(ctx.guild.id)

        query = ' '.join(args)  # get title/url from command
        if query == '':
            # unpause song if paused
            if key in instances.keys() and instances[key].is_paused:
                instances[key].is_paused = False
                instances[key].voice_client.resume()
            else:  # query is empty and song is not paused
                await ctx.send(embed=e.music[e.EMPTY_QUERY])
            return

        # get song data from YouTube
        song_data = self._search(query)
        # create MusicInstance for guild if not created
        if key not in instances.keys():
            instances[key] = MusicInstance(self.client, voice_channel)

        # add song to queue and play it if bot doesn't play anything
        instances[key].queue.append(song_data)
        if not instances[key].is_playing:
            await instances[key].play_music(ctx)

    @commands.command()
    @is_MusicInstance_created()
    async def pause(self, ctx):
        """Pauses (or resumes) current song."""
        key = str(ctx.guild.id)
        if not instances[key].is_playing:
            await ctx.send(embed=e.music[e.NO_MUSIC])
            return

        if not instances[key].is_paused:
            instances[key].voice_client.pause()
        else:
            instances[key].voice_client.resume()
        instances[key].is_paused = not instances[key].is_paused

    @commands.command(aliases=['r'])
    @is_MusicInstance_created()
    async def resume(self, ctx):
        """Resumes current song."""
        key = str(ctx.guild.id)
        if not instances[key].is_playing:
            await ctx.send(embed=e.music[e.NO_MUSIC])
            return

        if instances[key].is_paused:
            instances[key].voice_client.resume()
            instances[key].is_playing = True
        else:
            await ctx.send(embed=e.music[e.NOT_PAUSED])

    @commands.command(aliases=['s'])
    @is_MusicInstance_created()
    async def skip(self, ctx):
        """Skips current song and tries to play next one in the queue."""
        key = str(ctx.guild.id)
        if not instances[key].is_playing:
            await ctx.send(embed=e.music[e.NO_MUSIC])
            return

        instances[key].voice_client.stop()
        await instances[key].play_music(ctx)

    @commands.command(aliases=['q'])
    @is_MusicInstance_created()
    async def queue(self, ctx):
        """Shows songs in music queue."""
        key = str(ctx.guild.id)
        if key not in instances.keys():  # send proper embed if not connected
            await ctx.send(embed=e.music[e.NOT_CONNECTED])
        else:  # send embed with song queue
            embed = e.music[e.QUEUE].copy()
            if len(instances[key].queue) == 0:
                embed.add_field(name='-')
            else:
                # display next 5 songs
                for i, entry in enumerate(instances[key].queue[:5]):
                    embed.add_field(
                        name=f'{i + 1}. {entry["title"]}', inline=False
                    )
            await ctx.send(embed=embed)

    @commands.command(aliases=['c'])
    @is_MusicInstance_created()
    async def clear(self, ctx):
        """Stops currently played music and clear queue."""
        key = str(ctx.guild.id)
        if key not in instances.keys():
            await ctx.send(embed=e.music[e.NOT_CONNECTED])
        else:
            instances[key].voice_client.stop()
            instances[key].queue = []
            await ctx.send(embed=e.music[e.CLEARED])

    @commands.command(aliases=['l'])
    @is_MusicInstance_created()
    async def leave(self, ctx):
        """Kicks the bot from voice channel and delete music instance."""
        key = str(ctx.guild.id)
        instances[key].voice_client.stop()
        if instances[key].voice_client.is_connected():
            await instances[key].voice_client.disconnect()
        del instances[key]

    # Errors ---------------------------------------------------------------- #
    @pause.error
    @resume.error
    @queue.error
    @clear.error
    @leave.error
    async def MusicInstance_not_created_error(self, ctx, error):
        """Error handler if MusicInstance is not created for guild."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=e.mlt[e.NOT_CONNECTED])
        else:
            logger.error(f'Unknown error in start_mlt: {error}')


def setup(client):
    client.add_cog(MoriohChoRadio(client))
