# ferret

The Cigital Tech Ferret.


## Install CouchDB
1. Use your package manager or install CouchDB [from source](http://couchdb.apache.org/).
2. Install the couchDB client for python, e.g. `pip install couchdb`
3. Create a DB either via CouchDB's web interface (Futon) or using the client. You want to create a `direct_messages` database, as well as a database to store
tracked terms. The name is defined in `settings.py`
4. Change the database names to the ones you just created to dump all tracked tweets and direct messages.

## To run the bot
1. Checkout this repository
2. Create a `settings.py` file (see `settings.py.dist` for an example)
3. Install `tweepy` either in a python virtual environment or systemwide (e.g. `pip install tweepy`)
4. Run `ferret.py`
5. Follow the bot, send it DMs



TODO
====
- Add tests
- Add more docs
- Fix the stupid re-auth hack we're using to call the DMHandler
