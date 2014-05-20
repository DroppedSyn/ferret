from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Cursor
from dmhandlers import DmCommandHandler
from tweepy.utils import import_simplejson
from tweepy import Stream
import psycopg2
import settings 
json = import_simplejson()
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
This is a basic listener that just prints received tweets to stdout.

    """
    def on_status(self, status):
        conn = psycopg2.connect(settings.PGDBNAME)
        cur = conn.cursor()
        print status.text
        #cur.execute("""INSERT INTO tweets(tweet) VALUES(status=> "%s", author
        #        =>"%s""", (status.text, status.author.screen_name,))
    def on_error(self, error):
        print error
        

if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    a = API(auth)
    l = StdOutListener()
    stream = Stream(auth, l)
    stream.filter(track=['basketball'])
