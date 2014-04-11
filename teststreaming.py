from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Cursor
from dmhandlers import DMHandler
from tweepy.utils import import_simplejson
from tweepy import Stream

json = import_simplejson()
from settings import consumer_key, consumer_secret, access_token, access_token_secret


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
This is a basic listener that just prints received tweets to stdout.

    """
    def on_error(self, status):
        print status

    def on_direct_message(self, status):
        print status.parse()


if __name__ == '__main__':
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    a = API(auth)
    n = DMHandler(auth)
    print n.check_if_follows(screen_name="KimKardashian")
    l = StdOutListener()
    stream = Stream(auth, l)
    stream.filter(track=['JustinReleaseLifeIsWorthLiving'])