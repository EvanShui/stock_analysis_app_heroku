#flask app
from flask import Flask

#instantiate the flask append
app = Flask(__name__)

import stock_analysis_app.routes
