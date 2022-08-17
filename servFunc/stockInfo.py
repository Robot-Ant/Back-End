import requests
from datetime import date
import json
import urllib
from flask import Blueprint, make_response, request, Response, jsonify
from domestic_trade_v_alpha import domestic_trade, practice
from datetime import datetime
import xml.etree.ElementTree as ET
from time import sleep
from dateutil.relativedelta import relativedelta

blue_get = Blueprint('getInfo', __name__, url_prefix='/info')


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


companies = {}  # namelist만들면서 {기업이름:[기업코드,종목코드]}형태로 추가


@blue_get.route('/namelist')
def getcorplist():

    tree = ET.parse('CORPCODE.xml')  # CORPCODE.xml을 파싱하여 tree에 저장
    root = tree.getroot()

    namelist = []
    for company in root.findall('list'):
        stcode = company.find('stock_code').text

        cpcode = company.find('corp_code').text
        mddate = int(company.find('modify_date').text[0:4])
        # 기업개황이 최근 2년동안 갱신된적이 없는 기업과 상장되지 않은 기업은 거름
        if mddate > curyear-2 and stcode != ' ':
            name = company.find('corp_name').text
            namelist.append(name)
            companies[name] = [cpcode, stcode]
    print(f'기업 개수:{len(namelist)}개')
    return namelist


@blue_get.route('/financedata')
def getfinancedata():
    name = request.args.get("id")
    code = companies[name]  # 전역변수 companies에서 가져온 [기업코드, 종목코드]
    ql, el, pl = get_year_earning_price(corp_code=code[0], stock_code=code[1])
    data = {'title': name, 'year': ql, 'earning': el, 'price': pl}
    print('요청한 데이터', data)
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
    # print(URL)
    RLT = urllib.request.urlopen(URL)
    D = RLT.read().decode('utf-8')
    D1 = json.loads(D)  # 딕셔너리
    if(D1['status'] == '013'):  # 조회된 데이터가 없는 status
        if(year == str(curyear)):
            return 'continue'  # 3월쯤에 사업보고서가 올라오는데 2월같은때 조회하면 건너뜀
        else:
            return 'none'  # 최근년도부터 거슬러올라가다가 자료가 없으면 멈춤

    reslist = D1['list']  # 딕셔너리에서 'list'란 키를 키로 가지는 value 리스트
    # 연결재무제표를 우선해서 당기순이익 계정 가져오기- CFS:연결재무제표,   account_nm:계정명
    for i in reslist:
        if(i['account_nm'] == '당기순이익' and i['fs_div'] == 'CFS'):
            if(i['thstrm_amount'] == '-'):
                continue
            return i
    for i in reslist:
        if(i['account_nm'] == '당기순이익' and i['fs_div'] == 'OFS'):
            return i
    return 'none'


def get_date_and_earning(corp_code):
    datelist = []
    earninglist = []

    for i in range(curyear, curyear-8, -1):  # 최근 6년도
        year = str(i)
        # 사업보고서 : 11011 3분기보고서 : 11014 반기보고서 : 11012 1분기보고서 : 11013
        rplist = ['11011', '11014', '11012', '11013']
        earningtmp = []  # 사업연도의 보고서 4개의 어닝을 임시로 저장할 리스트
        for j in rplist:
            fdlist = []
            fd = getFinanceData(year=year, corp_code=corp_code, reprt_code=j)
            fdlist.append(fd)
            if fd == 'continue':
                continue
            elif fd == 'none':
                break
            else:  # 문자열을 숫자로 고침
                # print('{}년 당기 순이익 : {}원-보고서 제출일:{}'.format(
                #     fd['bsns_year'], fd['thstrm_amount'], fd['thstrm_dt'][13:]))
                # 2021.01.01 ~ 2021.12.31같은 형식의 날짜 문자열에서 마지막 날짜를 가져옴
                datelist.append(fd['thstrm_dt'][13:].replace('.', ''))
                earning = fd['thstrm_amount'].replace(',', '')
                earning = int(earning)  # 보고서의 어닝
                earningtmp.append(earning)  # 임시 리스트에 어닝 추가

        # 사업보고서는 1년 어닝이 들어있고 나머지는 3개월 어닝이 들어있기 때문에 사업보고서의 어닝을 3개월로 고침
        if len(earningtmp) == 4:  # 사업보고서가 없는 해는 길이가 3이하이기 때문에 고칠필요가 없음
            earningtmp[0] = earningtmp[0]-(sum(earningtmp[1:4]))
        if len(earningtmp) == 4:  # 보고서가 4개가 안되고 현재 년도가 아닌 년도는 버림
            earninglist = earninglist+earningtmp  # 어닝리스트에 결합하기
        elif year == curyear:
            earninglist = earninglist+earningtmp
    if len(earninglist) > 3:
        for i in range(0, len(earninglist)-3):
            earninglist[i] = earninglist[i]+sum(earninglist[i+1:i+4])
    else:  # 상장일로부터 1년 이후의 데이터만 표시됩니다
        return 'null'

    # 상장된지 4분기 이상 된 기업은 데이터의 마지막 3분기를 버림
    del datelist[-1:-4:-1]
    del earninglist[-1:-4:-1]
    print(earninglist)
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


def get_stcn(code=''):
    """상장주수 가져오기"""
    PATH = '/uapi/domestic-stock/v1/quotations/inquire-price'  # api마다 다름
    URL = f"{URL_BASE}/{PATH}"

    headers = {"Content-Type": "application/json; charset=utf-8",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "FHKST01010100",  # api마다 다름
               "custtype": "P"
               }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
    }

    res = requests.get(URL, headers=headers, params=params)
    stcn = int(res.json()["output"]["lstn_stcn"])
    return stcn


def get_price_by_date(code='', date=''):
    """일자별 조회"""
    PATH = 'uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice'  # api마다 다름
    URL = f"{URL_BASE}/{PATH}"
    # date를 2022-01-01같은 형식으로 바꿈
    datestring = f'{date[0:4]}-{date[4:6]}-{date[6:8]}'
    dateformat = '%Y-%m-%d'  # 날짜의 형식을 지정
    # 형식에 맞는 문자열을 형식에 맞는 date타입으로 바꿈
    formatdate = datetime.strptime(datestring, dateformat)
    enddate = formatdate+relativedelta(weeks=2)  # date타입 변수의 1주일 뒤 날짜를 구함
    enddate = str(enddate)[0:10]
    enddate = enddate.replace('-', '')  # date타입 변수를 20220108같은 문자열로 바꿈
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
        "fid_input_date_1": date,  # 전달받은 날짜에서 7일동안의 데이터를 받아옴
        "fid_input_date_2": enddate,  # 받아온 데이터에서 제일 마지막 데이터를 사용
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "0",
    }
    while True:
        res = requests.get(URL, headers=headers, params=params)
        rtcd = res.json()['rt_cd']
        if rtcd == '0':
            break
        else:
            sleep(0.5)  # 초당 거래 건수를 초과하면 0.5초 기다리고 다시 요청

    output2 = res.json()['output2']
    if len(output2[-1]) != 0:  # 데이터가 정상적으로 있음
        price = int(output2[-1]['stck_clpr'])
    else:  # 상장되기 이전이라 데이터가 없음
        price = 'null'
    return price


def get_year_earning_price(corp_code='', stock_code=''):
    stprlist = []  # 주가 리스트- 2021년에서 2015년까지의 보고서를 발표한 당일의 주가가 들어있음
    epslist = []  # eps 리스트-(사업보고서의 어닝)/(가장 최근 발행주식수)

    dne = get_date_and_earning(corp_code)  # 날짜와 어닝을 가져옴
    if dne == 'null':
        return [], [], []
    datelist = list(dne.keys())

    stcn = get_stcn(code=stock_code)

    for i in datelist:
        price = get_price_by_date(
            date=i, code=stock_code)  # 가져온 날짜로 당일 주가를 가져옴
        earning = int(dne[i])
        eps = earning/stcn  # 당일 공시된 어닝으로 eps 계산
        epslist.append(eps)
        stprlist.append(price)
    #print('{}년 이익:{:.2f}, 주가:{}'.format( int(i[0:4])-1,eps,output2[0]['stck_clpr'] ))
    # for i in range(0, len(datelist)-1):  # 2015년 가격은 버리고 최근 6년도 데이터를 표시-날짜를 얻을수가 없음
    #     print('{}년 공시날짜{} 이익:{:.2f}, 공시 당일 주가:{}'.format(
    #         datelist[i+1][0:4], datelist[i], epslist[i], stprlist[i]))

    quarterlist = datelist

    quarterlist.reverse()
    epslist.reverse()
    stprlist.reverse()
    return quarterlist, epslist, stprlist
    # 잘나오는거 카카오 예스24


# -eps(당기순이익/발행주식수)와 주가의 흐름을 비교해볼 수 있는 차트입니다

# -최근 6년도 데이터 중 상장일로부터 1년 이후의 데이터가 표시됩니다
