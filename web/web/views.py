from web import app
from flask import (Flask, flash, request, redirect, render_template, session,
                           url_for)
from flask.ext.sqlalchemy import SQLAlchemy

from rauth.service import OAuth1Service
from rauth.utils import parse_utf8_qsl
#from settings import TW_KEY, TW_SECRET, LIST_OF_PEOPLE, LIST_OF_NAMES
import web.models

# rauth OAuth 1.0 service wrapper
twitter = OAuth1Service(
    name='twitter',
    consumer_key=app.config['TW_KEY'],
    consumer_secret=app.config['TW_SECRET'],
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    base_url='https://api.twitter.com/1.1/')

# views
@app.route('/checkme/')
def checkme():
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter/login')
def login():
    oauth_callback = url_for('authorized', _external=True)
    params = {'oauth_callback': oauth_callback}

    r = twitter.get_raw_request_token(params=params)
    if r.status_code is not 200:
        flash('There was an issue while trying to connect to Twitter. Ping @rsinha')
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
        flash('There was an issue trying to login to twitter' + str(e))
        return redirect(url_for('index'))

    verify = sess.get('account/verify_credentials.json',
                      params={'format': 'json'}).json()
    follows = {}

    for person in app.config['LIST_OF_PEOPLE']:
        f = sess.get('friendships/show.json', params={'format':
                                                          'json', 'target_screen_name': person, 'source_screen_name':
                                                          verify['screen_name']}).json()
        follows[(app.config['LIST_OF_NAMES'][person],person)] = f['relationship']['source']['following']
    return render_template('login.html', follows=follows)

    #User.get_or_create(verify['screen_name'], verify['id'], oauth_verifier, request_token,
    #       request_token_secret)
    #check_if_follows(verify['screen_name'], params, creds)
    flash('Logged in as ' + verify['name'])
    return redirect(url_for('index'))

