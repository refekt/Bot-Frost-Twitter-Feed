import pathlib
import platform
from datetime import datetime
from os import path

from twitter import Twitter
from twitter.api import TwitterHTTPError
from twitter.oauth import OAuth
from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup

import encrypt

pltfm = platform.platform()

env_file = str(pathlib.Path.cwd().parent) + "\\vars.json"
key_path = str(pathlib.Path.cwd().parent) + "\\key.key"

if not path.exists(key_path):
    encrypt.write_key()
    key = encrypt.load_key(key_path)
    encrypt.encrypt(env_file, key)
else:
    key = encrypt.load_key(key_path)

env_vars = encrypt.decrypt_return_data(env_file, key)


def initiate_twitter_api():
    return OAuth(
        env_vars["TWITTER_TOKEN_KEY"],
        env_vars["TWITTER_TOKEN_SECRET"],
        env_vars["TWITTER_CONSUMER_KEY"],
        env_vars["TWITTER_CONSUMER_SECRET"]
    )


def start_twitter_stream():
    auth = initiate_twitter_api()
    twitter = Twitter(
        auth=auth,
        retry=True
    )

    follow = []
    husker_coaches_list = twitter.lists.members(owner_screen_name="ayy_gbr", slug="Nebraska-Football-Coaches")
    husker_media_list = twitter.lists.members(owner_screen_name="ayy_gbr", slug="Husker-Media")
    husker_lists = [husker_coaches_list, husker_media_list]
    for list in husker_lists:
        for member in list["users"]:
            follow.append(member["id_str"])
    follow_str = ",".join(follow)
    track_str = ""

    stream_args = dict(
        auth=auth,
        timeout=60,
        block=False,
        heartbeat_timeout=60
    )
    stream = TwitterStream(**stream_args)

    try:
        query_args = dict(
            follow=follow_str,
            track=track_str,
            language="en",
            retry=True
        )
        tweet_iter = stream.statuses.filter(**query_args)

        print("Waiting for a tweet...")

        for tweet in tweet_iter:

            print(tweet)

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

                tweet_str = f"Author: @{tweet['user']['screen_name']}\n" \
                            f"Link: https://twitter.com/{tweet['user']['screen_name']}/status/{tweet[id]}\n" \
                            f"Text: {tweet['text']}\n" \
                            f"Created At: {dt.strftime('%B %d, %Y at %H:%M%p')}"
                print(tweet_str)
            else:
                print("-- Some data: " + str(tweet))
    except TwitterHTTPError as e:
        print(e)
        print("Waiting 15 minutes and then restarting")
        import time
        time.sleep(15 * 60)
        print("Restarting the twitter stream")
        start_twitter_stream()


def main():
    start_twitter_stream()


if __name__ == "__main__":
    main()
