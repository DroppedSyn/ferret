from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from utils import bcolors
from follow import Follow
from textwrap import TextWrapper
from dmhandlers import DMHandler
import sys, time
from tweepy.utils import import_simplejson, urlencode_noplus

json = import_simplejson()
from settings import consumer_key, consumer_secret, access_token, access_token_secret


class UserStreamListener(StreamListener):
    """
    A listener handles tweets are the received on the user stream.
    """

    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')

    def on_status(self, status):
        try:
            print self.status_wrapper.fill(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
        except:
            pass

    def on_direct_message(self, status):
        text = status.direct_message["text"].strip().lower()
        user = status.direct_message["sender_screen_name"]
        if "check me out" in text:
            print "Yeah OK, i'll check you out"
            # This is bullshit, we can do better than re-authing here!
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            n = DMHandler(auth)
            follow_status = n.check_if_follows(screen_name=user)
            people_to_follow = []
            for k, v in follow_status.iteritems():
                if v is False:
                    people_to_follow.append(k)
            if len(people_to_follow) > 0:
                print "You need to follow", people_to_follow
            else:
                print "You're AWESOME already, ROCK ON you!"
        else:
            print "DM received, did nothing"
        return True

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

    def on_status(self, status):
        try:
            print self.status_wrapper.fill(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
        except:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass

    def on_error(self, status):
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
    try:
        print "Streaming started..."
        userstream.userstream()
        publicstream.filter(track=["swsec"])
    except:
        print bcolors.WARNING + "Stopped streaming...." + bcolors.ENDC
        userstream.disconnect()
        publicstream.disconnect()


if __name__ == '__main__':
    main()
