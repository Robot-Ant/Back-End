from flask import Blueprint
from korStock import stock
import korStock as kor
import createModel

#from domestic_trade_v_alpha import strategies
blue_get = Blueprint('getInfo', __name__, url_prefix='/info')
# blue_switch = Blueprint('')
info = stock()
@blue_get.route('/cash')
def getCash():
    cash = stock.currentCash()
    return str(cash)

@blue_get.route('/stock')
def getStock():
    # 현재 소지한 주식을 조회힐때마다 DB에 저장
    evlu = ''
    stockInf = ''
    stockInf, evlu = stock.checkStock()
    account = kor.CANO
    pr_account = kor.ACNT_PRDT_CD
    order_possible_cash = stock.currentCash()
    benefit_percent=evlu[0]['asst_icdc_erng_rt']
    createModel.insertTradeinfo(account=account, pr_account=pr_account, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)
    return str(stockInf[0]) #(node.js 서버와 연결했을경우 적용)
