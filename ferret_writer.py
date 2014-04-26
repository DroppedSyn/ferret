__author__ = 'ritesh'
from tweepy import OAuthHandler, API
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from follow import Follow
import time
from dmhandlers import DMHandler
from couchdbkit import *

def main():
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    f = Follow(auth)
    dm = DMHandler(auth)
    # Localhost DB
    server = Server()
    dmdb = server.get_or_create_db("direct_messages")
    try:
        while True:
            # Process DM actions
            allmessages = dmdb.all_docs()
            print ("Have %d messages to handle") % len(allmessages)
            for i in allmessages:
                message = dmdb.get(i["id"])
                #Handle DM
                dm.handledm(message)
                #Delete it, lets hope it was handled.
                dmdb.delete_docs(message)
            #Follow who follow us
            print "Sleeping for a bit to stay below API limits"
            time.sleep(11)
            print "I'm awake!"
    except KeyboardInterrupt:
        print "Killed by keyboard interrupt!"
if __name__ == '__main__':
    main()
