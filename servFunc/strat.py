import threading
from flask import Blueprint
from domestic_trade_v_alpha import strategies
from domestic_trade_v_alpha.strategies import Rebal, Vp, Vola, Mas

blue_switch = Blueprint('strategiy switch', __name__, url_prefix='/strat')
code = strategies.switch()
tmp = '' # instance object save

@blue_switch.route('/exeinfo')
def exeinfo():
    for i in threading.enumerate():
        if i.name == 'vola':
            return 'True'
        if i.name == 'rebal':
            return 'True'
        if i.name == 'vp':
            return 'True'
        if i.name == 'mas':
            return 'True'
    return 'False'

@blue_switch.route('/stop')
def stop():
    for i in threading.enumerate():
        if i.name == 'vola':
            tmp.stop()
            tmp.join()
        if i.name == 'rebal':
            tmp.stop()
            tmp.join()
        if i.name == 'vp':
            tmp.stop()
            tmp.join()
        if i.name == 'mas':
            tmp.stop()
            tmp.join()
    return '0'

@blue_switch.route('/vola')
def selectVola():
    stop()
    strategies.allsell()
    vo = Vola(name='vola')
    vo.start()
    global tmp
    tmp = vo
    return '0'

@blue_switch.route('/rebal')
def selectRebal():
    stop()
    strategies.allsell()
    re = Rebal(name='rebal')
    re.start()
    global tmp
    tmp = re
    return '0'


@blue_switch.route('/vp')
def selectVP():
    stop()
    strategies.allsell()
    vp = Vp(name='vp')
    vp.start()
    global tmp
    tmp = vp
    return '0'

@blue_switch.route('/mas')
def selectMoveAve():
    stop()
    strategies.allsell()
    mas = Mas(name='mas')
    mas.start()
    global tmp
    tmp = mas
    return '0'