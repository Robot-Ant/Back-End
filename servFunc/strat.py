from flask import Blueprint
from domestic_trade_v_alpha import strategies

blue_switch = Blueprint('strategiy switch', __name__, url_prefix='strat')

@blue_switch.route('/vola')
def selectVola():
    strategies.strategy_code = 0
    if strategies.strategy_code == 0:
        return 0
    else:
        return -1

@blue_switch.route('/rebal')
def selectRebal():
    strategies.strategy_code = 1
    if strategies.strategy_code == 1:
        return 0
    else:
        return -1
@blue_switch.route('/VP')
def selectVP():
    strategies.strategy_code = 2
    if strategies.strategy_code == 2:
        return 0
    else:
        return -1
@blue_switch.route('/moveAve')
def selectMoveAve():
    strategies.strategy_code = 3
    if strategies.strategy_code == 3:
        return 0
    else:
        return -1