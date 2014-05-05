from celery import Celery
from time import sleep
import random
import tweepy
import settings
import utils
from dmhandlers import DmCommandHandler

app = Celery('ferret_tasks')
app.config_from_object('celeryconfig')

def _get_api():
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api

@app.task
def fetchdms():
    api = _get_api()
    a = utils.PrettyPrint.ratelimit(api.rate_limit_status(), 'direct_messages', 
            '/direct_messages')
    messages = None
    if a['remaining'] >=1:
        messages = api.direct_messages(since_id=0)
    if messages is not None:
        dmcommandhandler = DmCommandHandler(messages)

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
            print "Failed for %s due to %s" % (screen_name, err['message'])
            return
    msg = u''
    for k, v in out.iteritems():
        if v is False:
            msg = msg + k + " "
    update_status.delay(msg, to=screen_name)

@app.task
def send_dm(message):
    pass

@app.task
def update_status(message, to=None):
    print "Updated status lol.Very API much WOW"

@app.task
def reply_to_status(message):
    pass
