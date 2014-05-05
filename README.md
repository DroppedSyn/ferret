# ferret

The Cigital Tech Ferret.


## Install pre-requisites
1. Install this using your package manager (for Ubuntu/Debian, you may want to install the latest version from here: http://www.postgresql.org/download/linux/ubuntu/)
2. Install `rabbitmq` and `couchdb`
3. Set up a postgres database. If you create a database called `$USER` you do not require a password to connect to it locally. To do this, run `createtb -U <your username>`. This is good enough for our purposes.


## To run the bot
1. Checkout this repository in a python virtual environment
2. Run `pip install -r requirements.txt`
2. Create a `settings.py` file (see `settings.py.dist` for an example)
4. Run `celery beat` and `celery -A tasks worker --loglevel=info`. This starts up the scheduler and the task handler. This will be replaced by a `supervisord` file at some point.
5. Follow the bot, send it DMs
