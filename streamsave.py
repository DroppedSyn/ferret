from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Cursor
from tweepy import Stream, error
import time
import psycopg2
import psycopg2.extras
import settings
import json
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

a = 0  #Need this for api access (re-tweet)


def check_if_tweet_from_follower(tweet):
    """
    This function checks if a given tweet is from a user who is following us (THIS MIGHT HAVE TO BE REPLACED WITH THE VERIFIED TABLE IN THE FUTURE)
    """
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    userid = str(tweet["user"]["id"])
    cur.execute("SELECT screen_name from FOLLOWER JOIN verified ON follower.screen_name=verified.twitter_handle "
                "WHERE id = %s", (userid,))

    #cur.execute("SELECT twitter_handle FROM VERIFIED WHERE id = %s",
    #            [str(tweet["user"]["id"])])
    result = cur.fetchone()
    conn.close()
    if result is not None:
        return True
    return False


def check_if_follower_has_tweeted_before(tweet):
    """
    This function checks if the user has tweeted before, by checking if the user is within the hastweeted table.
    :return True if they've tweeted before, false if they haven't
    """
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM HASTWEETED WHERE user_id = %s", [str(tweet["user"]["id"])]);
    results = cur.fetchone()
    conn.close()
    if results is not None:
        return True
    return False


def screen_and_handle_user(tweet):
    """
    This function checks if the user is a follower and if they have not tweeted before. If this is the case, it will re-tweet the users tweet, add them to the 
    hastweeted table, and re-tweet their tweet.
    """
    if check_if_tweet_from_follower(tweet) is True and check_if_follower_has_tweeted_before(tweet) is False:
        try:
            a.retweet(tweet["id"])
        except error.TweepError as te:
            print"A Tweepy error occurred, failed to retweet! ", te
            return
        conn = psycopg2.connect(settings.PGDBNAME)
        cur = conn.cursor()
        #print"User is a follower - Retweeted, Adding user."
        try:
            cur.execute("INSERT INTO HASTWEETED(user_id) VALUES (%s)", [str(tweet["user"]["id"])])
            conn.commit()
        except Exception as e:
            conn.rollback()
            reset_cursor(conn)
            print "[!-]Unable to save", e
            return
        if cur.lastrowid == None:
            print "[!-]Unable to save"
            conn.close()
        else:
            pass
            #print"[!]user is not a follower. or user has already tweeted.."


def create_tweet_dict(tweet):
    """
    this function creates a dict of the tweets, which can then be persisted.
    """
    tweetDict = []
    for i in ["text", "favorited", "retweeted", "text"]:
        tweetDict.append([i, unicode(tweet[i])])

    ts = '%014d' % long(time.mktime(time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')))
    tweetDict.append(['created_at', ts])

    if len(tweet["entities"]["urls"]):
        tweetDict.append(["urls", unicode(tweet["entities"]["urls"])])

    if len(tweet["entities"]["hashtags"]):
        tweetDict.append(["hashtags", unicode(tweet["entities"]["hashtags"])])

    if len(tweet["entities"]["user_mentions"]):
        tweetDict.append(["has_user_mentions", unicode(tweet["entities"]["user_mentions"])])
        tweetDict.append(["entities", unicode(json.dumps(tweet["entities"]))])
    if len(tweet["user"]):
        tweetDict.append(["user_id", unicode(tweet["user"]["id"])])
        tweetDict.append(["verified", unicode(tweet["user"]["verified"])])
        tweetDict.append(["follower_count", unicode(tweet["user"]["followers_count"])])
        tweetDict.append(["tweet_count", unicode(tweet["user"]["statuses_count"])])
        tweetDict.append(["description", unicode(tweet["user"]["description"])])
        tweetDict.append(["friends_count", unicode(tweet["user"]["friends_count"])])
        tweetDict.append(["location", unicode(tweet["user"]["location"])])
        tweetDict.append(["following", unicode(tweet["user"]["following"])])
        tweetDict.append(["name", unicode(tweet["user"]["name"])])
        tweetDict.append(["screen_name", unicode(tweet["user"]["screen_name"])])
        uts = '%014d' % long(time.mktime(time.strptime(tweet["user"]['created_at'], '%a %b %d %H:%M:%S +0000 %Y')))
        tweetDict.append(["user_created_at", uts])
    print tweetDict
    return tweetDict


def persist_tweet_dict(data):
    """
    This function persists a dict of tweets.
    """
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    convertedTweets = create_tweet_dict(data)
    try:
        cur.execute("INSERT INTO tweet(id, doc) VALUES(%s, hstore(%s))",
                    ("%d-%d" % (data["id"], time.time()), convertedTweets))
        conn.commit()
    #print"[!+] persisted"
    #conn.close()
    except Exception as e:
        conn.rollback()
        reset_cursor(conn)
        print "[!-]Unable to save", e
        return
    if cur.lastrowid == None:
        print "[!-]Unable to save"
    #print checkIsTweetFromFollower(data)
    conn.close()
    screen_and_handle_user(data)


def reset_cursor(conn):
    return conn.cursor()


class StdOutListener(StreamListener):
    """
    A listener handles tweets are the received from the stream.
    """

    def on_data(self, data):
        #print"Status Ding!"
        tweets = json.loads(data)
        persist_tweet_dict(tweets)

    def on_error(self, error):
        print "Error in Streaming API", error
        return True


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    a = API(auth)
    l = StdOutListener()
    stream = Stream(auth, l, timeout=None)
    stream.filter(track=settings.TRACKING_TERMS)

