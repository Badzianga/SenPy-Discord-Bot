from json import dump, load
from logging import getLogger
from os import getenv

from asyncpraw import Reddit
from asyncprawcore import NotFound
from discord.ext import commands, tasks

import embeds as e

logger = getLogger('discord')

# for now, channels, subreddits and images will be held in json file and dict
# database = {
#     channel_id: {
#            subreddit: [images]
#     }
# }
database = {}


class RedditSurfer(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = database  # now I can load json to this dict

    def _get_reddit_client(self) -> Reddit:
        """
        Returns Reddit client which takes necessary arguments from environment
        variables.
        """
        return Reddit(
            client_id=getenv('CLIENT_ID'),
            client_secret=getenv('CLIENT_SECRET'),
            user_agent=getenv('USER_AGENT')
        )

    def _save_database_to_json(self) -> None:
        """Saves database dictionary to json file."""
        with open('reddit.json', 'w') as f:
            dump(database, f, indent=4)
        logger.info('Dumped database to reddit.json')

    def _load_database_from_json(self) -> None:
        """Loads database dictionary from json file."""
        with open('reddit.json', 'r') as f:
            self.database = load(f)
        logger.info('Loaded database from reddit.json')

    # Tasks ----------------------------------------------------------------- #
    @tasks.loop(hours=1)
    async def browse_reddit(self):
        """
        Browses subscribed subreddits every hour and sends newly added images.
        """
        logger.info('Starting RedditSurfer task loop...')
        reddit = self._get_reddit_client()
        logger.info('Connected to Reddit!')

        for channel_id, subreddits in database.items():
            channel = self.client.get_channel(int(channel_id))
            for subreddit_name, urls in subreddits.items():
                subreddit = reddit.subreddit(subreddit_name)
                logger.info(
                    f'Sending images from r/{subreddit_name} to: {channel_id}'
                )
                async for post in subreddit.hot(limit=30):
                    link = post.url
                    if not link.endswith('jpg', 'jpeg', 'png') or link in urls:
                        continue
                    urls.append(link)  # this might not work
                    # if so, use this instead:
                    # database[channel_id][subreddit_name].append(link)
                    await channel.send(link)
                    logger.info(f'Sent image: {link}')
        logger.info('Finished sending images')
        self._save_database_to_json()

        await reddit.close()
        logger.info('Closed Reddit connection')

    # Listeners ------------------------------------------------------------- #
    @commands.Cog.listener()
    async def on_ready(self):
        self._load_database_from_json()
        await self.browse_reddit.start()

    # Commands -------------------------------------------------------------- #
    @commands.command()
    async def addreddit(self, ctx, name: str):
        """Look for subreddit and add it to channel."""
        reddit = self._get_reddit_client()
        logger.info(f'Looking for subreddit: {name}')
        try:
            subreddits = [
                sub async for sub in reddit.subreddits.search_by_name(
                    name, include_nsfw=True, exact=True
                )
            ]
            logger.info(f'Found subreddits: {subreddits}')
            # I'm not really sure why I'm doing this, I can delete this later
            subreddit = subreddits[0].display_name.lower()

            key = str(ctx.channel.id)
            # add channel id to dict if it doesn't exist yet
            if key not in database.keys():
                database[key] = {}

            # add reddit to channel
            if subreddit not in database[key].keys():
                database[key][subreddit] = []
                logger.info(f'Added r/{subreddit} to channel: {key}')
                embed = e.rs[e.SUCCESSFULLY_ADDED]
                await ctx.send(embed=embed)
                self._save_database_to_json()
            else:  # channel is already added to channel
                logger.info(f'r/{subreddit} already added to channel: {key}')
                await ctx.send(embed=e.rs[e.ALREADY_ADDED])

        except NotFound:  # subreddit is not found
            logger.info(f'r/{subreddit} not found')
            await ctx.send(embed=e.rs[e.NOT_FOUND])

        await reddit.close()
        logger.info('Closed Reddit connection')

    @commands.command()
    async def delreddit(self, ctx, name: str):
        """Checks if subreddit is added the to channel and deletes it if so."""
        # prepare subreddit name
        name = name.lower()
        if name.startswith(("r/", "/r/")):
            name = name.split("r/")[-1]

        # check if channel has any subreddits
        key = str(ctx.channel.id)
        if key not in database.keys():
            await ctx.send(embed=e.rs[e.NOT_CONNECTED])
        # check if channel has not this specific subreddit
        elif name not in database[key].keys():
            await ctx.send(embed=e.rs[e.NOT_CONNECTED])
        else:  # remove subreddit from channel
            del database[key][name]
            logger.info(f'Removed r/{name} from channel: {key}')
            await ctx.send(embed=e.rs[e.SUCCESSFULLY_REMOVED])
            self._save_database_to_json()

    @commands.command()
    async def reddits(self, ctx):
        """Displays all subreddits connected to channel."""
        key = str(ctx.channel.id)
        if key not in database.keys():
            await ctx.send(embed=e.rs[e.NO_SUBREDDITS])
        elif len(database[key]) == 0:
            await ctx.send(embed=e.rs[e.NO_SUBREDDITS])
        else:
            embed = e.rs[e.SUBREDDITS].copy()
            embed.description = '\n' + '\n'.join(
                list(sorted([subreddit for subreddit in database[key].keys()]))
            )
            await ctx.send(embed=embed)

    # Errors ---------------------------------------------------------------- #
    @addreddit.error
    @delreddit.error
    async def addreddit_and_delreddit_errors(self, ctx, error):
        """Error handler when argument is not passed."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=e.rs[e.MISSING_ARGUMENT])


def setup(client) -> None:
    client.add_cog(RedditSurfer(client))
