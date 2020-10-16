import logging
import json
import platform
from datetime import datetime
from os import path

from discord import Embed, Intents
from discord.ext import commands

import encrypt
import tweepy
from tweepy import API, Stream, OAuthHandler

members_following = []
api = API()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class TwitterUser:
    def __init__(self, _id, id_str, name, screen_name, location, url, description, translator_type, protected, verified, followers_count, friends_count, listed_count, favourites_count, statuses_count, created_at, utc_offset, time_zone, geo_enabled,
                 lang, contributors_enabled, is_translator, profile_background_color, profile_background_image_url, profile_background_image_url_https, profile_background_tile, profile_link_color, profile_sidebar_border_color, profile_sidebar_fill_color,
                 profile_text_color, profile_use_background_image, profile_image_url, profile_image_url_https, default_profile, default_profile_image, following, follow_request_sent, notifications):
        self.id = _id
        self.id_str = id_str
        self.name = name
        self.screen_name = screen_name
        self.location = location
        self.url = url
        self.description = description
        self.translator_type = translator_type
        self.protected = protected
        self.verified = verified
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.listed_count = listed_count
        self.favourites_count = favourites_count
        self.statuses_count = statuses_count
        self.created_at = created_at
        self.utc_offset = utc_offset
        self.time_zone = time_zone
        self.geo_enabled = geo_enabled
        self.lang = lang
        self.contributors_enabled = contributors_enabled
        self.is_translator = is_translator
        self.profile_background_color = profile_background_color
        self.profile_background_image_url = profile_background_image_url
        self.profile_background_image_url_https = profile_background_image_url_https
        self.profile_background_tile = profile_background_tile
        self.profile_link_color = profile_link_color
        self.profile_sidebar_border_color = profile_sidebar_border_color
        self.profile_sidebar_fill_color = profile_sidebar_fill_color
        self.profile_text_color = profile_text_color
        self.profile_use_background_image = profile_use_background_image
        self.profile_image_url = profile_image_url
        self.profile_image_url_https = profile_image_url_https
        self.default_profile = default_profile
        self.default_profile_image = default_profile_image
        self.following = following
        self.follow_request_sent = follow_request_sent
        self.notifications = notifications


class TweetEntities:

    def __init__(self, hashtags, urls, user_mentions, symbols):
        self.hashtags = hashtags
        self.urls = urls
        self.user_mentions = user_mentions
        self.symbols = symbols


class Tweet:
    def __init__(self, created_at, _id, id_str, text, source, truncated, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, geo, coordinates, place, contributors, is_quote_status,
                 quote_count, reply_count, retweet_count, favorite_count, favorited, retweeted, filter_level, lang, timestamp_ms, user, entities):
        self.created_at = created_at
        self.id = _id
        self.id_str = id_str
        self.text = text
        if "iPhone" in source:
            self.source = "📱 iPhone"
        elif "Android" in source:
            self.source = "📱 Android"
        else:
            self.source = "💻 Web"
        self.truncated = truncated
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_status_id_str = in_reply_to_status_id_str
        self.in_reply_to_user_id = in_reply_to_user_id
        self.in_reply_to_user_id_str = in_reply_to_user_id_str
        self.in_reply_to_screen_name = in_reply_to_screen_name
        self.user = user
        self.geo = geo
        self.coordinates = coordinates
        self.place = place
        self.contributors = contributors
        self.is_quote_status = is_quote_status
        self.quote_count = quote_count
        self.reply_count = reply_count
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.entities = entities
        self.favorited = favorited
        self.retweeted = retweeted
        self.filter_level = filter_level
        self.lang = lang
        self.timestamp_ms = timestamp_ms
        self.url = f"https://twitter.com/{self.user.screen_name}/status/{self.id}"


class TwitterStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        logger.info(f"*~~> on_status: status")

    def on_connect(self):
        logger.info("*~~> Twitter Stream started!")

    async def on_data(self, raw_data):
        raw_data = json.loads(raw_data)

        # Limit messages
        if raw_data.get("limit"):
            return logger.info(raw_data)

        # Some random tweet would come through and break the code
        try:
            raw_data["user"].get("id")
        except KeyError:
            return

        tweet = build_tweet(raw_data)

        if tweet.user.id_str not in members_following:
            logger.info(f"*~~> Skipping tweet from @{tweet.user.screen_name}!")
            return

        logger.info(f"*~~> Sending tweet from @{tweet.user.screen_name} to Discord")

        await send_tweet_to_discord(tweet)

    def on_delete(self, status_id, user_id):
        logger.info("*~~> on_delete", status_id, user_id)

    def on_direct_message(self, status):
        logger.info("*~~> on_direct_message", status)

    def on_disconnect(self, notice):
        logger.info("*~~> on_disconnect", notice)

    def on_error(self, status_code):
        if status_code == 401:
            import sys

            logger.info("*~~> Status Code: 401. Unable to authenticate. Turning off!")
            sys.exit()
        elif status_code == 420:
            import time
            minutes_to_sleep = 5
            logger.info(f"*~~> Rate limit exceeded! Waiting {minutes_to_sleep} minutes...")
            time.sleep(60 * minutes_to_sleep)
            logger.info("*~~> Restarting the Twitter stream...")
            return True

    def on_event(self, status):
        logger.info("*~~> on_event", status)

    def on_exception(self, exception):
        logger.info("*~~> on_exception", exception)

    def on_friends(self, friends):
        logger.info("*~~> on_friends")

    def on_limit(self, track):
        logger.info("*~~> on_limit", track)

    def on_scrub_geo(self, notice):
        logger.info("*~~> on_scrub_geo", notice)

    def on_status_withheld(self, notice):
        logger.info("*~~> on_status_withheld", notice)

    def on_timeout(self):
        logger.info("*~~> on_timeout")

    def on_user_withheld(self, notice):
        logger.info("*~~> on_user_withheld", notice)

    def on_warning(self, notice):
        logger.info("*~~> on_warning")


def build_tweet(rd):
    tweet = Tweet(
        created_at=rd.get("created_at", None),
        _id=rd.get("id", None),
        id_str=rd.get("id_str", None),
        text=rd.get("text", None),
        source=rd.get("source", None),
        truncated=rd.get("truncated", None),
        in_reply_to_status_id=rd.get("in_reply_to_status_id", None),
        in_reply_to_status_id_str=rd.get("in_reply_to_status_id_str", None),
        in_reply_to_user_id=rd.get("in_reply_to_user_id", None),
        in_reply_to_user_id_str=rd.get("in_reply_to_user_id_str", None),
        in_reply_to_screen_name=rd.get("in_reply_to_screen_name", None),
        user=TwitterUser(
            _id=rd["user"].get("id", None),
            id_str=rd["user"].get("id_str", None),
            name=rd["user"].get("name", None),
            screen_name=rd["user"].get("screen_name", None),
            location=rd["user"].get("location", None),
            url=rd["user"].get("url", None),
            description=rd["user"].get("description", None),
            translator_type=rd["user"].get("translator_type", None),
            protected=rd["user"].get("protected", None),
            verified=rd["user"].get("verified", None),
            followers_count=rd["user"].get("followers_count", None),
            friends_count=rd["user"].get("friends_count", None),
            listed_count=rd["user"].get("listed_count", None),
            favourites_count=rd["user"].get("favourites_count", None),
            statuses_count=rd["user"].get("statuses_count", None),
            created_at=rd["user"].get("created_at", None),
            utc_offset=rd["user"].get("utc_offset", None),
            time_zone=rd["user"].get("time_zone", None),
            geo_enabled=rd["user"].get("geo_enabled", None),
            lang=rd["user"].get("lang", None),
            contributors_enabled=rd["user"].get("contributors_enabled", None),
            is_translator=rd["user"].get("is_translator", None),
            profile_background_color=rd["user"].get("profile_background_color", None),
            profile_background_image_url=rd["user"].get("profile_background_image_url", None),
            profile_background_image_url_https=rd["user"].get("profile_background_image_url_https", None),
            profile_background_tile=rd["user"].get("profile_background_tile", None),
            profile_link_color=rd["user"].get("profile_link_color", None),
            profile_sidebar_border_color=rd["user"].get("profile_sidebar_border_color", None),
            profile_sidebar_fill_color=rd["user"].get("profile_sidebar_fill_color", None),
            profile_text_color=rd["user"].get("profile_text_color", None),
            profile_use_background_image=rd["user"].get("profile_use_background_image", None),
            profile_image_url=rd["user"].get("profile_image_url", None),
            profile_image_url_https=rd["user"].get("profile_image_url_https", None),
            default_profile=rd["user"].get("default_profile", None),
            default_profile_image=rd["user"].get("default_profile_image", None),
            following=rd["user"].get("following", None),
            follow_request_sent=rd["user"].get("follow_request_sent", None),
            notifications=rd["user"].get("notifications", None)
        ),
        geo=rd.get("geo", None),
        coordinates=rd.get("coordinates", None),
        place=rd.get("place", None),
        contributors=rd.get("contributors", None),
        is_quote_status=rd.get("is_quote_status", None),
        quote_count=rd.get("quote_count", None),
        reply_count=rd.get("reply_count", None),
        retweet_count=rd.get("retweet_count", None),
        favorite_count=rd.get("favorite_count", None),
        entities=TweetEntities(
            hashtags=rd.get("entities", None).get("hashtags", None),
            urls=rd.get("entities", None).get("urls", None),
            user_mentions=rd.get("entities", None).get("user_mentions", None),
            symbols=rd.get("entities", None).get("symbols", None)
        ),
        favorited=rd.get("favorited", None),
        retweeted=rd.get("retweeted", None),
        filter_level=rd.get("filter_level", None),
        lang=rd.get("lang", None),
        timestamp_ms=rd.get("timestamp_ms", None)
    )

    return tweet


async def send_tweet_to_discord(tweet: Tweet):
    channel = client.get_channel(id=636220560010903584)  # Twitter
    # channel = client.get_channel(id=593984711706279937)  # Spam

    try:
        dt = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y')
    except KeyError:
        dt = datetime.now()

    general_chan_id = 440868279150444544
    recruiting_chan_id = 507520543096832001

    general_chan = client.get_channel(id=general_chan_id)
    recruiting_chan = client.get_channel(id=recruiting_chan_id)

    tweet_embed = Embed(
        # title=f"Bot Frost Twitter Feed #GBR",
        color=0xD00000,
        # timestamp=dt
    )
    tweet_embed.set_author(
        name=f"{tweet.user.name[:25]} (@{tweet.user.screen_name}) via {tweet.source}",
        icon_url=tweet.user.profile_image_url
    )
    tweet_embed.add_field(
        name="Tweet",
        value=tweet.text,
        inline=False
    )
    tweet_embed.add_field(
        name="Link",
        value=f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
        inline=False
    )
    tweet_embed.add_field(
        name="Share This Tweet!",
        value=f"React with 🎈 to send to {general_chan.mention} or 🌽 to send to {recruiting_chan.mention}",
        inline=False
    )
    tweet_embed.set_footer(
        text=f"Tweet created on {dt.strftime('%B %d, %Y at %H:%M%p')}",
        icon_url="https://i.imgur.com/Ah3x5NA.png"
    )

    tweet_message = await channel.send(embed=tweet_embed)
    reactions = ("🎈", "🌽")

    for reaction in reactions:
        await tweet_message.add_reaction(reaction)


class TTD(commands.Bot):

    async def on_ready(self):
        logger.info("*~~> Initializing the OAuth Handler")
        c_k = env_vars["TWITTER_CONSUMER_KEY"]
        c_s = env_vars["TWITTER_CONSUMER_SECRET"]
        auth = OAuthHandler(
            consumer_key=c_k,
            consumer_secret=c_s
        )

        logger.info("*~~> Setting access token")

        k = env_vars["TWITTER_TOKEN_KEY"]
        s = env_vars["TWITTER_TOKEN_SECRET"]
        auth.set_access_token(
            key=k,
            secret=s
        )

        logger.info("*~~> Initializing the API")

        global api
        api = API(
            auth_handler=auth,
            wait_on_rate_limit_notify=True,
            wait_on_rate_limit=True
        )

        logger.info("*~~> Initializing the Stream")

        listener = TwitterStreamListener()
        stream = Stream(
            auth=auth,
            listener=listener
        )

        logger.info("*~~> Creating filters")

        global members_following

        media_list = api.list_members(
            list_id=1307680291285278720
        )
        for member in media_list:
            members_following.append(member.id_str)

        coaches_list = api.list_members(
            list_id=1223689242896977922
        )
        for coach in coaches_list:
            members_following.append(coach.id_str)

        logger.info(f"*~~> Media members: {[member for member in members_following]}")

        # tracking = [
        #     "#huskers",
        #     "#gbr",
        #     "nebraska"
        # ]
        #
        # logger.info(f"*~~> Keywords: {[keyword for keyword in tracking]}")

        logger.info("*~~> Starting Twitter stream...")

        await stream.filter(
            follow=members_following
        )


pltfm = platform.platform()
env_file = None
key_path = None

logger.info("*~~> Establishing environment variables")

if "Windows" in pltfm:
    env_file = "vars.json"
    key_path = "key.key"
elif "Linux" in pltfm:
    env_file = "/home/botfrosttwitter/bot/vars.json"
    key_path = "/home/botfrosttwitter/bot/key.key"

logger.info("*~~> Loading encryption key")

if not path.exists(key_path):
    encrypt.write_key()
    key = encrypt.load_key(key_path)
    encrypt.encrypt(env_file, key)
else:
    key = encrypt.load_key(key_path)

# Debugging purposes only
# from encrypt import decrypt, encrypt
# decrypt(env_file, key)
# encrypt(env_file, key)

env_vars = encrypt.decrypt_return_data(env_file, key)

del key, env_file, key_path, pltfm

logger.info("*~~> Starting Discord bot")

client_intents = Intents()
client_intents.members = True
client_intents.messages = True
client_intents.guilds = True

client = TTD(command_prefix="+")


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 189554873778307073

    return commands.check(predicate)


@client.command(aliases=["q", ], hidden=True)
@is_owner()
async def bye(ctx):
    await ctx.send("Good bye!")
    await client.logout()


client.run(env_vars["DISCORD_TOKEN"])
