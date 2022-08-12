import requests
from datetime import date
import json
import urllib
from flask import Blueprint, make_response, request, Response, jsonify
from korStock import stock
import korStock as kor
from domestic_trade_v_alpha import domestic_trade, practice
from datetime import datetime
#import createModel
import xml.etree.ElementTree as ET

blue_get = Blueprint('getInfo', __name__, url_prefix='/info')
info = stock()

@blue_get.route('/tabledata')
def gettabledata():
    temp = domestic_trade.getTableInfo()
    return jsonify(temp)

@blue_get.route('/backdata')
def getbackrebal():
    data = practice.data_packing()
    return data

@blue_get.route('/stock')
def getStock():
    # 현재 소지한 주식을 조회힐때마다 DB에 저장
    stockInf = ''
    res = ''

    stockInf, evlu = domestic_trade.get_stock_balance()
    account = domestic_trade.CANO
    pr_account = domestic_trade.ACNT_PRDT_CD
    order_possible_cash = domestic_trade.get_balance()
    benefit_percent = evlu[0]['asst_icdc_erng_rt']
   # createModel.insertTradeinfo(account=account, pr_account=pr_account, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)
    # current_cash = 잔금, total_asset=총 자산, asst_icdc = 총 수익률, evlu_amt = 평가금액 총합, evlu_ratio = 평가손익율
    tmp = float(evlu[0]['asst_icdc_erng_rt'])
    asst_icdc = "%.2f" % tmp
    tt_asset = int(evlu[0]['tot_evlu_amt'])
    tt_asset = format(tt_asset, ',')
    ev_am = int(evlu[0]['evlu_amt_smtl_amt'])
    ev_am = format(ev_am, ',')
    evlu_ratio = sumevlu(stockInf)
    if evlu_ratio == -1:
        evlu_ratio = 0
    else:
        evlu_ratio *= 100
    evlu_ratio = "%.2f" % evlu_ratio
    res = dict({'current_cash': order_possible_cash, 'total_asset': tt_asset, 'asst_icdc': float(
        asst_icdc), 'evlu_amt': ev_am, 'evlu_ratio': float(evlu_ratio)})
    return res  # (node.js 서버와 연결했을경우 적용)


def sumevlu(stockInf):
    res_sum = 0
    res_profit = 0
    res = 0.0
    for key, stock in stockInf.items():
        res_profit += float(stock['evlu_pfls_amt'])
        res_sum += int(stock['pchs_amt'])
    try:
        res = res_profit / res_sum
        return res
    except ZeroDivisionError:
        return -1


companies = {}


@blue_get.route('/namelist')
def getcorplist():
    tree = ET.parse('CORPCODE.xml')  # CORPCODE.xml을 파싱하여 tree에 저장
    root = tree.getroot()

    namelist = []
    for company in root.findall('list'):
        stcode = company.find('stock_code').text
        if stcode != ' ':
            name = company.find('corp_name').text
            stcode = stcode
            cpcode = company.find('corp_code').text
            namelist.append(name)
            companies[name] = [cpcode, stcode]
    return namelist


@blue_get.route('/financedata')
def getfinancedata():
    name = request.args.get("id")
    code = companies[name]
    yl, el, pl = get_year_earning_price(corp_code=code[0], stock_code=code[1])
    data = {'title': name, 'year': yl, 'earning': el, 'price': pl}
    return data


my_api = 'a9e5a2117c01cd2d0760d075c204a990d0a17174'


U1 = f'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?crtfc_key={my_api}'
corp_code = ''
reprt_code = ''
year = ''

URL = '{}&corp_code={}&bsns_year={}&reprt_code={}'.format(
    U1, corp_code, reprt_code, year)
curyear = int(str(date.today())[0:4])  # 현재 년도


def getFinanceData(corp_code, reprt_code, year):
    URL = '{}&corp_code={}&bsns_year={}&reprt_code={}'.format(
        U1, corp_code, year, reprt_code)
    RLT = urllib.request.urlopen(URL)
    D = RLT.read().decode('utf-8')
    D1 = json.loads(D)  # 딕셔너리
    if(D1['status'] == '013'):  # 조회된 데이터가 없는 status
        if(year == curyear-1):
            return 'continue'  # 3월쯤에 사업보고서가 올라오는데 2월같은때 조회하면 건너뜀
        else:
            return 'none'  # 최근년도부터 거슬러올라가다가 자료가 없으면 멈춤

    list = D1['list']  # 딕셔너리에서 'list'란 키를 키로 가지는 value 리스트

    # 연결재무제표에서 당기순이익 계정 가져오기- CFS:연결재무제표,   account_nm:계정명
    for i in list:
        if(i['account_nm'] == '당기순이익' and i['fs_div'] == 'CFS'):

            return i


def get_date_and_earning(corp_code):
    datelist = []
    earninglist = []

    for i in range(curyear-1, curyear-8, -1):  # 최근 6년도
        year = str(i)
        income = getFinanceData(
            year=year, corp_code=corp_code, reprt_code='11011')
        if income == 'continue':
            continue
        elif income == 'none':
            break
        else:
            #print('{}년 당기 순이익 : {}원-보고서 제출일:{}'.format(income['bsns_year'],income['thstrm_amount'],income['rcept_no'][0:8]))
            datelist.append(income['rcept_no'][0:8])
            earninglist.append(income['thstrm_amount'].replace(',', ''))

    date_and_earning = dict(zip(datelist, earninglist))
    return date_and_earning


URL_BASE = 'https://openapivts.koreainvestment.com:29443'

APP_KEY = 'PSz1w5ad7nLupIhH1R1s0K3PSFkmfzTfiaRV'
APP_SECRET = 'fiHq56Hb9NWifu9GPVhNgOzZbgOY97X5aBjbS579uHPXfNHJR+JzjEWts1JwIKa9rE8RylNyVGMt6ejHXaFeF10gIpKGBcIVv0CRJ0Ry1M8Myru3l9dmqsTRLI/ehJ7F34GWBc4bCYe7/gr0kOhEG/QKoXpbt3nIiXGM5n1BHDatvq+UugU='


def get_access_token():
    """토큰 발급"""
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN


ACCESS_TOKEN = get_access_token()


def get_date_price(code='', date=''):
    """일자별 조회"""
    PATH = 'uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice'  # api마다 다름
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json; charset=utf-8",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "FHKST03010100",  # api마다 다름
               "custtype": "P"
               }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
        "fid_input_date_1": date,
        "fid_input_date_2": date,
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "0",
    }

    res = requests.get(URL, headers=headers, params=params)
    return res.json()

# res = get_date_price(date='20220308')


def get_year_earning_price(corp_code='', stock_code=''):
    stprlist = []  # 주가 리스트- 2021년에서 2015년까지의 보고서를 발표한 당일의 주가가 들어있음
    epslist = []  # eps 리스트-(사업보고서의 어닝)/(가장 최근 발행주식수)

    dne = get_date_and_earning(corp_code)  # 날짜와 어닝을 가져옴
    datelist = list(dne.keys())

    for i in datelist:
        res = get_date_price(date=i, code=stock_code)  # 가져온 날짜로 당일 주가를 가져옴
        output1 = res['output1']
        output2 = res['output2']
        earning = int(dne[i])
        eps = earning/int(output1['lstn_stcn'])  # 당일 공시된 어닝으로 eps 계산
        epslist.append(eps)
        stprlist.append(output2[0]['stck_clpr'])

    for i in range(0, len(datelist)-1):  # 2015년 가격은 버리고 최근 6년도 데이터를 표시-날짜를 얻을수가 없음
        print('{}년 공시날짜{} 이익:{:.2f}, 공시 당일 주가:{}'.format(
            datelist[i+1][0:4], datelist[i], epslist[i], stprlist[i]))

    yearlist = []
    for i in range(1, len(datelist)):
        yearlist.append(datelist[i][0:4])

    yearlist.reverse()
    epslist.reverse()
    stprlist.reverse()
    return yearlist, epslist, stprlist
