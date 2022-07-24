from asyncio import TimeoutError
from itertools import cycle
from logging import getLogger
from random import shuffle

from discord.ext import commands

import embeds as e

logger = getLogger('discord')

PACKS = {'1️⃣': ('mixed_truths.txt', 'mixed_dares.txt')}
T_D_EMOJIS = ('🇹', '🇩')

games = {}


class Game:
    def __init__(self, client, ctx) -> None:
        self.client = client
        self.ctx = ctx
        self.msg = None
        self.truths = None
        self.dares = None
        self.players = []
        self.current_player = None
        # used for preventing KeyError in _after_timeout after typing end_todf
        self.wait_for_reaction_coroutine = None

    async def _after_timeout(self) -> None:
        """
        Deletes key from the 'games' dictionary when timeout occurs. Removes
        all reactions from game message and changes it's content.
        """
        key = str(self.ctx.channel.id)
        await self.msg.edit(embed=e.tod[e.TIMEOUT])
        await self.msg.clear_reactions()
        del games[key]

    def _check_number_reaction(self, reaction, user) -> bool:
        """Checks if user reacted with proper number emoji to select pack."""
        if user == self.client.user or reaction.message != self.msg:
            return False
        return str(reaction.emoji) in PACKS.keys()

    def _check_td_reaction(self, reaction, user) -> bool:
        """Checks if right user reacted with right emoji."""
        if user != self.current_player or reaction.message != self.msg:
            return False
        return str(reaction.emoji) in T_D_EMOJIS

    async def _load_questions(self, reaction) -> None:
        """
        Loads questions from file. File is selected by proper reaction. After
        selection, embed with information is sended.
        """
        try:
            # get pack filenames
            truths_filename, dares_filename = PACKS[str(reaction.emoji)]
            # load truths
            with open(f'files/tod/{truths_filename}', 'r') as pack:
                self.truths = pack.read().strip('\n').split('\n')
                shuffle(self.truths)
            # load dares
            with open(f'files/tod/{dares_filename}', 'r') as pack:
                self.dares = pack.read().strip('\n').split('\n')
                shuffle(self.dares)
            # clear reactions and send success message
            await self.msg.clear_reactions()
            await self.msg.edit(embed=e.tod[e.LOADED_QUESTIONS])
        except FileNotFoundError as err:
            await self.msg.clear_reactions()
            await self.msg.edit(embed=e.mlt[e.IMPORT_ERROR])
            logger.error(f'Error while loading ToD questions ({err})')
            del games[str(self.ctx.channel.id)]

    async def select_pack(self) -> None:
        """
        Function used for selecting question pack by reacting with proper emoji
        under the message with packs names. Selected packs are stored as lists
        in self.truths and self.dares variables.
        """
        self.msg = await self.ctx.send(embed=e.tod[e.CREATE])

        for emoji in PACKS.keys():
            await self.msg.add_reaction(emoji)

        try:
            # waits for proper reaction; if time expires, game ends
            self.wait_for_reaction_coroutine = self.client.wait_for(
                'reaction_add', timeout=30.0, check=self._check_number_reaction
            )
            reaction, _ = await self.wait_for_reaction_coroutine
            await self._load_questions(reaction)
        except TimeoutError:
            await self._after_timeout()

    async def start(self) -> None:
        """
        Main loop of the game. It changes current player, sends question, waits
        for reaction and gives truth or dare. After that, the cycle repeats.
        """
        # firstly, change players list to cycle object
        self.players = cycle(self.players)

        try:
            while self.truths and self.dares:  # both of lists can't be empty
                self.current_player = next(self.players)

                embed = e.tod[e.TRUTH_OR_DARE_QUESTION]
                embed.description = f'Current user: {self.current_player.name}'
                self.msg = await self.ctx.send(embed=embed)
                await self.msg.add_reaction('🇹')
                await self.msg.add_reaction('🇩')
                self.wait_for_reaction_coroutine = self.client.wait_for(
                    'reaction_add', timeout=600.0,
                    check=self._check_td_reaction
                )
                reaction, _ = await self.wait_for_reaction_coroutine
                await self.msg.clear_reactions()

                if str(reaction.emoji) == '🇹':
                    embed = e.tod[e.TRUTH]
                    embed.description = self.truths.pop()
                elif str(reaction.emoji) == '🇩':
                    embed = e.tod[e.DARE]
                    embed.description = self.dares.pop()
                await self.msg.edit(embed=embed)
            # end the game after all questions
            key = str(self.ctx.channel.id)
            await self.msg.clear_reactions()
            await self.msg.edit(embed=e.tod[e.NO_MORE_QUESTIONS])
            del games[key]

        except TimeoutError:
            await self._after_timeout()


class TruthOrDare(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    # Decorators ------------------------------------------------------------ #
    def is_game_not_created() -> bool:
        """Simple decorator that checks if the game is not created."""
        async def predicate(ctx) -> bool:
            return str(ctx.channel.id) not in games.keys()
        return commands.check(predicate)

    def is_game_created() -> bool:
        """Simple decorator that checks if the game is created."""
        async def predicate(ctx):
            return str(ctx.channel.id) in games.keys()
        return commands.check(predicate)

    def is_user_not_in_game() -> bool:
        """Simple decorator that checks if player is not in the game."""
        async def predicate(ctx):
            return ctx.author not in games[str(ctx.channel.id)].players
        return commands.check(predicate)

    def is_user_in_game() -> bool:
        """Simple decorator that checks if player is in the game."""
        async def predicate(ctx):
            return ctx.author in games[str(ctx.channel.id)].players
        return commands.check(predicate)

    # Listeners ------------------------------------------------------------- #
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        Checks deleted messages. When games dictionary is empty, it skips
        further actions. When at least one game exists, listener checks whether
        deleted message is a game message and deletes proper game if so.
        """
        if not games:
            return
        key = str(payload.channel_id)
        if key in games.keys():
            if payload.message_id == games[key].msg.id:
                games[key].wait_for_reaction_coroutine.close()
                await games[key].message.channel.send(embed=e.mlt[e.END])
                del games[key]

    @commands.Cog.listener()
    async def on_guild_channel_delete(channel):
        """
        Checks deleted channels. If channel has active game, listener properly
        deletes it.
        """
        if not games:
            return
        key = str(channel.id)
        if key in games.keys():
            games[key].wait_for_reaction_coroutine.close()
            del games[key]

    @commands.Cog.listener()
    async def on_guild_remove(guild):
        """
        Checks left guild events. If any of channels in the guild had active
        game, listener properly deletes this game.
        """
        if not games:
            return
        for channel in guild.channels:
            key = str(channel.id)
            if key in games.keys():
                games[key].wait_for_reaction_coroutine.close()
                del games[key]

    # Commands -------------------------------------------------------------- #
    @commands.command()
    @is_game_not_created()
    async def create_tod(self, ctx):
        """
        Creates Truth Or Dare game and calls select_pack() method in created
        game object.
        """
        key = str(ctx.channel.id)
        games[key] = Game(self.client, ctx)
        await games[key].select_pack()

    @commands.command()
    @is_game_created()
    async def end_tod(self, ctx):
        """Ends Truth or Dare game and removes game object from dictionary."""
        key = str(ctx.channel.id)
        await games[key].msg.clear_reactions()
        await ctx.send(embed=e.tod[e.END])
        games[key].wait_for_reaction_coroutine.close()
        del games[key]

    @commands.command()
    @is_user_not_in_game()
    @is_game_created()
    async def join_tod(self, ctx):
        """Adds user to Truth or Dare game and shows current participants."""
        key = str(ctx.channel.id)
        games[key].players.append(ctx.author)

        embed = e.tod[e.JOIN].copy()
        embed.description += '\n' + '\n'.join(
            [player.name for player in games[key].players]
        )
        await ctx.send(embed=embed)

    @commands.command()
    @is_user_in_game()
    @is_game_created()
    async def leave_tod(self, ctx):
        """
        Removes user from Truth or Dare game and shows remaining participants.
        """
        key = str(ctx.channel.id)
        games[key].players.remove(ctx.author)

        embed = e.tod[e.LEAVE].copy()
        embed.description += '\n' + '\n'.join(
            [player.name for player in games[key].players]
        )
        await ctx.send(embed=embed)

    @commands.command()
    @is_game_created()
    async def tod_participants(self, ctx):
        """Shows Truth or Dare participants."""
        key = str(ctx.channel.id)

        embed = e.tod[e.PARTICIPANTS].copy()
        embed.description += '\n' + '\n'.join(
            [player.name for player in games[key].players]
        )
        await ctx.send(embed=embed)

    @commands.command()
    @is_game_created()
    async def start_tod(self, ctx):
        """Starts Truth or Dare game."""
        key = str(ctx.channel.id)
        # TODO: move this check to decorator
        if games[key].players < 2:
            await ctx.send(embed=e.tod[e.NOT_ENOUGH_PLAYERS])
        if games[key].truths is None:
            await ctx.send(embed=e.tod[e.NOT_LOADED_QUESTIONS])
        await games[key].start()

    # Errors ---------------------------------------------------------------- #
    @create_tod.error
    async def game_already_created_error(self, ctx, error):
        """Error handler if game is already created."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=e.tod[e.ALREADY_CREATED])
        else:
            logger.error(f'Unknown error: {error} (in @create_tod.error)')

    @end_tod.error
    @tod_participants.error
    @start_tod.error
    async def game_not_created_error(self, ctx, error):
        """Error handler if game isn't created"""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=e.tod[e.NOT_CREATED])
        else:
            logger.error(f'Unknown error: {error} (hard to say in which one)')

    @join_tod.error
    async def join_tod_errors(self, ctx, error):
        """Error handler if player is already in game or game isn't created."""
        if isinstance(error, commands.CheckFailure):
            if str(ctx.channel.id) in games.keys():
                await ctx.send(embed=e.tod[e.ALREADY_IN_GAME])
            else:
                await ctx.send(embed=e.tod[e.NOT_CREATED])
        else:
            logger.error(f'Unknown error: {error} (in @join_tod.error)')

    @leave_tod.error
    async def leave_tod_errors(self, ctx, error):
        """Error handler if player is not in game or game isn't created."""
        if isinstance(error, commands.CheckFailure):
            if str(ctx.channel.id) in games.keys():
                await ctx.send(embed=e.tod[e.NOT_IN_GAME])
            else:
                await ctx.send(embed=e.tod[e.NOT_CREATED])
        else:
            logger.error(f'Unknown error: {error} (in @leave_tod.error)')


def setup(client) -> None:
    client.add_cog(TruthOrDare(client))
