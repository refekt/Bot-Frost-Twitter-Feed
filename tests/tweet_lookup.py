import pathlib
from pprint import pprint

from twitter import Twitter
from twitter.oauth import OAuth

import encrypt

env_file = str(pathlib.Path.cwd().parent) + "\\vars.json"
key_path = str(pathlib.Path.cwd().parent) + "\\key.key"

key = encrypt.load_key(key_path)

env_vars = encrypt.decrypt_return_data(env_file, key)

auth = OAuth(env_vars["TWITTER_TOKEN_KEY"], env_vars["TWITTER_TOKEN_SECRET"], env_vars["TWITTER_CONSUMER_KEY"], env_vars["TWITTER_CONSUMER_SECRET"])

stream_args = dict(
    timeout=60,
    block=False,
    heartbeat_timeout=60
)

twitter = Twitter(
    auth=auth
)

tweet = twitter.statuses.oembed(_id=1307688583201947649)

pprint(tweet)
