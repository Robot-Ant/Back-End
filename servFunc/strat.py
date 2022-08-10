from flask import Blueprint
from domestic_trade_v_alpha import strategies

blue_switch = Blueprint('strategiy switch', __name__, url_prefix='/strat')
code = strategies.switch()
strategy = strategies.stratege()

@blue_switch.route('/vola')
def selectVola():
    code.strategy_code = 0
    if code.strategy_code == 0:
        strategy.allSell()
        strategy.volatility_breakthrough()
    else:
        return -1

@blue_switch.route('/rebal')
def selectRebal():
    code.strategy_code = 1
    if code.strategy_code == 1:
        strategy.allSell()
        strategy.re_balance_portfolio()
    else:
        return -1
@blue_switch.route('/VP5')
def selectVP():
    code.strategy_code = 2
    if code.strategy_code == 2:
        strategy.allSell()
        strategy.volume_power_5min_mean()
    else:
        return -1
@blue_switch.route('/moveAve')
def selectMoveAve():
    code.strategy_code = 3
    if code.strategy_code == 3:
        strategy.allSell()
        strategy.moving_average_swing()
    else:
        return -1