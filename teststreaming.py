from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Cursor
from dmhandlers import DmCommandHandler
from tweepy.utils import import_simplejson
from tweepy import Stream
import time
import psycopg2
import psycopg2.extras
import settings 
#json = import_simplejson()
import json
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


def checkFollowing(userIDs, tweetID):
    for id in userIDs:
	if (tweetID = id):
	return true    
    return false

def createTweetDict(tweet):
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

def persistTweetDict(tweets):
    conn = psycopg2.connect(settings.PGDBNAME)
    cur = conn.cursor()
    convertedTweets = createTweetDict(tweets)
    try:
	cur.execute("INSERT INTO tweet(id, doc) VALUES(%s, hstore(%s))", ("%d-%d" % (tweets["id"], time.time()), convertedTweets))
	conn.commit()
	print"[!+] persisted"
    except Exception as e:
	    conn.rollback()
	    reset_cursor(conn)
	    print "[!-]Unable to save", e
	    return
    if cur.lastrowid == None:
	    print "[!-]Unable to save"

def reset_cursor(c):
    cursor=c.cursor()


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
	print"Status Ding!"
        #conn = psycopg2.connect(settings.PGDBNAME)
        #cur = conn.cursor()
	tweets = json.loads(data)
	#createTweetDict(tweet)
	persistTweetDict(tweets)
        #print status.user.id
        #cur.execute("""INSERT INTO tweets(tweet) VALUES(status=> "%s", author
        #        =>"%s""", (status.text, status.author.screen_name,))
    def on_error(self, error):
        print error

#    def on_data(self, data):
#	print data        

if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    a = API(auth)
    l = StdOutListener()
    stream = Stream(auth, l, timeout=None)
    stream.filter(track=['SuarezDentalTips'])
