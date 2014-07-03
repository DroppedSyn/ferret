# ferret

The Cigital Tech Ferret.


## Install pre-requisites
1. Install postgresql using your package manager (for Ubuntu/Debian, you may want to install the latest version from here: http://www.postgresql.org/download/linux/ubuntu/). You will also need the developement headers to build the python postgres client. These packages are usually of the format `postgresql-server-dev-X.Y`. Install the python dev headers, too. On Wheezy this is the `python-dev` package.
2. Install `rabbitmq` using the package manager for your system.
3. Set up a postgres database. If you create a database called `$USER` (whatever your username is, e.g. ritesh) you do not require a password to connect to it locally. To do this, first run `createuser --interactive` as the postgres user. The name of the role should be `$USER`. Give this user the privilege to create new databases. When logged in as `$USER` run `createdb $USER`. Test that you can connect to the `$USER` database without a password by running `psql`. 
4. Install `virtualenv` for your platform. Create a `virtualenv` somewhere.

## To run the bot
1. Checkout this repository inside a python virtual environment. Activate the virtual environment (e.g. `source /home/ritesh/code/venvs/ferretbot/bin/activate`)
1. Run `pip install -r requirements.txt` from within the ferret directory.
1. Create a `settings.py` file (see `settings.py.dist` for an example, or borrow one from a friend.)
1. Create a `celeryconfig.py` file (see `celeryconfig.py.dist` for an example, or borrow one from a friend.)
1. Run `./runcelery.sh` in one window and `celery beat` in another. This starts up the task handler and the scheduler. 
1. Run `python streamsave.py` to save and process tweets (e.g. tweets with the #swsec hashtag)
1. See `tasks.py` for a list of tasks that the bot can run asynchronously. You can also run these tasks from an interactive Python prompt like so:

    ```python
    from tasks import send_email 
    send_email('someone_at_cigital@cigital.com', 'This One Trick Can Take 10 Years off Your Legacy Code', 'Sorry, I lied.')
    ```    
1. For the `verify_email` feature to work, the DB must be populated with email addresses. To do this, grab a copy of the corp dir in CSV (or any other plaintext format). Save this file as `corpdir.txt` in the `ferret` directory and run `./populate_emails.sh`
 
## Next steps
1. More testing required
