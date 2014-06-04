from celery import Celery
from time import sleep
import random
import tweepy
import settings
import utils
from dmhandlers import DmCommandHandler
import psycopg2
from tweepy import TweepError

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
    hits = utils.get_hits_left(api.rate_limit_status(), 'direct_messages',
            '/direct_messages')
    if hits < 1:
        return
    messages = None
    sinceid = _get_sinceid('dm_sinceid')
    try:
        messages = api.direct_messages(since_id=sinceid)
    except TweepError as err:
        print "Failed to fetch DMs", err
        return False
    if len(messages) is not 0:
        dmcommandhandler = DmCommandHandler(messages)
        _set_sinceid('dm_sinceid', messages[0].id)
    else:
        print "No new DMs yet!"
    return True

@app.task
def send_dm(to, message):
    #TODO: Handle fails by saving to DB ?
    api = _get_api()
    try:
        api.send_direct_message(screen_name=to, text=message)
    except TweepError as t:
        print "Failed to send %s to %s" % (message, to)
        print t

@app.task
def update_status(message, to, replyto=None, taskid=None):
    if taskid is not None:
        try:
            status = "@%s %s" % (to, message[:140])
            print status, taskid
            api = _get_api()
            api.update_status(status)
            #Set task as complete in DB
            cur = conn.cursor()
            cur.execute("SET TIMEZONE = 'UTC' ")
            cur.execute("""UPDATE TASKS SET COMPLETED = TRUE WHERE ID = %s""",
                    (int(taskid),))
            conn.commit()
        except TweepError as err:
            "Fail!"
    else:
        print "No task, calling update anyway"

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
def commend_user(to, message=None):
    if message is None:
        send_dm.delay(to, "Your rate of awesomeness grows exponentially!")

if __name__ == '__main__':
    print "Testing!"
    #commend_user("@rsinha")
