import asyncio
from datetime import datetime
from os import path

import discord
import twitter
from discord.ext import commands

import encrypt


class TTD(commands.Bot):

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.nebraska_twitter_list_id = 1223689242896977922

    def initiate_twitter_api(self):
        return twitter.Api(
            consumer_key=env_vars["TWITTER_CONSUMER_KEY"],
            consumer_secret=env_vars["TWITTER_CONSUMER_SECRET"],
            access_token_key=env_vars["TWITTER_TOKEN_KEY"],
            access_token_secret=env_vars["TWITTER_TOKEN_SECRET"]
        )

    async def start_twitter_stream(self):

        api = self.initiate_twitter_api()

        list = api.GetListMembers(
            list_id=self.nebraska_twitter_list_id
        )

        list_ids = []
        track_terms = []

        for member in list:
            list_ids.append(member.id_str)

        track_terms.extend(
            []  # ["gbr", "huskers", "@siryacht"]
        )

        twitter_stream = api.GetStreamFilter(
            follow=list_ids,
            # track=track_terms,
            languages=["en"]
        )

        chan = client.get_channel(636220560010903584)

        while True:
            try:
                for index, tweet in enumerate(twitter_stream):
                    print(f"Tweet #{index}...")
                    # Only pass tweets from uesrs in the list
                    if not tweet['user']['id_str'] in list_ids:
                        print(f"[{index}]: Skipping tweet!")
                        # print(f"[{index}]: Skipping tweet from {tweet['user']['name']} (@{tweet['user']['screen_name']})!")
                        continue

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

                    # print(f"Sending a tweet from [@{tweet['user']['screen_name']}] [https://twitter.com/{tweet['user']['screen_name']}/status/{tweet['id']}].")
                    tweet_message = await chan.send(embed=tweet_embed)
                    reactions = ("🎈", "🌽")
                    for reaction in reactions:
                        await tweet_message.add_reaction(reaction)

                    # Attempt to avoid rate limiting
                    await asyncio.sleep(60 * 5)
            except twitter.error.TwitterError:
                delay = 60 * 60 * 2

                # Attempt to pause for awhile
                print(f"{datetime.now()}: A Twitter Timeout Error occurred. Sleeping for {delay} seconds.")
                await asyncio.sleep(delay=delay)
                print(f"{datetime.now()}: Sleeping done. Resuming.")
                continue

    async def on_ready(self):
        print("Starting the Twitter stream.")
        task = asyncio.create_task(self.start_twitter_stream())
        try:
            await task
        except asyncio.TimeoutError:
            print(f"{datetime.now()}: Twitter Stream returned Timeout Error")

        print("The Twitter stream has started.")


env_file = "vars.json"

if not path.exists("key.key"):
    encrypt.write_key()
    key = encrypt.load_key()
    encrypt.encrypt(env_file, key)
else:
    key = encrypt.load_key()

env_vars = encrypt.decrypt_return_data(env_file, key)

client = TTD(
    command_prefix="+++",
)

client.run(env_vars["DISCORD_TOKEN"])
