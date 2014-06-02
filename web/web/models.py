from flask.ext.sqlalchemy import SQLAlchemy
from web import app
db = SQLAlchemy(app)

# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    twitter_id = db.Column(db.String(120))
    oauth_verifier= db.Column(db.String(200))
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

