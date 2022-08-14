from discord import Embed

# custom colors
GREEN = 0x4BDB82
BLACK = 0x000000
YELLOW = 0xDBBF40
BLUE = 0x6160DB
RED = 0xDB3D35

# dictionary keys as integers
CREATE = 0
START = 1
END = 2
JOIN = 3
LEAVE = 4
PARTICIPANTS = 5
TIMEOUT = 6
ALREADY_CREATED = 7
NOT_CREATED = 8
ALREADY_IN_GAME = 9
NOT_IN_GAME = 10
IMPORT_ERROR = 11
LOADED_QUESTIONS = 12
TRUTH_OR_DARE_QUESTION = 13
TRUTH = 14
DARE = 15
NOT_ENOUGH_PLAYERS = 16
NOT_LOADED_QUESTIONS = 17
EMPTY_QUERY = 18
USER_NOT_CONNECTED = 19
NOT_CONNECTED = 20
CLEARED = 21
QUEUE = 22
CURRENTLY_PLAYING = 23
NO_MORE_QUESTIONS = 24
MISSING_ARGUMENT = 25
NOT_FOUND = 26
SUCCESSFULLY_ADDED = 27
ALREADY_ADDED = 28
SUCCESSFULLY_REMOVED = 29
NO_SUBREDDITS = 30
SUBREDDITS = 31
NO_MUSIC = 32
NOT_PAUSED = 33

mlt = {
    START: Embed(
        title='Most Likely To game started!',
        description='''Select question pack to start the game:
        1. Mixed''',
        color=GREEN
    ),
    IMPORT_ERROR: Embed(
        title='Oops...! Something\'s wrong while loading questions!',
        description='Please contact creator of bot. Sorry!',
        color=BLACK
    ),
    TIMEOUT: Embed(
        title='Time\'s out! Game ended!',
        color=YELLOW
    ),
    END: Embed(
        title='Most Likely To game ended!',
        color=YELLOW
    ),
    ALREADY_CREATED: Embed(
        title='Game on this channel is already created!',
        color=RED
    ),
    NOT_CREATED: Embed(
        title='There isn\'t created game on this channel!',
        color=RED
    ),
    NO_MORE_QUESTIONS: Embed(
        title='No more questions! Game ended!',
        color=YELLOW
    )
}

tod = {
    CREATE: Embed(
        title='Truth Or Dare game created!',
        description='''Select question pack to start the game:
        1. Mixed''',
        color=GREEN
    ),
    LOADED_QUESTIONS: Embed(
        title='Truths and dares loaded!',
        description='Use join_tod to join the game.',
        color=GREEN
    ),
    IMPORT_ERROR: Embed(
        title='Oops...! Something\'s wrong while loading questions!',
        description='Please contact creator of bot. Sorry!',
        color=BLACK
    ),
    TIMEOUT: Embed(
        title='Time\'s out! Game ended!',
        color=YELLOW
    ),
    JOIN: Embed(
        title='Truth Or Dare game joined!',
        description='Current participants:',
        color=GREEN
    ),
    LEAVE: Embed(
        title='Truth Or Dare game left!',
        description='Current participants:',
        color=RED
    ),
    PARTICIPANTS: Embed(
        title='Current participants:',
        color=RED
    ),
    END: Embed(
        title='Truth Or Dare game ended!',
        color=YELLOW
    ),
    ALREADY_CREATED: Embed(
        title='Game on this channel is already created!',
        color=RED
    ),
    ALREADY_IN_GAME: Embed(
        title='You\'re already in game!',
        color=RED
    ),
    NOT_IN_GAME: Embed(
        title='You\'re not in game!',
        color=RED
    ),
    NOT_CREATED: Embed(
        title='Game on this channel isn\'t created!',
        color=RED
    ),
    TRUTH_OR_DARE_QUESTION: Embed(
        title='Truth or Dare?',
        description='',
        color=BLUE
    ),
    TRUTH: Embed(
        title='Truth',
        description='',
        color=BLUE
    ),
    DARE: Embed(
        title='Dare',
        description='',
        color=BLUE
    ),
    NOT_ENOUGH_PLAYERS: Embed(
        title='At least two players are required to start the game!',
        color=RED
    ),
    NOT_LOADED_QUESTIONS: Embed(
        title='Load questions before starting the game!',
        color=RED
    ),
    NO_MORE_QUESTIONS: Embed(
        title='No more truths or dares! Game ended!',
        color=YELLOW
    )
}

music = {
    EMPTY_QUERY: Embed(
        title='Pass name of the song or link!',
        color=RED
    ),
    USER_NOT_CONNECTED: Embed(
        title='You are not connected to a voice channel!',
        color=RED
    ),
    NOT_CONNECTED: Embed(
        title='I\'m not connected to voice channel!',
        color=RED
    ),
    CLEARED: Embed(
        title='Music queue cleared.',
        color=BLUE
    ),
    QUEUE: Embed(
        title='Music queue:',
        color=BLUE
    ),
    CURRENTLY_PLAYING: Embed(
        title='Currently playing:',
        color=BLUE
    ),
    NO_MUSIC: Embed(
        title='No song is currently playing!',
        color=RED
    ),
    NOT_PAUSED: Embed(
        title='Song is not paused!',
        color=RED
    )
}

rs = {
    MISSING_ARGUMENT: Embed(
        title='You have to type subreddit name after command!',
        color=RED
    ),
    NOT_FOUND: Embed(
        title='Subreddit not found!',
        color=RED
    ),
    SUCCESSFULLY_ADDED: Embed(
        title='Subreddit added to this channel!',
        color=GREEN
    ),
    ALREADY_ADDED: Embed(
        title='This subreddit is already added to this channel!',
        color=RED
    ),
    NOT_CONNECTED: Embed(
        title='This subreddit is not connected to this channel!',
        color=RED
    ),
    SUCCESSFULLY_REMOVED: Embed(
        title='This subreddit will no longer be connected to this channel.',
        color=GREEN
    ),
    NO_SUBREDDITS: Embed(
        title='There aren\'t any subreddits connected to this channel!',
        color=RED
    ),
    SUBREDDITS: Embed(
        title='Connected subreddits:',
        description='',
        color=BLUE
    )
}
