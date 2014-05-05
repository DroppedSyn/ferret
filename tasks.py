from celery import Celery
from time import sleep
import random
import tweepy
import settings
import utils
from dmhandlers import DmCommandHandler
import psycopg2

app = Celery('ferret_tasks')
app.config_from_object('celeryconfig')
conn = psycopg2.connect(settings.PGDBNAME)

def _get_api():
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api

def _get_sinceid(name):
    cur = conn.cursor()
    cur.execute("SELECT value FROM SINCEID WHERE name = %s", (name,))
    r = cur.fetchone()[0]
    print r
    return r

def _set_sinceid(name, sinceid):
    cur = conn.cursor()
    cur.execute("UPDATE SINCEID SET value = %s WHERE name = %s", (sinceid,
        name,))
    conn.commit()

@app.task
def fetchdms():
    api = _get_api()
    a = utils.PrettyPrint.ratelimit(api.rate_limit_status(), 'direct_messages', 
            '/direct_messages')
    messages = None
    sinceid = _get_sinceid('dm_sinceid')
    try:
        messages = api.direct_messages(since_id=sinceid)
    except TweepError as err:
        print "Failed to fetch DMs: %s" %  (err['message'])
        return False
    if len(messages) is not 0:
        dmcommandhandler = DmCommandHandler(messages)
        _set_sinceid('dm_sinceid', messages[0].id)
    return True

@app.task
def check_if_follows(screen_name):
    out = {}
    api = _get_api()
    for person in settings.LIST_OF_PEOPLE:
        try:
            output = api.show_friendship(source_screen_name = screen_name,
                    target_screen_name = person)
            for item in output:
                if item.screen_name == screen_name:
                    out[person] = item.following
        except TweepError as err:
            print "Failed to check follows for %s" % (screen_name)
            return False
    msg = u''
    for k, v in out.iteritems():
        if v is False:
            msg = msg + "@"+ k + " "
    if len(msg) > 0:
        msg = " you should follow " + msg
        update_status.delay(msg, to=screen_name)
    else:
        send_dm.delay("You're following everyone already, yay!", screen_name)

@app.task
def send_dm(message, to):
    print "@"+to+message[:140]

@app.task
def update_status(message, to, replyto=None):
    print "@"+to+message[:140]

@app.task
def reply_to_status(message):
    pass

@app.task
def fetch_tracked_terms():
    pass

@app.task
def process_tracked_terms():
    pass

@app.task
def commend_user(message):
    pass

