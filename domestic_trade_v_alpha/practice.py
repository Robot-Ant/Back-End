from domestic_trade_v_alpha import domestic_trade as api
import math


# volatility_breakthrough
def back_test_vb(code):
    monthly_data = {}
    last_60days = api.get_past_datas(code)
    start = 10000000
    money = start
    for i in range(len(last_60days)-2,-1,-1):
        target_price = (float(last_60days[i+1]['stck_hgpr'])-float(last_60days[i+1]['stck_lwpr']))/2 + float(last_60days[i]['stck_oprc'])
        close_price = float(last_60days[i]['stck_clpr'])
        high_price = float(last_60days[i]['stck_hgpr'])
        if high_price > target_price:
            profit_rt = (close_price-target_price)/target_price
            profit = profit_rt*money
            money += profit
        monthly_data[last_60days[i]["stck_bsop_date"][4:6]] = int(money)
    return monthly_data

# re_balance_portfolio
def back_test_rbp(code):
    monthly_data = {}
    last_60days = api.get_past_datas(code)
    start = 10000000
    money = start
    holding_amt = 0
    holding_qty = 0
    cash = money
    for i in range(len(last_60days)-1,-1,-1):
        balance = (cash+holding_qty*float(last_60days[i]['stck_clpr']))/2
        new_qty = balance//float(last_60days[i]['stck_clpr'])
        new_amt = new_qty*float(last_60days[i]['stck_clpr'])
        
        if holding_qty == 0:
            holding_qty = new_qty
            cash = money - new_amt
            holding_amt = new_amt
        else:
            profit = new_amt - holding_amt
            profit_rt = profit / money
            money += profit
            holding_amt = new_amt
            holding_qty = new_qty
            cash = money - new_amt
        monthly_data[last_60days[i]["stck_bsop_date"][4:6]] = money
        
    return monthly_data

def data_packing():
    vb = back_test_vb("005930")
    rbp = back_test_rbp("005930")
    month = {"03":"March","04":"April","05":"May","06":"June","07":"July","08":"August"}
    date = []
    asset_vb = []
    asset_rbp = []
    for key, value in vb.items():
        date.append(month[key])
        asset_vb.append(value)
    for key, value in rbp.items():
        asset_rbp.append(value)
    result = {"date":date, "asset_vb":asset_vb, "asset_rbp":asset_rbp}
    return result