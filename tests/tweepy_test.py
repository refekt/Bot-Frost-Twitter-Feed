import json
import logging

import tweepy

from main import send_tweet_to_discord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


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


class UserMentions:
    def __init__(self, screen_name, name, _id, id_str):
        self.screen_name = screen_name
        self.name = name
        self.id = _id
        self.id_str = id_str


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
        self.source = source
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


class TwitterStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        logger.info("*~~> on_status", status)

    def on_connect(self):
        logger.info("*~~> on_connect")

    def on_data(self, raw_data):
        raw_data = json.loads(raw_data)

        try:
            raw_data["user"].get("id")
        except KeyError:
            return

        send_tweet_to_discord(
            build_tweet(
                raw_data
            )
        )

    def on_delete(self, status_id, user_id):
        logger.info("*~~> on_delete", status_id, user_id)

    def on_direct_message(self, status):
        logger.info("*~~> on_direct_message", status)

    def on_disconnect(self, notice):
        logger.info("*~~> on_disconnect", notice)

    def on_error(self, status_code):
        if status_code == 401:
            logger.info("*~~> Status Code: 401. Unable to authenticate!")
            import sys
            sys.exit()
        else:
            logger.info("*~~> on_error", status_code)

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
