
from flask import Flask, request
from flask import render_template
from korStock import *
from createModel import Logininfo
import createModel
'''
app = Flask(__name__)

@app.route('/getCash')
def getCash():
    return currentCash()

@app.route('/getStock')
# dict or json으로 반환
def getStock():
    # 현재 소지한 주식을 조회힐때마다 DB에 저장
    stock = checkStock()
    createModel.insertTradeinfo(account=CANO, pr_account=ACNT_PRDT_CD, order_possible_cash=currentCash(), benefit_percent=stock["evlu_pfls_rt"])
    return str(stock) #(node.js 서버와 연결했을경우 적용)
    """
    for s in stock:
        a = s["prdt_name"]
        b = s["hldg_qty"]
        c = s["prpr"]
        d = s["evlu_pfls_amt"]
        e = s["evlu_pfls_rt"]
        rs = f"종목명:{a} 보유수량:{b}  현재가:{c}  평가손익:{d}  평가손익율:{e}"
        return rs
    """
@app.route('/insertlogininfo')
def postlogin():
    res = createModel.insertLogininfo()
    if res == 1:
        return 'success'
    else:
        if res == -1:
            return 'AttributeError:db에 들어갈 요소가 부족합니다'

@app.route('/insertorderinfo')
def postorder():
    res = createModel.insertOrderinfo()
    if res == 1:
        return 'success'
    else:
        if res == -1:
            return 'AttributeError:db에 들어갈 요소가 부족합니다'

@app.route('/inserttradeinfo')
def posttrade():
    res = createModel.insertTradeinfo()
    if res == 1:
        return 'success'
    else:
        if res == -1:
            return 'AttributeError:db에 들어갈 요소가 부족합니다'


if __name__ == '__main__':
    app.run(debug=True)

'''