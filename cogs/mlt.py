from asyncio import TimeoutError
from itertools import cycle
from logging import getLogger
from random import shuffle

from discord.ext import commands

import embeds as e

logger = getLogger('discord')

PACKS = {'1️⃣': 'mixed.txt'}

games = {}  # existing games (Game objects)


class Game:
    def __init__(self, client, ctx) -> None:
        self.client = client
        self.ctx = ctx
        self.questions = None
        self.msg = None
        # used for preventing KeyError in _after_timeout after typing end_mlt
        self.wait_for_reaction_coroutine = None

    async def _after_timeout(self) -> None:
        """
        Deletes key from the 'games' dictionary when timeout occurs. Removes
        all reactions from game message and changes it's content.
        """
        key = str(self.ctx.channel.id)
        await self.msg.edit(embed=e.mlt[e.TIMEOUT])
        await self.msg.clear_reactions()
        del games[key]

    def _check_arrow_reaction(self, reaction, user) -> bool:
        """Checks if user reacted with arrow emoji to give next question."""
        if user == self.client.user or reaction.message != self.msg:
            return False
        return str(reaction.emoji) == '➡️'

    def _check_number_reaction(self, reaction, user) -> bool:
        """Checks if user reacted with proper number emoji to select pack."""
        if user == self.client.user or reaction.message != self.msg:
            return False
        return str(reaction.emoji) in PACKS.keys()

    async def _load_questions(self, reaction) -> None:
        """Loads questions from file. File is selected by proper reaction."""
        try:
            with open(f'files/mlt/{PACKS[reaction.emoji]}', 'r') as pack:
                self.questions = pack.read().strip('\n').split('\n')
                shuffle(self.questions)
                self.questions = cycle(self.questions)

        except FileNotFoundError as err:
            await self.msg.clear_reactions()
            await self.msg.edit(embed=e.mlt[e.IMPORT_ERROR])
            logger.error(f'Error while loading questions ({err})')

            del games[str(self.ctx.channel.id)]

    async def select_pack(self) -> None:
        """
        Function used for selecting question pack by reacting with proper emoji
        under the message with packs. Selected pack is stored as cycle object
        in self.questions variable.
        """
        # send starting message and save it to variable
        self.msg = await self.ctx.send(embed=e.mlt[e.START])

        # add reactions under message
        for emoji in PACKS.keys():
            await self.msg.add_reaction(emoji)

        try:
            # waits for proper reaction; if time expires, end game
            self.wait_for_reaction_coroutine = self.client.wait_for(
                'reaction_add', timeout=30.0, check=self._check_number_reaction
            )
            reaction, _ = await self.wait_for_reaction_coroutine
            await self._load_questions(reaction)
        except TimeoutError:
            await self._after_timeout()

    async def start(self) -> None:
        """
        Main loop of the game. It removes old reactions, changes game message
        content and waits for next reaction to continue the game.
        """
        await self.msg.clear_reactions()
        await self.msg.add_reaction('➡️')

        try:
            while True:
                question = f'Who is most likely to {next(self.questions)}?'
                embed = e.Embed(description=question, color=e.BLUE)
                await self.msg.edit(embed=embed)
                self.wait_for_reaction_coroutine = self.client.wait_for(
                    'reaction_add', timeout=300.0,
                    check=self._check_arrow_reaction
                )
                reaction, user = await self.wait_for_reaction_coroutine
                await self.msg.remove_reaction(reaction, user)
        except TimeoutError:
            await self._after_timeout()


class MostLikelyTo(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    # Decorators ------------------------------------------------------------ #
    def is_game_created() -> bool:
        """Simple decorator that checks if the game is created."""
        async def predicate(ctx) -> bool:
            return str(ctx.channel.id) in games.keys()
        return commands.check(predicate)

    def is_game_not_created() -> bool:
        """Simple decorator that checks if the game is not created."""
        async def predicate(ctx) -> bool:
            return str(ctx.channel.id) not in games.keys()
        return commands.check(predicate)

    # Listeners ------------------------------------------------------------- #
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Checks deleted messages. When games dictionary is empty, it skips
        further actions. When at least one game exists, listener checks whether
        deleted message is a game message and deletes proper game if so.
        """
        if not games:
            return
        key = str(message.channel.id)
        if key in games.keys():
            if message == games[key].msg:
                del games[message.channel.id]
                message.channel.send(embed=e.mlt[e.END])

    # Commands -------------------------------------------------------------- #
    @commands.command()
    @is_game_not_created()
    async def start_mlt(self, ctx):
        """Starts Most Likely To game and allows to select question pack."""
        key = str(ctx.channel.id)
        games[key] = Game(self.client, ctx)
        # select_pack() can delete game after timeout occurence
        await games[key].select_pack()
        # that's why this check should exist before starting the game
        # I just prevent KeyError here
        if key in games.keys():
            await games[key].start()

    @commands.command()
    @is_game_created()
    async def end_mlt(self, ctx):
        """Ends Most Likely To game and removes game object from dictionary."""
        key = str(ctx.channel.id)
        await games[key].msg.clear_reactions()
        await games[key].msg.edit(embed=e.mlt[e.END])
        # this one closes wait_for reaction coroutine
        # thanks to that KeyError won't occur in _after_timeout
        games[key].wait_for_reaction_coroutine.close()
        del games[key]

    # Errors ---------------------------------------------------------------- #
    @start_mlt.error
    async def start_mlt_errors(self, ctx, error):
        """Error handler if game is already created."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=e.mlt[e.ALREADY_CREATED])
        else:
            logger.error(f'Unknown error in start_mlt: {error}')

    @end_mlt.error
    async def end_mlt_errors(self, ctx, error):
        """Error handler if game is not created."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=e.mlt[e.NOT_CREATED])
        else:
            logger.error(f'Unknown error in end_mlt: {error}')


def setup(client) -> None:
    client.add_cog(MostLikelyTo(client))
