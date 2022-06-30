from discord import Embed

GREEN = 0x4BDB82
BLACK = 0x000000
YELLOW = 0xDBBF40
BLUE = 0x6160DB
RED = 0xDB3D35

CREATE = 0
START = 1
END = 2
JOIN = 3
LEAVE = 4
PARTICIPANTS = 5
TIMEOUT = 6
ALREADY_CREATED = 7
NOT_CREATED = 8
JOIN_ERROR = 9
LEAVE_ERROR = 10
IMPORT_ERROR = 11

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
