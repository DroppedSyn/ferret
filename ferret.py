from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from utils import bcolors
from follow import Follow
import sys, time
from tweepy.utils import import_simplejson, urlencode_noplus
json = import_simplejson()
from settings import consumer_key, consumer_secret, access_token, access_token_secret


class UserStreamListener(StreamListener):
    """
    A listener handles tweets are the received on the user stream.
    """
    def on_status(self,status):
        status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')
        try:
            print self.status_wrapper.fill(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
        except:
    # Catch any unicode errors while printing to console
    # and just ignore them to avoid breaking application.
            pass


    def on_error(self, status):
        print status

    def on_timeout(self):
        sys.stderr.write(bcolors.WARNING + "Timeout, sleeping for 60 seconds...\n" + bcolors.ENDC)
        time.sleep(60)
        return

class PublicStreamListener(StreamListener):
    """
    A listener that handles public stream data
    """
    def on_data(self, raw_data):
        print raw_data
        return True

    def on_status(self,status):
        status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')
        try:
            print self.status_wrapper.fill(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
        except:
             # Catch any unicode errors while printing to console
             # and just ignore them to avoid breaking application.
             pass
    def on_error(self,status):
        print "Error!"
        print status

def main():
    # Set up the authentication!
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create a user and public stream
    u = UserStreamListener()
    userstream = Stream(auth, u)
    p = PublicStreamListener()
    publicstream = Stream(auth, p)
    # Show my followers
    f = Follow(auth)
    print f.my_followers()

    print "Streaming started..."
    try:
        userstream.userstream()
        publicstream.filter(track=["swsec"])

    except:
        print bcolors.WARNING + "Stopped streaming...." + bcolors.ENDC
        userstream.disconnect()
        publicstream.disconnect()

if __name__ == '__main__':
    main()
