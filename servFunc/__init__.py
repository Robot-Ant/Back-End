from flask import Flask
from servFunc import stockInfo

#from servFunc import strat
#from domestic_trade_v_alpha import strategies
app = Flask(__name__)
app.register_blueprint(stockInfo.blue_get)
#app.register_blueprint(strat.blue_switch)