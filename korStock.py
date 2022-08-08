import json
import requests
import yaml
import createModel
from datetime import datetime

with open('info.yml', encoding='UTF-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
APP_KEY = data['APP_KEY']
APP_SECRET = data['APP_SECRET']
URL_BASE = data['VURL_BASE']
CANO = data['CANO']
ACNT_PRDT_CD = data['ACNT_PRDT_CD']

def getToken():
        headers = {"content-type":"application/json"}
        body = {
        "grant_type":"client_credentials",
        "appkey":APP_KEY, 
        "appsecret":APP_SECRET}
        PATH = "oauth2/tokenP"
        URL = f"{URL_BASE}/{PATH}"
        res = requests.post(URL, headers=headers, data=json.dumps(body))
        ACCESS_TOKEN = res.json()["access_token"]
        return ACCESS_TOKEN
ACCESS_TOKEN = getToken()
# 토큰 발급 거래시 사용
class stock:

    def __init__(self):
        global APP_SECRET, APP_KEY, URL_BASE, CANO, ACNT_PRDT_CD, ACCESS_TOKEN
    # 암호화 해시키
    def hashkey(self,datas):
        PATH = "uapi/hashkey"
        URL = f"{URL_BASE}/{PATH}"
        headers = {
            "Content-Type" : "application/json",
            "appKey" : APP_KEY,
            "appSecret" : APP_SECRET,
        }
        res = requests.post(URL, headers=headers, data=json.dumps(datas))
        hashkey = res.json()["HASH"]
        return hashkey

    #매수, 매도
    #pdno = 종목코드, ord_qty = 주량, ord_dvsn = 주문방법, ord_unpr = 주당가격
    """
    ord_dvsn 종류
    00 : 지정가
    01 : 시장가
    02 : 조건부지정가
    03 : 최유리지정가
    04 : 최우선지정가
    05 : 장전 시간외
    06 : 장후 시간외
    07 : 시간외 단일가
    08 : 자기주식
    09 : 자기주식S-Option
    10 : 자기주식금전신탁
    11 : IOC지정가 (즉시체결,잔량취소)
    12 : FOK지정가 (즉시체결,전량취소)
    13 : IOC시장가 (즉시체결,잔량취소)
    14 : FOK시장가 (즉시체결,전량취소)
    15 : IOC최유리 (즉시체결,잔량취소)
    16 : FOK최유리 (즉시체결,전량취소)
    """
    def buy(pdno="", ord_kind=True, ord_qty=0, ord_unpr=0, ord_dvsn="00"):
        if pdno=="":
            return "종목코드가 입력되지 않았습니다"
        PATH = "uapi/domestic-stock/v1/trading/order-cash"
        URL = f"{URL_BASE}/{PATH}"
        if ord_kind==True:
            #매수
            kind = "VTTC0802U"
        else:
            #매도
            kind = "VTTC0801U"
        body = {
            "CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "PDNO":pdno,
            "ORD_DVSN":ord_dvsn,
            "ORD_QTY":str(ord_qty),
            "ORD_UNPR":str(ord_unpr)
        }
        hashK = stock.hashkey(body)
        headers = {
            "Content-Type":"application/json",
            "authorization":f"Bearer {ACCESS_TOKEN}",
            "appkey":APP_KEY,
            "appsecret":APP_SECRET,
            "tr_id":kind,
            "hashkey":hashK  
        }

        res = requests.post(URL, headers=headers, data=json.dumps(body))
        errcode = res.json()["rt_cd"]
        msg = res.json()["msg1"]
        if errcode == 0:
            if ord_kind == True:
                createModel.insertOrderinfo(order_price=ord_unpr, order_kind='T', order_qty=ord_qty, order_time=datetime.utcnow, order_str='')
            else:
                createModel.insertOrderinfo(order_price=ord_unpr, order_kind='F', order_qty=ord_qty, order_time=datetime.utcnow, order_str='')
            return msg
        else:
            print(f"errcode:{errcode}/{msg}")
            result = f"errCode:{errcode}, msg:{msg}"
            return result

    # 현재 보유 주식
    def checkStock():
        PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
        URL = f"{URL_BASE}/{PATH}"
        parameters = {
            "CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "AFHR_FLPR_YN":"N",
            "OFL_YN":"",
            "INQR_DVSN":"02",
            "UNPR_DVSN":"01",
            "FUND_STTL_ICLD_YN":"N",
            "FNCG_AMT_AUTO_RDPT_YN":"N",
            "PRCS_DVSN":"00",
            "CTX_AREA_FK100":"",
            "CTX_AREA_NK100":""
        }
        headers = {
            "Content-Type":"application/json",
            "authorization":f"Bearer {ACCESS_TOKEN}",
            "appkey":APP_KEY,
            "appsecret":APP_SECRET,
            "tr_id":"VTTC8434R"      
        }
        res = requests.get(URL, headers=headers, params=parameters)
        errcode = res.json()["rt_cd"]
        msg1 = res.json()["msg1"]
        print("======요청결과======")
        if errcode != "0":
            print(f"errcode:{errcode}/{msg1}")
            print("======요청결과======")
            return None
        else:
            stocklist = res.json()["output1"]
            evlu = res.json()["output2"]
            i = 1
            for stock in stocklist:
                print("종목명:",stock["prdt_name"],sep="")
                print("보유수량:",stock["hldg_qty"],sep="")
                print("현재가:", stock["prpr"],sep="")
                print("평가손익:",stock["evlu_pfls_amt"],sep="")
                print("평가손익율",stock["evlu_pfls_rt"],sep="")
                print(f"======{i}======")
                i += 1
        print("======요청결과======")
        # print(evlu['evlu_pfls_smtl_amt'])
        return stocklist, evlu

    #현재 주문 가능 현금 조회
    def currentCash():
        PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"       
        URL = f"{URL_BASE}/{PATH}"
        datas = {
            "CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "PDNO":"005930",
            "ORD_UNPR":"65500",
            "ORD_DVSN":"01",
            "CMA_EVLU_AMT_ICLD_YN":"N",
            "OVRS_ICLD_YN":"N"
        }
        headers = {
            "Content-Type":"application/json",
            "authorization":f"Bearer {ACCESS_TOKEN}",
            "appkey":APP_KEY,
            "appsecret":APP_SECRET,
            "tr_id":"VTTC8908R",
        }
        res = requests.get(URL, headers=headers, params=datas)
        errcode = res.json()["rt_cd"]
        msg = res.json()["msg1"]
        if errcode != '0':
            print(f"errcode:{errcode}/{msg}")
            return -1
        else:
            cash = res.json()["output"]["ord_psbl_cash"]
            print("잔액:",cash,sep="")
            return cash

    def dartInfo():
        #dart 기업고유번호와 기업명 dict return
        res = {}
        temp = {}
        with open('CORPCODE.json', 'r') as file:
            jsonString = json.load(file)
        for a, b in jsonString.items():
            temp = b
        i = 0
        resList = []
        for a,b in temp.items():
            tmp = b
        for tp in tmp:
            res = dict({'corp_name':tp['corp_name'], 'corp_code':tp['corp_code']})
            resList.append(res)
            i += 1
        return resList
