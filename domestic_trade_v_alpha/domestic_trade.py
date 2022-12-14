import threading
import requests
import json
import yaml
import datetime
import logging
import math
import time

with open('domestic_trade_v_alpha/config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN

ACCESS_TOKEN = get_access_token()

lock = threading.Lock()

logger= logging.getLogger('transation')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('transation.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def getlogdata():
    data = []
    lock.acquire()
    with open('transation.log', 'r') as file:
       while True:
        data.append(file.readline())
        if not file.readline():
            break
    lock.release()
    return data

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)
    
def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_current_price(code):
    """현재가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"FHKST01010100"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    }
    res = requests.get(URL, headers=headers, params=params)
    return float(res.json()['output']['stck_prpr'])

def get_stock_balance(message=False):
    """주식 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"VTTC8434R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = { data['pdno']:data  for data in stock_list if int(data['hldg_qty']) > 0  }
    if message:
        send_message(f"====주식 보유잔고====")
        send_message(f"주식 평가 금액: {evaluation[0]['scts_evlu_amt']}원")
        send_message(f"평가 손익 합계: {evaluation[0]['evlu_pfls_smtl_amt']}원")
        send_message(f"총 자산 금액: {evaluation[0]['tot_evlu_amt']}원")
        send_message(f"=================")
    return stock_dict, evaluation

def get_balance(message=False):
    """현금 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"VTTC8908R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": "005930",
        "ORD_UNPR": "65500",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "Y",
        "OVRS_ICLD_YN": "Y"
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    cash = res.json()['output']['ord_psbl_cash']
    if message:
        send_message(f"주문 가능 현금 잔고: {cash}원")
    return float(cash)

def buy(code, qty):
    """주식 시장가 매수"""  
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"VTTC0802U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매수 성공]{str(res.json())}")
        logger.info(f"0, {code}, {get_current_price(code)}, {qty}")
        return True
    else:
        send_message(f"[매수 실패]{str(res.json())}")
        return False

def sell(code, qty):
    """주식 시장가 매도"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(qty),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"VTTC0801U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매도 성공]{str(res.json())}")
        logger.info(f"1, {code}, {get_current_price(code)}, {qty}")
        return True
    else:
        send_message(f"[매도 실패]{str(res.json())}")
        return False
    
def get_target_price(code='005930'):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    stck_oprc = float(res.json()['output'][0]['stck_oprc']) #오늘 시가
    stck_hgpr = float(res.json()['output'][1]['stck_hgpr']) #전일 고가
    stck_lwpr = float(res.json()['output'][1]['stck_lwpr']) #전일 저가
    target_price = stck_oprc + (stck_hgpr - stck_lwpr)/2
    return target_price

def get_evaluation():
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"VTTC8434R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    evaluation = res.json()['output2']
    send_message(f"[나의 자산]{str(evaluation[0]['nass_amt'])}")
    return evaluation

def get_moving_average(code):
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400",
        "custtype":"P",
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
        "fid_org_adj_prc": "0000000000",
        "fid_period_div_code": "D"
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    last_20d = res.json()['output']
    sum = 0
    sqrsum = 0
    for i in range(20):
        sum += float(last_20d[i]['stck_clpr'])
        sqrsum += pow(float(last_20d[i]['stck_clpr']),2)
    m = sum/20
    s = math.sqrt(sqrsum/20-pow(m,2))
    return (m,s)

def get_volume_power(code):
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010300",
        "custtype":"P",
    }
    params = {
        "FID_INPUT_ISCD":code,
        "FID_COND_MRKT_DIV_CODE":"J"
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    return float(res.json()['output'][0]['tday_rltv'])

def get_ordered(code):
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_type":"1",
        "custtype":"P",
        "content_type":"UTF-8"
    }
    body = {
        "tr_id":"H0STCNI9",
        "tr_key":code
    }
    res = requests.get(URL,headers=headers,bodys=body)
    return res.json()

def get_monthly_asset():
    monthly_data = [{"date" : [],"asset_vb":[],"asset_rbp":[]},{"date" : [],"asset_mas":[]}]
    with open("vb_record.log",'r') as record:
        while True:
            data = record.readline().split()
            if len(data) != 10:
                break
            if data[0][4:6] in monthly_data[0]["date"]:
                monthly_data[0]["asset_vb"][monthly_data[0]["date"].index(data[0][4:6])] = int(float(data[9]))
            else:
                monthly_data[0]["date"].append(data[0][4:6])
                monthly_data[0]["asset_vb"].append(int(float(data[9])))
    with open("rbp_record.log",'r') as record:
        while True:
            data = record.readline().split()
            if len(data) != 10:
                break
            if monthly_data[0]["date"].index(data[0][4:6]) >= len(monthly_data[0]["asset_rbp"]) :
                monthly_data[0]["asset_rbp"].append(int(float(data[9])))
            else:
                monthly_data[0]["asset_rbp"][monthly_data[0]["date"].index(data[0][4:6])] = int(float(data[9]))
    with open("mas_record.log",'r') as record:
        while True:
            data = record.readline().split()
            if len(data) != 10:
                break
            if data[0][4:6] in monthly_data[1]["date"]:
                monthly_data[1]["asset_mas"][monthly_data[1]["date"].index(data[0][4:6])] = int(float(data[9]))
            else:
                monthly_data[1]["date"].append(data[0][4:6])
                monthly_data[1]["asset_mas"].append(int(float(data[9])))
    return monthly_data

def get_past_datas(code,since):
    datas = []
    t_now = datetime.datetime.now()
    to = str(t_now.year)+(('0'+str(t_now.month)) if t_now.month < 10 else str(t_now.month)) + (('0'+str(t_now.day)) if t_now.day < 10 else str(t_now.day))
    while True:
        datas.append(get_last_100days(code,since,to))
        to = str(int(datas[len(datas)-1][len(datas[len(datas)-1])-1]['stck_bsop_date'])-1)
        if int(to) < int(since) or len(datas[len(datas)-1]) < 100:
            break
    result = [data for i in datas for data in i ]
    return result

def get_last_100days(code,past,now):
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST03010100",
        "custtype":"P",
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_date_1": past,
        "fid_input_date_2": now,
        "fid_input_iscd": code,
        "fid_org_adj_prc": "0",
        "fid_period_div_code": "D" 
    }
    time.sleep(0.11)
    res = requests.get(URL, headers=headers, params=params)
    return res.json()['output2']

def get_past_moving_average(datas,index):
    sum = 0
    sqr_sum = 0
    for i in range(index,index+20):
        sum += float(datas[i]['stck_clpr'])
        sqr_sum += pow(float(datas[i]['stck_clpr']),2)
    m = sum/20
    s = math.sqrt(sqr_sum/20 - pow(m,2))
    return (m,s)

def getTableInfo():
    data = getlogdata()
    res = []
    now_time = time.localtime()
    mon = now_time.tm_mon
    mon = '{0:0>2}'.format(mon)
    day = now_time.tm_mday
    current_day = f'{mon}-{day}'
    reverse_res = []
    #{date:'08-06', time:159, mesu:6.0, code:24, price:4.0, count:5}
    for i in data:
        if i == '':
            break
        dt, ms ,code, pr, qt = i.split(',')
        da, tim = dt.split()
        da = da[5:len(da)]
        if da != current_day:
            continue
        j, ti = ms.split('-')
        if ti == '0':
            ti = '매수'
        else:
            ti = '매도'
        code = code.lstrip()
        pr = pr.lstrip()
        pr = int(float(pr))
        qt = qt.strip(' \n')
        res.append(dict({
            'date':da,
            'time':tim,
            'order_type':ti,
            'code':code,
            'price':format(pr,','),
            'count':qt
        }))
    reverse_res = res[::-1]
    return reverse_res