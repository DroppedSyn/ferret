"""
Simple webapp using rauth to check for followers!
"""

from flask import (Flask, flash, request, redirect, render_template, session,
                   url_for)
from flask.ext.sqlalchemy import SQLAlchemy

from flask_bootstrap import Bootstrap

from rauth.service import OAuth1Service
from rauth.utils import parse_utf8_qsl
import settings

# Flask config
SQLALCHEMY_DATABASE_URI = 'sqlite:///twitter.db'
SECRET_KEY = 'dev key lol pls dont hack'
DEBUG = True
TW_KEY = settings.CONSUMER_KEY
TW_SECRET = settings.CONSUMER_SECRET

# Flask setup
app = Flask(__name__)
app.config.from_object(__name__)
Bootstrap(app)
db = SQLAlchemy(app)

# rauth OAuth 1.0 service wrapper
twitter = OAuth1Service(
    name='twitter',
    consumer_key=TW_KEY,
    consumer_secret=TW_SECRET,
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    base_url='https://api.twitter.com/1.1/')


# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    twitter_id = db.Column(db.String(120))
    oauth_verifier = db.Column(db.String(200))
    request_token = db.Column(db.String(200))
    request_token_secret = db.Column(db.String(200))

    def __init__(self, username, twitter_id, oauth_verifier, request_token,
                 request_token_secret):
        self.username = username
        self.twitter_id = twitter_id
        self.oauth_verifier = oauth_verifier
        self.request_token = request_token
        self.request_token_secret = request_token_secret

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def get_or_create(username, twitter_id, oauth_verifier, request_token,
                      request_token_secret):
        # TODO: Test if user exists and has old tokens
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username, twitter_id, oauth_verifier, request_token,
                        request_token_secret)
            db.session.add(user)
            db.session.commit()
        return user

    @staticmethod
    def get_user(username):
        user = User.query.filter_by(username).first()
        return user


# views
@app.route('/')
def index():
    return render_template('login.html')


@app.route('/twitter/login')
def login():
    oauth_callback = url_for('authorized', _external=True)
    params = {'oauth_callback': oauth_callback}

    r = twitter.get_raw_request_token(params=params)
    if r.status_code is not 200:
        flash('Much twitter fail! Try again!')
        return redirect(url_for('index'))
    data = parse_utf8_qsl(r.content)
    session['twitter_oauth'] = (data['oauth_token'],
                                data['oauth_token_secret'])
    return redirect(twitter.get_authorize_url(data['oauth_token'], **params))


@app.route('/twitter/authorized')
def authorized():
    request_token, request_token_secret = session.pop('twitter_oauth')

    # check to make sure the user authorized the request
    if not 'oauth_token' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))
    #oauth_verifier = None
    #params = None
    #creds = None
    try:
        creds = {'request_token': request_token,
                 'request_token_secret': request_token_secret}
        params = {'oauth_verifier': request.args['oauth_verifier']}
        #oauth_verifier = params['oauth_verifier']
        sess = twitter.get_auth_session(params=params, **creds)
    except Exception, e:
        flash('There was a problem logging into Twitter: ' + str(e))
        return redirect(url_for('index'))

    verify = sess.get('account/verify_credentials.json',
                      params={'format': 'json'}).json()
    follows = {}

    for person in settings.LIST_OF_PEOPLE:
        f = sess.get('friendships/show.json', params={'format':
                                                          'json', 'target_screen_name': person, 'source_screen_name':
                                                          verify['screen_name']}).json()
        follows[(settings.LIST_OF_NAMES[person],person)] = f['relationship']['source']['following']
    return render_template('login.html', follows=follows)

    #User.get_or_create(verify['screen_name'], verify['id'], oauth_verifier, request_token,
    #       request_token_secret)
    #check_if_follows(verify['screen_name'], params, creds)
    flash('Logged in as ' + verify['name'])
    return redirect(url_for('index'))

#def check_if_follows(user_id, params, creds):
#   session = twitter.get_auth_session(params=params, **creds)
#      print f



if __name__ == '__main__':
    db.create_all()
    app.run()
