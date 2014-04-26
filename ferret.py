from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API
from tweepy import Stream
from utils import bcolors
from follow import Follow
from textwrap import TextWrapper
import sys
import time
from tweepy.utils import import_simplejson, urlencode_noplus
from couchdbkit import *
import commands

json = import_simplejson()
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
# Terms we want to track in the public stream
from settings import TRACKING_TERMS, DBNAME


class UserStreamListener(StreamListener):
    """
    A listener handles tweets are the received on the user stream.
    """
    def __init__(self):
        self.server = Server()

    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')

    def on_status(self, status):
        try:
            print self.status_wrapper.fill(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
        except:
            pass
        return

    def on_direct_message(self, status):
        """
        Receive direct messages, chuck them in a DB
        Tag them for action required, if applicable.
        """
        text = status.direct_message["text"].strip().lower()
        print text
        # Check if the text contains any commands
        cigibot_action = -1
        try:
            cigibot_action = commands.COMMANDS[text]
        except KeyError:
            pass
        # If we need to take action, save the message, else ignore it.
        if cigibot_action is not -1:
            status.direct_message["cigibot_action"] = cigibot_action
        # Save
        db = self.server.get_or_create_db("direct_messages")
        print status["text"]
        db.save_doc(status)
        return True

    def on_error(self, status):
        print "Error!", status
        return

    def on_timeout(self):
        sys.stderr.write(bcolors.WARNING + "Timeout, sleeping for 60 seconds...\n" + bcolors.ENDC)
        time.sleep(60)
        return


class PublicStreamListener(StreamListener):
    """
    A listener that handles public stream data
    """
    def __init__(self, api=None):
        super(StreamListener, self).__init__()
        self.api = api or API()
        self.server = Server()
        self.db = self.server.get_or_create_db(DBNAME)

    def on_data(self, raw_data):
        data = json.loads(raw_data)
        self.db.save_doc(data)
        return

    def on_error(self, status):
        print status
        return

    def on_timeout(self):
        sys.stderr.write(bcolors.WARNING+"Timed out!, Sleeping for 60s"+bcolors.ENDC)
        time.sleep(60)
        return

def main():
    # Set up the authentication!
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = API(auth)
    ratelimit = api.rate_limit_status()
    print "We have" + ratelimit["remaining_hits"]+ "hits left"
    # Create a user and public stream
    u = UserStreamListener()
    userstream = Stream(auth, u)

    p = PublicStreamListener()
    publicstream = Stream(auth, p)

    # Show my followers
    f = Follow(auth)
    print f.my_followers()

    print "Streaming started..."
    publicstream.filter(track=TRACKING_TERMS)
    #except:
    #    print bcolors.WARNING + "Stopped streaming...." + bcolors.ENDC
     #   userstream.disconnect()
     #   publicstream.disconnect()


if __name__ == '__main__':
    main()
