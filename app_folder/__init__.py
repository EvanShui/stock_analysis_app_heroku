#flask app
from flask import Flask

#instantiate the flask append
app = Flask(__name__)

import app_folder.routes
