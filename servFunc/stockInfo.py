from flask import Blueprint, make_response, request, Response, jsonify
from korStock import stock
import korStock as kor
from domestic_trade_v_alpha import domestic_trade
#import createModel

blue_get = Blueprint('getInfo', __name__, url_prefix='/info')
info = stock()


@blue_get.route('/stock')
def getStock():
    # 현재 소지한 주식을 조회힐때마다 DB에 저장
    stockInf = ''
    res = ''

    stockInf, evlu = domestic_trade.get_stock_balance()
    account = domestic_trade.CANO
    pr_account = domestic_trade.ACNT_PRDT_CD
    order_possible_cash = domestic_trade.get_balance()
    benefit_percent=evlu[0]['asst_icdc_erng_rt']
   # createModel.insertTradeinfo(account=account, pr_account=pr_account, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)
    #current_cash = 잔금, total_asset=총 자산, asst_icdc = 총 수익률, evlu_amt = 평가금액 총합
    tmp = float(evlu[0]['asst_icdc_erng_rt'])
    asst_icdc = "%.2f"%tmp
    tt_asset = int(evlu[0]['tot_evlu_amt'])
    tt_asset = format(tt_asset, ',')
    ev_am = int(evlu[0]['evlu_amt_smtl_amt'])
    ev_am = format(ev_am, ',')
    res = dict({'current_cash':order_possible_cash,'total_asset':tt_asset, 'asst_icdc':float(asst_icdc), 'evlu_amt':ev_am})
    return res #(node.js 서버와 연결했을경우 적용)
