from flask import Blueprint
from korStock import stock
import korStock as kor
import createModel

blue_get = Blueprint('getInfo', __name__, url_prefix='/info')
info = stock()
@blue_get.route('/cash')
def getCash():
    cash = stock.currentCash()
    return str(cash)

@blue_get.route('/stock')
def getStock():
    # 현재 소지한 주식을 조회힐때마다 DB에 저장
    stockInf = stock.checkStock()
    account = kor.CANO
    pr_account = kor.ACNT_PRDT_CD
    order_possible_cash = stock.currentCash()
    benefit_percent=stockInf[0]["evlu_pfls_rt"]
    createModel.insertTradeinfo(account=account, pr_account=pr_account, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)
    return str(stockInf[0]) #(node.js 서버와 연결했을경우 적용)
