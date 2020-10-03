import json
import pathlib

from twitter import OAuth

import encrypt
import tweepy

env_file = str(pathlib.Path.cwd().parent) + "\\vars.json"
key_path = str(pathlib.Path.cwd().parent) + "\\key.key"

key = encrypt.load_key(key_path)

env_vars = encrypt.decrypt_return_data(env_file, key)

auth = OAuth(env_vars["TWITTER_TOKEN_KEY"], env_vars["TWITTER_TOKEN_SECRET"], env_vars["TWITTER_CONSUMER_KEY"],
             env_vars["TWITTER_CONSUMER_SECRET"])


class StreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        print(f"{tweet.user.name}:{tweet.text}")
        print(f"https://twitter.com/user/status/{tweet.id}")

    def on_error(self, status_code):
        if status_code == 420:
            return False
        print("Error Detected")


api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

tweetStreamListener = StreamListener()
tweetStream = tweepy.Stream(auth=api.auth, listener=tweetStreamListener)
tweetStream.filter(follow=['457066083'])