from celery import Celery
import binascii
import os
import tweepy
import settings
import utils
import dmhandlers
import psycopg2
from tweepy import TweepError
from email.mime.text import MIMEText
from settings import EMAIL_ADDRESS, SMTP_SERVER, DEBUG
import smtplib
from psycopg2 import ProgrammingError

app = Celery('ferret_tasks')
app.config_from_object('celeryconfig')
conn = psycopg2.connect(settings.PGDBNAME)
conn.autocommit = True


def _get_api():
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api


def _get_cursor():
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1")
    except ProgrammingError as p:
        print "Programming error", p
        cur.rollback()
    return cur


def _get_sinceid(name):
    cur = _get_cursor()
    cur.execute("SELECT value FROM SINCEID WHERE name = %s", (name,))
    r = cur.fetchone()
    conn.commit()
    if r is not None:
        return r[0]
    else:
        return 0


def _set_sinceid(name, sinceid):
    cur = conn.cursor()
    cur.execute("UPDATE SINCEID SET value = %s WHERE name = %s",
                (sinceid, name,))
    conn.commit()


def _get_code():
    cur = _get_cursor()
    cur.execute("SELECT code FROM verified")
    r = cur.fetchall()
    code = binascii.b2a_hex(os.urandom(4))
    # There has got to be a better way to do this!
    while (code,) in r:
        code = binascii.b2a_hex(os.urandom(4))
    return code


@app.task
def refresh_followers():
    api = _get_api()
    cur = _get_cursor()
    hits = utils.get_hits_left(api.rate_limit_status(), 'followers', '/followers/list')
    print "refresh_followers: We have %s hits left" % (hits,)
    if hits < 1:
        return
    try:
        for user in tweepy.Cursor(api.followers, screen_name="CigiBot").items():
            cur.execute("""INSERT INTO FOLLOWER (id,screen_name) SELECT %s, %s WHERE
                NOT EXISTS (SELECT id FROM FOLLOWER WHERE id = %s)""", (str(user.id), user.screen_name, str(user.id)))
            conn.commit()
    except TweepError as err:
        raise refresh_followers.retry(countdown=60 * 3, exc=err)


@app.task()
def auto_follow():
    api = _get_api()
    hits = utils.get_hits_left(api.rate_limit_status(), 'followers', '/followers/list')
    print "auto_follow: We have %s hits left" % (hits,)
    if hits < 1:
        return
    for follower in tweepy.Cursor(api.followers).items():
        follower.follow()


@app.task
def check_if_follows():
    api = _get_api()
    hits = utils.get_hits_left(api.rate_limit_status(), 'followers', '/followers/list')
    print hits
    if hits < 1:
        return
    for user in tweepy.Cursor(api.followers, screen_name="CigiBot").items():
        print user.screen_name


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
        return
    if len(messages) is not 0:
        dmhandlers.DmCommandHandler(messages)
        _set_sinceid('dm_sinceid', messages[0].id)
        destroy_dms.delay(messages)
    else:
        if DEBUG:
            print "No new DMs yet! Hits left %s" % (hits,)


@app.task
def destroy_dms(messages):
    api = _get_api()
    for message in messages:
        api.destroy_direct_message(message.id)


@app.task
def send_dm(to, message):
    # TODO: Handle fails by saving to DB ?
    api = _get_api()
    try:
        api.send_direct_message(screen_name=to, text=message)
    except TweepError as err:
        print "Failed to send %s to %s" % (message, to)
        print err
        # TODO: Exponential back-off, for now retry after 180 seconds
        #raise send_dm.retry(countdown=60*3, exc=err)


@app.task
def update_status(message):
    if DEBUG:
        print "Running in DEBUG! Status update: %s" % (message,)
        return
    try:
        # status = "@%s %s" % (to, message[:140])
        #print status
        api = _get_api()
        api.update_status(message)
    except TweepError as err:
        print "Failed to update status, retrying in 180 seconds", err
        # TODO: Exponential back-off, for now retry after 180 seconds
        #raise update_status.retry(countdown=60*3, exc=err)


@app.task
def link_user(email, twitter_handle):
    """
    Allow users to claim twitter IDs
    if they say I am rksinha, then the DM sender is mapped to that twitter ID
    """
    cur = _get_cursor()
    cur.execute("SELECT email FROM VERIFIED WHERE LOWER(email) = LOWER(%s) AND VERIFIED = FALSE", (email,))
    print "Trying to verify %s" % (email,)
    r = cur.fetchone()
    if r is not None:
        # random code for auth
        code = _get_code()
        cur = _get_cursor()
        cur.execute("UPDATE VERIFIED SET twitter_handle = %s, CODE = %s WHERE LOWER(email) = LOWER(%s)",
                    (twitter_handle, code, email,))
        conn.commit()
        #update_status.delay("%s I've sent you a code, check your email" % (twitter_handle,))
        msg = """Hello %s,\nEither you, or someone claiming to be you, asked to link a Twitter account. \nIf you are the
        owner of @%s, please send a direct message to @cigibot with the following code:\n\n%s""" \
              % (email, twitter_handle, code)
        send_email.delay(email, "Look inside for your cigibot code!", msg)
    else:
        print email, ":No such email_address or user has verified already!"
        return


@app.task
def check_auth_code(twitter_handle, code):
    """
    Test if twitter handle has the authcode
    :param twitter_handle: The twitter handle that sent us the code
    :param code: the code we have in DB
    :return:
    """
    print "Checking auth for %s - %s" % (twitter_handle, code,)
    cur = _get_cursor()

    cur.execute("SELECT LOWER(email) from VERIFIED WHERE code = %s AND twitter_handle = %s", (code, twitter_handle, ))
    result = cur.fetchone()
    conn.commit()
    # No results!
    if result is None:
        # Do nothing if we have a bad code
        return
    cur = _get_cursor()
    cur.execute("UPDATE VERIFIED SET verified = TRUE WHERE twitter_handle = %s", (twitter_handle,))
    conn.commit()
    update_status.delay("Congratulations @%s, and welcome to Tech Fair 2014!" % (twitter_handle,))


@app.task
def send_email(to, subject, message):
    """
    Send email using the tech ferret's gmail account
    :param to: The recipient
    :param subject: The subject of the email
    :param message: The message
    :return:
    """
    #if DEBUG:
    #    print ("DEBUG: Email to %s,\nSubject:%s\nMessage:%s") % (to, subject, message)
    #    return
    # TODO: Add checks to stop spamming people limit 3?!
    cur = _get_cursor()
    cur.execute("SELECT emails_sent FROM verified WHERE email = %s", (to,))
    r = cur.fetchone()
    if r is not None:
        if r[0] >= 3:
            print ("ERR: User %s has been spammed enough, not going to email them.") % (to,)
            return
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = "%s@cigital.com" % (to,)
    session = smtplib.SMTP(SMTP_SERVER, '25')
    #TODO: Retry if we fail?
    session.ehlo()
    session.sendmail(EMAIL_ADDRESS, msg['To'], msg.as_string())
    cur = _get_cursor()
    cur.execute("UPDATE verified SET emails_sent = emails_sent + 1 WHERE email = %s", (to,))
    conn.commit()


if __name__ == '__main__':
    print "Testing!"
