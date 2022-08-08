from flask import Flask
from servFunc import stockInfo

app = Flask(__name__)

app.register_blueprint(stockInfo.blue_get)