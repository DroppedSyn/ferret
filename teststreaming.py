from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Cursor
from dmhandlers import DmCommandHandler
from tweepy.utils import import_simplejson
from tweepy import Stream

json = import_simplejson()
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
This is a basic listener that just prints received tweets to stdout.

    """
    def on_error(self, status):
        print status

    def on_direct_message(self, status):
        print status.parse()


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    a = API(auth)
    n = DmCommandHandler(auth)
    print n.check_if_follows(screen_name="KimKardashian")
    l = StdOutListener()
    stream = Stream(auth, l)
    stream.filter(track=['JustinReleaseLifeIsWorthLiving'])
