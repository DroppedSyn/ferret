from celery import Celery
import binascii, os
import tweepy
import settings
import utils
import dmhandlers
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
    r = cur.fetchone()
    if r is not None:
        return r[0]
    else:
        return 0


def _set_sinceid(name, sinceid):
    cur = conn.cursor()
    cur.execute("UPDATE SINCEID SET value = %s WHERE name = %s",
                (sinceid, name,))
    conn.commit()


@app.task
def refresh_followers():
    api = _get_api()
    cur = conn.cursor()
    try:
        for user in tweepy.Cursor(api.followers, screen_name="CigiBot").items():
            # print"[i]Inserting ---------"
            # print user.id
            #print user.screen_name
            cur.execute("""INSERT INTO FOLLOWER (id,screen_name) SELECT %s, %s WHERE
                NOT EXISTS (SELECT id FROM FOLLOWER WHERE id = %s)""", (str(user.id), user.screen_name, str(user.id)))
    except TweepError as err:
        raise refresh_followers.delay(countdown=60*3, exc=err)
    conn.commit()


@app.task
def check_if_follows():
    api = _get_api()
    for user in tweepy.Cursor(api.followers, screen_name="CigiBot").items():
        print user.screen_name



@app.task
def fetchdms():
    api = _get_api()
    hits = utils.get_hits_left(api.rate_limit_status(), 'direct_messages',
                               '/direct_messages')
    if hits < 1:
        return
    #messages = None
    sinceid = _get_sinceid('dm_sinceid')
    try:
        messages = api.direct_messages(since_id=sinceid)
    except TweepError as err:
        print "Failed to fetch DMs", err
        # Retry in four minutes if we fail
        raise fetchdms.retry(countdown=60*4, exc=err)
    if len(messages) is not 0:
        dmhandlers.DmCommandHandler(messages)
        _set_sinceid('dm_sinceid', messages[0].id)
    else:
        print "No new DMs yet!"
    return True


@app.task
def send_dm(to, message):
    # TODO: Handle fails by saving to DB ?
    api = _get_api()
    try:
        api.send_direct_message(screen_name=to, text=message)
    except TweepError as err:
        print "Failed to send %s to %s" % (message, to)
        #TODO: Exponential back-off, for now retry after 180 seconds
        raise send_dm.retry(countdown=60*3, exc=err)


@app.task
def update_status(message, to=None):
    try:
        status = "@%s %s" % (to, message[:140])
        print status
        api = _get_api()
        api.update_status(status)
    except TweepError as err:
        print "Failed to update status, retrying in 180 seconds"
        #TODO: Exponential back-off, for now retry after 180 seconds
        raise update_status.retry(countdown=60*3, exc=err)

@app.task
def link_user(email, twitter_handle):
    """
    Allow users to claim twitter IDs
    if they say I am rksinha, then the DM sender is mapped to that twitter ID
    """
    cur = conn.cursor()
    cur.execute("SELECT email FROM VERIFIED WHERE email = %s", (email,))
    r = cur.fetchone()
    if r is not None:
        # random code for auth
        code = binascii.b2a_hex(os.urandom(4))
        # we might have dupe codes!! Random number generators are not to be trusted.
        cur.execute("UPDATE VERIFIED SET twitter_handle = %s, CODE = %s WHERE email = %s",
                    (twitter_handle, code, email,))
        conn.commit()
        send_dm.delay(twitter_handle, "I've sent you a code to claim your Twitter handle, "
                                            "check your Cigital email")
        msg = """Hello %s,\n\nEither you, or someone claiming to be you asked to verify the twitter handle %s. If you
        are the owner of @%s, please send a direct message to the Cigital Tech ferret bot with the following code:\n\n%s""" \
              % (email, twitter_handle, twitter_handle, code)
        send_email.delay(email + "@cigital.com", "Your verification code", msg)
    else:
        send_dm.delay(twitter_handle, "That looks like an invalid code. Try again?")
        pass


@app.task
def check_auth_code(twitter_handle, code):
    """
    Test if twitter handle has the authcode
    :param twitter_handle: The twitter handle that sent us the code
    :param code: the code we have in DB
    :return:
    """
    print "Checking auth for %s - %s" % (twitter_handle, code)
    cur = conn.cursor()
    cur.execute("SELECT email, twitter_handle from VERIFIED WHERE code = %s", (code,))
    result = cur.fetchone()
    if result is None:
        send_dm.delay(twitter_handle, "I do not understand this code :( ")
        return
    cur.execute("UPDATE VERIFIED SET verified = TRUE WHERE twitter_handle = %s", (twitter_handle,))
    conn.commit()
    send_dm.delay(twitter_handle, "Congratulations, you are now a verified user. Email: %s" % (result[0]))


@app.task
def send_email(to, subject, message):
    """
    Send email using the tech ferret's gmail account
    :param to: The recipient
    :param subject: The subject of the email
    :param message: The message
    :return:
    """
    #TODO: Add checks to stop spamming people!
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    session = smtplib.SMTP('smtp.gmail.com', '587')
    #TODO: Retry if we fail
    session.ehlo()
    session.starttls()
    session.login(EMAIL_ADDRESS, EMAIL_PW)
    session.sendmail(EMAIL_ADDRESS, to, msg.as_string())

if __name__ == '__main__':
    print "Testing!"
