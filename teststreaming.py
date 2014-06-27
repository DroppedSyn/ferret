from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Cursor
from dmhandlers import DmCommandHandler
from tweepy.utils import import_simplejson
from tweepy import Stream, error
import time
import psycopg2
import psycopg2.extras
import settings
import json
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

a = 0     #Need this for api access (re-tweet)

def checkIsTweetFromFollower(tweet):
    """
    This function checks if a given tweet is from a user who is following us (THIS MIGHT HAVE TO BE REPLACED WITH THE VERIFIED TABLE IN THE FUTURE)
    """
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM FOLLOWER WHERE id = %s", [str(tweet["user"]["id"])]) #Magic! ('One, two, three, convert this id!')
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
	return True
    return False

def checkIfFollowerHasTweetedBefore(tweet):
    """
    This function checks if the user has tweeted before, by checking if the user is within the hastweeted table.
    """
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM HASTWEETED WHERE user_id = %s", [str(tweet["user"]["id"])]);
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
	return True
    return False

def screenAndHandleUser(tweet):
    """
    This function checks if the user is a follower and if they have not tweeted before. If this is the case, it will re-tweet the users tweet, add them to the 
    hastweeted table, and re-tweet their tweet.  if checkIsTweetFromFollower(tweet) == True and checkIfFollowerHasTweetedBefore(tweet) == False: #If the user is a follower AND they have not tweeted yet.
    """
    try:
        a.retweet(tweet["id"]) #Retweet the tweet!
    except error.TweepError as te:
        print"A tweepy error occurred: ", te
    conn=psycopg2.connect(settings.PGDBNAME)
    cur=conn.cursor()
    #print"User is a follower - User has not tweeted. Retweeting, Adding user."
    try:
        cur.execute("INSERT INTO HASTWEETED(user_id) VALUES (%s)", [str(tweet["user"]["id"])]);
        conn.commit()
        #print"[!+] persisted - user has been added to has tweeted."
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


def createTweetDict(tweet):
    """
    this function creates a dict of the tweets, which can then be persisted.
    """
    tweetDict = []
    for i in ["text", "favorited", "retweeted", "text"]:
	tweetDict.append([i, unicode(tweet[i])])

    ts = '%014d' % long(time.mktime( time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y') ))
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
	tweetDict.append(["verified",unicode(tweet["user"]["verified"])])
	tweetDict.append(["follower_count",unicode(tweet["user"]["followers_count"])])
	tweetDict.append(["tweet_count",unicode(tweet["user"]["statuses_count"])])
	tweetDict.append(["description",unicode(tweet["user"]["description"])])
	tweetDict.append(["friends_count", unicode(tweet["user"]["friends_count"])])
	tweetDict.append(["location",unicode(tweet["user"]["location"])])
	tweetDict.append(["following",unicode(tweet["user"]["following"])])
	tweetDict.append(["name",unicode(tweet["user"]["name"])])
	tweetDict.append(["screen_name",unicode(tweet["user"]["screen_name"])])
	uts = '%014d' % long(time.mktime(time.strptime(tweet["user"]['created_at'], '%a %b %d %H:%M:%S +0000 %Y') ))
	tweetDict.append(["user_created_at",uts])
    print tweetDict
    return tweetDict

def persistTweetDict(data):
    """
    This function persists a dict of tweets.
    """
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    convertedTweets = createTweetDict(data)
    try:
	cur.execute("INSERT INTO tweet(id, doc) VALUES(%s, hstore(%s))", ("%d-%d" % (data["id"], time.time()), convertedTweets))
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
    screenAndHandleUser(data)

def reset_cursor(c):
    cursor=c.cursor()


class StdOutListener(StreamListener):
    """
    A listener handles tweets are the received from the stream.
    """
    def on_data(self, data):
	#print"Status Ding!"
	tweets = json.loads(data)
	persistTweetDict(tweets)
    def on_error(self, error):
        print error


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    a = API(auth)
    l = StdOutListener()
    stream = Stream(auth, l, timeout=None)
    stream.filter(track=['testingDisregard'])
