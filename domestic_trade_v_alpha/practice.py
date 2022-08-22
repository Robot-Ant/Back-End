from domestic_trade_v_alpha import domestic_trade as api
import datetime
# volatility_breakthrough
def back_test_monthly_vb(code):
    
    monthly_data = {}
    past_datas = api.get_past_datas(code,"20210815")
    start = 10000000
    money = start
    for i in range(len(past_datas)-2,-1,-1):
        target_price = (float(past_datas[i+1]['stck_hgpr'])-float(past_datas[i+1]['stck_lwpr']))/2 + float(past_datas[i]['stck_oprc'])
        close_price = float(past_datas[i]['stck_clpr'])
        high_price = float(past_datas[i]['stck_hgpr'])
        profit_rt = 0
        profit = 0
        if high_price > target_price:
            profit_rt = (close_price-target_price)/target_price
            profit = profit_rt*money
            money += profit
        monthly_data[past_datas[i]['stck_bsop_date'][2:6]]=money
    return monthly_data

def back_test_monthly_mas(code):
    past_datas = api.get_past_datas(code,"20210714")
    start = 10000000
    monthly_data = {}
    money = start
    bought = False
    bought_price = 0
    qty = 0
    for i in range(len(past_datas)-21,-1,-1):
        ms = api.get_past_moving_average(past_datas,i)
        if bought:
            sell_price = float(ms[0]+ms[1]*2)
            hgpr = float(past_datas[i]['stck_hgpr'])
            if hgpr >= sell_price:
                profit_rt = (sell_price-bought_price)/bought_price
                profit = money*profit_rt
                money += profit
                bought = False
            monthly_data[past_datas[i]['stck_bsop_date'][2:6]] = float(past_datas[i]['stck_clpr'])*qty
        else:
            buy_price = float(ms[0]-ms[1]*2)
            lwpr = float(past_datas[i]['stck_lwpr'])
            if lwpr <= buy_price:
                bought_price = buy_price
                qty = money / buy_price
                bought = True
            monthly_data[past_datas[i]['stck_bsop_date'][2:6]]=money
    if bought:
        profit_rt = (float(past_datas[0]['stck_clpr'])-bought_price)/bought_price
        profit = money*profit_rt
        money += profit
    
    return monthly_data


# re_balance_portfolio
def back_test_monthly_rbp(code):
    monthly_data = {}
    past_datas = api.get_past_datas(code,"20210815")
    start = 10000000
    money = start
    holding_amt = 0
    holding_qty = 0
    cash = money
    for i in range(len(past_datas)-1,-1,-1):
        balance = (cash+holding_qty*float(past_datas[i]['stck_clpr']))/2
        new_qty = balance//float(past_datas[i]['stck_clpr'])
        new_amt = new_qty*float(past_datas[i]['stck_clpr'])
        
        if holding_qty == 0:
            holding_qty = new_qty
            cash = money - new_amt
            holding_amt = new_amt
        else:
            profit = new_amt - holding_amt
            money += profit
            holding_amt = new_amt
            holding_qty = new_qty
            cash = money - new_amt
        monthly_data[past_datas[i]["stck_bsop_date"][2:6]] = money
        
    return monthly_data


def data_packing():
    vb = back_test_monthly_vb("005930")
    rbp = back_test_monthly_rbp("005930")
    mas = back_test_monthly_mas("005930")
    date = []
    asset_vb = []
    asset_rbp = []
    asset_mas = []
    for key, value in vb.items():
        a = str(key[0:2])
        b = str(key[2:4])
        key = f'{a}/{b}'
        date.append(key)
        asset_vb.append(int(value))
    for key, value in rbp.items():
        asset_rbp.append(int(value))
    for key, value in mas.items():
        asset_mas.append(int(value))
    result = {"date":date, "asset_vb":asset_vb, "asset_rbp":asset_rbp,"asset_mas":asset_mas}
    return result

kospi100 = {
    "삼성전자":"005930",
    "SK하이닉스":"000660",
    "NAVER":"035420",
    "카카오":"035720",
    "삼성바이오로직스":"207940",
    "LG화학":"051910",
    "삼성SDI":"006400",
    "현대차":"005380",
    "셀트리온":"068270",
    "기아":"000270",
    "카카오뱅크":"323410",
    "POSCO홀딩스":"005490",
    "삼성물산":"028260",
    "현대모비스":"012330",
    "LG전자":"066570",
    "삼성전자우":"005935",
    "LG생활건강":"051900",
    "SK이노베이션":"096770",
    "SK텔레콤":"017670",
    "KB금융":"105560",
    "신한지주":"055550",
    "SK":"034730",
    "SK바이오사이언스":"302440",
    "엔씨소프트":"036570",
    "한국전력":"015760",
    "HMM":"011200",
    "삼성생명":"032830",
    "SK아이이테크놀로지":"361610",
    "LG":"003550",
    "삼성전기":"009150",
    "삼성에스디에스":"018260",
    "아모레퍼시픽":"090430",
    "하나금융지주":"086790",
    "포스코케미칼":"003670",
    "하이브":"352820",
    "넷마블":"251270",
    "두산에너빌리티":"034020",
    "KT&G":"033780",
    "S-Oil":"010950",
    "대한항공":"003490",
    "삼성화재":"000810",
    "SK바이오팜":"326030",
    "고려아연":"010130",
    "한국조선해양":"009540",
    "롯데케미칼":"011170",
    "KT":"030200",
    "한온시스템":"018880",
    "우리금융지주":"316140",
    "LG디스플레이":"034220",
    "기업은행":"024110",
    "한화솔루션":"009830",
    "CJ제일제당":"097950",
    "현대글로비스":"086280",
    "현대제철":"004020",
    "금호석유":"011780",
    "LG유플러스":"032640",
    "코웨이":"021240",
    "한국타이어엔테크놀로지":"161390",
    "SKC":"011790",
    "현대건설":"000720",
    "에스디바이오건설":"137310",
    "미래에셋증권":"006800",
    "강원랜드":"035250",
    "현대중공업":"329180",
    "HD현대":"267250",
    "한미사이언스":"008930",
    "LG이노텍":"011070",
    "아모레G":"002790",
    "F&F":"383220",
    "이마트":"139480",
    "오리온":"271560",
    "삼성엔지니어링":"028050",
    "맥쿼리인프라":"088980",
    "한진칼":"180640",
    "두산밥캣":"241560",
    "유한양행":"000100",
    "KODEX200":"069500",
    "쌍용C&E":"003410",
    "삼성중공업":"010140",
    "DB손해보험":"005830",
    "팬오션":"028670",
    "롯데지주":"004990",
    "삼성카드":"029780",
    "GS":"078930",
    "CJ대한통운":"000120",
    "한미약품":"128940",
    "삼성증권":"016360",
    "녹십자":"006280",
    "현대차2우B":"005387",
    "효성티앤씨":"298020",
    "일진머티리얼즈":"020150",
    "GS건설":"006360",
    "호텔신라":"008770",
    "NH투자증권":"005940",
    "GS리테일":"007070",
    "메리츠증권":"008560",
    "신풍제약":"019170",
    "현대오토에버":"307950",
    "대우조선해양":"042660",
    "휠라홀딩스":"081660",
}

def back_test_ratio_vb(code):
    t_now = datetime.datetime.now()
    lastyear = str(int(t_now.year)-1) + (('0'+str(t_now.month)) if t_now.month < 10 else str(t_now.month)) + (('0'+str(t_now.day)) if t_now.day < 10 else str(t_now.day))
    past_datas = api.get_past_datas(code,lastyear)
    start = 10000000
    money = start
    for i in range(len(past_datas)-2,-1,-1):
        target_price = (float(past_datas[i+1]['stck_hgpr'])-float(past_datas[i+1]['stck_lwpr']))/2 + float(past_datas[i]['stck_oprc'])
        close_price = float(past_datas[i]['stck_clpr'])
        high_price = float(past_datas[i]['stck_hgpr'])
        profit_rt = 0
        profit = 0
        if high_price > target_price:
            profit_rt = (close_price-target_price)/target_price
            profit = profit_rt*money
            money += profit
    return (money-start)/start*100

def back_test_ratio_mas(code):
    t_now = datetime.datetime.now()
    lastyear = str(int(t_now.year)-1) + (('0'+str(t_now.month)) if t_now.month < 10 else str(t_now.month)) + (('0'+str(t_now.day)) if t_now.day < 10 else str(t_now.day))
    past_datas = api.get_past_datas(code,lastyear)
    start = 10000000
    money = start
    bought = False
    bought_price = 0
    for i in range(len(past_datas)-21,-1,-1):
        ms = api.get_past_moving_average(past_datas,i)
        if bought:
            sell_price = float(ms[0]+ms[1]*2)
            hgpr = float(past_datas[i]['stck_hgpr'])
            if hgpr >= sell_price:
                profit_rt = (sell_price-bought_price)/bought_price
                profit = money*profit_rt
                money += profit
                bought = False
        else:
            buy_price = float(ms[0]-ms[1]*2)
            lwpr = float(past_datas[i]['stck_lwpr'])
            if lwpr <= buy_price:
                bought_price = buy_price
                bought = True
    if bought:
        profit_rt = (float(past_datas[0]['stck_clpr'])-bought_price)/bought_price
        profit = money*profit_rt
        money += profit
    return (money-start)/start*100

def back_test_ratio_rbp(code):
    t_now = datetime.datetime.now()
    lastyear = str(int(t_now.year)-1) + (('0'+str(t_now.month)) if t_now.month < 10 else str(t_now.month)) + (('0'+str(t_now.day)) if t_now.day < 10 else str(t_now.day))
    past_datas = api.get_past_datas(code,lastyear)
    start = 10000000
    money = start
    holding_qty = 0
    cash = money
    for i in range(len(past_datas)-1,-1,-1):
        money = cash+holding_qty*float(past_datas[i]['stck_oprc'])
        cash = money/2
        res = divmod(cash,float(past_datas[i]['stck_oprc']))
        holding_qty = res[0]
        cash += res[1]
        
    return (money-start)/start*100