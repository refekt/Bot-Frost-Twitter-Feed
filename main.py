import platform
from datetime import datetime
from os import path

import discord
from discord.ext import commands
from twitter import Twitter
from twitter.oauth import OAuth
from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup

import encrypt


class TTD(commands.Bot):

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.nebraska_twitter_list_id = 1223689242896977922
        self.timeout = 90
        self.no_block = True
        self.heartbeat_timeout = 90

    def initiate_twitter_api(self):
        return OAuth(
            env_vars["TWITTER_TOKEN_KEY"],
            env_vars["TWITTER_TOKEN_SECRET"],
            env_vars["TWITTER_CONSUMER_KEY"],
            env_vars["TWITTER_CONSUMER_SECRET"]
        )

    async def start_twitter_stream(self):

        # When using twitter stream you must authorize.
        auth = self.initiate_twitter_api()

        # These arguments are optional:
        stream_args = dict(
            timeout=self.timeout,
            block=not self.no_block,
            heartbeat_timeout=self.heartbeat_timeout
        )

        twitter = Twitter(
            auth=auth
        )

        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/api-reference/post-statuses-filter
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/basic-stream-parameters

        husker_coaches_list = twitter.lists.members(owner_screen_name="ayy_gbr", slug="Nebraska-Football-Coaches")
        # husker_players_list = twitter.lists.members(owner_screen_name="ayy_gbr", slug="Nebraska-Football-Players")
        husker_media_list = twitter.lists.members(owner_screen_name="ayy_gbr", slug="Husker-Media")
        husker_lists = [husker_coaches_list, husker_media_list]

        follow = []
        for list in husker_lists:
            for member in list['users']:
                follow.append(member["id_str"])
        follow_str = ",".join(follow)

        # track_str = "#huskers #gbr #b1g #bigten"
        query_args = dict()
        query_args["follow"] = follow_str
        # query_args["track"] = track_str
        query_args["language"] = "en"

        stream = TwitterStream(auth=auth, **stream_args)
        tweet_iter = stream.statuses.filter(**query_args)
        chan = client.get_channel(636220560010903584)

        del husker_coaches_list, husker_media_list, husker_lists, member, follow, query_args

        print("Waiting for a tweet...")

        for tweet in tweet_iter:

            if tweet is None:
                print("-- None --")
            elif tweet is Timeout:
                print("-- Timeout --")
            elif tweet is HeartbeatTimeout:
                print("-- Heartbeat Timeout --")
            elif tweet is Hangup:
                print("-- Hangup --")
            elif tweet.get('text'):

                tweet_author = tweet["user"]["screen_name"]
                if tweet_author not in follow_str:
                    print(f"Skipping tweet from [ @{tweet_author} ]")
                    continue

                print("Sending a tweet!")

                try:
                    dt = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
                except KeyError:
                    dt = datetime.now()

                tweet_embed = discord.Embed(
                    title=f"Bot Frost Twitter Feed #GBR",
                    color=0xD00000,
                    timestamp=dt
                )
                tweet_embed.add_field(
                    name="Tweet",
                    value=tweet["text"],
                    inline=False
                )
                tweet_embed.add_field(
                    name="Link",
                    value=f"https://twitter.com/{tweet['user']['screen_name']}/status/{tweet['id']}",
                    inline=False
                )
                tweet_embed.set_author(
                    name=f"{tweet['user']['name']} (@{tweet['user']['screen_name']})",
                    icon_url=tweet['user']['profile_image_url']
                )
                tweet_embed.set_footer(
                    text=f"{dt.strftime('%B %d, %Y at %H:%M%p')} | 🎈 = General 🌽 = Scott's Tots",
                    icon_url="https://i.imgur.com/Ah3x5NA.png"
                )

                tweet_message = await chan.send(embed=tweet_embed)
                reactions = ("🎈", "🌽")
                for reaction in reactions:
                    await tweet_message.add_reaction(reaction)

            else:
                print("-- Some data: " + str(tweet))

    async def on_ready(self):
        print("Starting the Twitter stream.")

        await self.start_twitter_stream()

    @commands.command(aliases=["q"])
    async def quit(ctx):
        print("Quiting...")
        await client.logout()


pltfm = platform.platform()
env_file = None
key_path = None

if "Windows" in pltfm:
    env_file = "vars.json"
    key_path = "key.key"
elif "Linux" in pltfm:
    env_file = "/home/botfrosttwitter/bot/vars.json"
    key_path = "/home/botfrosttwitter/bot/key.key"

if not path.exists("key.key"):
    encrypt.write_key()
    key = encrypt.load_key(key_path)
    encrypt.encrypt(env_file, key)
else:
    key = encrypt.load_key(key_path)

env_vars = encrypt.decrypt_return_data(env_file, key)

# from pprint import pprint
# pprint(env_vars)

del key, env_file, key_path

client = TTD(
    command_prefix="+",
)

client.run(env_vars["DISCORD_TOKEN"])
