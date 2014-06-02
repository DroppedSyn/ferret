from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_envvar('FERRET_WEB')
Bootstrap(app)

import web.views
