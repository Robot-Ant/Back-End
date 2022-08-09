from flask import Blueprint, make_response, request, Response
from korStock import stock
import korStock as kor
from domestic_trade_v_alpha import domestic_trade
import createModel

blue_get = Blueprint('getInfo', __name__, url_prefix='/info')
info = stock()
@blue_get.route('/cash', methods=['GET', 'OPTIONS'])
def getCash():
    cash = domestic_trade.get_balance()
    return str(cash)

@blue_get.route('/stock')
def getStock():
    # json으로 리턴 수정(미완)
    # 현재 소지한 주식을 조회힐때마다 DB에 저장
    stockInf = ''
    """
    stockInf, evlu = stock.checkStock()
    account = kor.CANO
    pr_account = kor.ACNT_PRDT_CD
    order_possible_cash = stock.currentCash()
    benefit_percent = evlu[0]['asst_icdc_erng_rt']
    """
    stockInf, evlu = domestic_trade.get_stock_balance()
    account = domestic_trade.CANO
    pr_account = domestic_trade.ACNT_PRDT_CD
    order_possible_cash = domestic_trade.get_balance()
    benefit_percent=evlu[0]['asst_icdc_erng_rt']
    createModel.insertTradeinfo(account=account, pr_account=pr_account, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)

    return stockInf #(node.js 서버와 연결했을경우 적용)
