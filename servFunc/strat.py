from flask import Blueprint
from domestic_trade_v_alpha import strategies

blue_switch = Blueprint('strategiy switch', __name__, url_prefix='/strat')
code = strategies.switch()

@blue_switch.route('/vola')
def selectVola():
    code.strategy_code = 0
    if code.strategy_code == 0:
        strategies.stratege.volatility_breakthrough()
    else:
        return -1

@blue_switch.route('/rebal')
def selectRebal():
    code.strategy_code = 1
    if code.strategy_code == 1:
        strategies.stratege.re_balance_portfolio()
    else:
        return -1
@blue_switch.route('/VP5')
def selectVP():
    code.strategy_code = 2
    if code.strategy_code == 2:
        strategies.stratege.volume_power_5min_mean()
    else:
        return -1
@blue_switch.route('/moveAve')
def selectMoveAve():
    code.strategy_code = 3
    if code.strategy_code == 3:
        strategies.stratege.moving_average_swing()
    else:
        return -1