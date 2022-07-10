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
        color=RED
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
    )
}
