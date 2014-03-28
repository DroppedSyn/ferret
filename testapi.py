from tweepy import OAuthHandler, API

from tweepy.utils import import_simplejson, urlencode_noplus
json = import_simplejson()
from settings import consumer_key, consumer_secret, access_token, access_token_secret

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = API(auth)

print "Logged in as:" + api.me().name
