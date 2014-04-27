__author__ = 'ritesh'
from tweepy import OAuthHandler, API
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import time
from dmhandlers import DmCommandHandler
import sqlite3

def main():
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = API(auth)
    conn = sqlite3.connect('stats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS STATS(dm_sinceid INTEGER)''')
    try:
        while True:
            # Add rate limit checks
            since = None
            # Might be an empty DB
            c.execute('''SELECT dm_sinceid from STATS''')
            row = c.fetchone()
            since = row[0]
            print "Since ID", since
            messages = None
            if since is not None:
                messages = api.direct_messages(since_id=since)
            else:
                messages = api.direct_messages()
            if len(messages) is not 0:
                sinceid = messages[0].id
                print "Since ID %d, updating" % sinceid
                c.execute('UPDATE STATS SET dm_sinceid=?', (sinceid, ))
                conn.commit()
                print ("Have %d messages to handle") % len(messages)
                dmcommandhandler = DmCommandHandler(auth)
                for message in messages:
                    dmcommandhandler.handle_dm_command(message)
                    time.sleep(10)
            else:
                print "Nothing to do just now. No new messages"
            print "Sleeping for a bit to stay below API limits"
            time.sleep(60)
            print "I'm awake!"
    except KeyboardInterrupt:
        print "Killed by keyboard interrupt!"
        conn.commit()
        conn.close()

if __name__ == '__main__':
    main()
