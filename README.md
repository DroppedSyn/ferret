# ferret

The Cigital Tech Ferret.

To get started

1. Checkout this repository
2. Create a `settings.py` file (see `settings.py.dist` for an example)
3. Install `tweepy` either in a python virtual environment or systemwide (e.g. `pip install tweepy`)
4. Run `ferret.py`
5. Follow the bot, send it DMs

## Install CouchDB
1. Use your package manager or install CouchDB [from source](http://couchdb.apache.org/).
2. Install the couchDB client for python, e.g. `pip install couchdb`
3. Create a DB either via CouchDB's web interface (Futon) or using the client. 
4. Change the database name to the one you just created to dump all tracked tweets.

The bot is restricted to dumping tweets from a stream to a database. At this point, it doesn't do much apart from putting everything tracked into a DB, and responding to "check me out" via DM. 

TODO
====
- Add tests
- Add more docs
- Fix the stupid re-auth hack we're using to call the DMHandler
- Implement a marker for DMs that we want to handle later
