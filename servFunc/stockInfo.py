from flask import Blueprint, make_response, request, Response
from korStock import stock
import korStock as kor
from domestic_trade_v_alpha import domestic_trade
import json
#import createModel

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
    res = ''

    stockInf, evlu = domestic_trade.get_stock_balance()
    account = domestic_trade.CANO
    pr_account = domestic_trade.ACNT_PRDT_CD
    order_possible_cash = domestic_trade.get_balance()
    benefit_percent=evlu[0]['asst_icdc_erng_rt']
   # createModel.insertTradeinfo(account=account, pr_account=pr_account, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)
    #total_asset=총 자산, asst_icdc = 총 수익률, evlu_amt = 평가금액 총합
    res = dict({'total_asset':evlu[0]['tot_evlu_amt'],'asst_icdc':evlu[0]['asst_icdc_erng_rt'], 'evlu_amt':evlu[0]['evlu_amt_smtl_amt']})
    return json.dumps(res) #(node.js 서버와 연결했을경우 적용)
