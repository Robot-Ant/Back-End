from domestic_trade_v_alpha import domestic_trade as api

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