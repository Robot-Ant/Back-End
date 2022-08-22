from flask import Flask
from servFunc import stockInfo
from servFunc import strat
from servFunc import chartdata

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.register_blueprint(stockInfo.blue_get)
app.register_blueprint(strat.blue_switch)
app.register_blueprint(chartdata.blue_chart)