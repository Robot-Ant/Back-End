import threading
from flask import Blueprint
from domestic_trade_v_alpha import strategies
from domestic_trade_v_alpha.strategies import Rebal, Vp, Vola, Mas

blue_switch = Blueprint('strategiy switch', __name__, url_prefix='/strat')
code = strategies.switch()
tmp = '' # instance object save

@blue_switch.route('/stop')
def stop():
    for i in threading.enumerate():
        if i.name == 'vola':
            tmp.stop()
            return '0'
        if i.name == 'rebal':
            tmp.stop()
            return '0'
        if i.name == 'vp':
            tmp.stop()
            return '0'
        if i.name == 'mas':
            tmp.stop()
            return '0'
    return '-1'

@blue_switch.route('/vola')
def selectVola():
    stop()
    vo = Vola(name='vola')
    vo.start()
    global tmp
    tmp = vo
    return '0'

@blue_switch.route('/rebal')
def selectRebal():
    stop()
    re = Rebal(name='rebal')
    re.start()
    global tmp
    tmp = re
    return '0'


@blue_switch.route('/vp')
def selectVP():
    stop()
    vp = Vp(name='vp')
    vp.start()
    global tmp
    tmp = vp
    return '0'

@blue_switch.route('/mas')
def selectMoveAve():
    stop()
    mas = Mas(name='mas')
    mas.start()
    global tmp
    tmp = mas
    return '0'