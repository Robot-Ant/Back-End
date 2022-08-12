import datetime
import threading
from domestic_trade_v_alpha import domestic_trade as api
import time

def allsell():
    currentStock, i = api.get_stock_balance()
    key = currentStock.keys()
    for i in key:
        api.sell(i, currentStock[i]['hldg_qty'])


class Vola(threading.Thread):
    def __init__(self, name=''):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.symbol_list = ["005930","035720","000660","005380","035420","003550","015760"]
        self.flag = True
    
    def stop(self):
        self.flag = False

    def run(self):
        total_cash = float(api.get_balance(True)) # 보유 현금 조회
        stock_dict, i = api.get_stock_balance(True) # 보유 주식 조회
        target_buy_count = 3 # 매수할 종목 수
        buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
        bought_list = []
        for sym in stock_dict.keys():
            bought_list.append(sym)
        STOP_LOSS_RATIO = 2

        while self.flag:
            t_now = datetime.datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.datetime.today().weekday()
            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                api.send_message("주말이므로 프로그램을 종료합니다.")
                break
            if t_9 < t_now < t_start: # 잔여 수량 매도
                for sym, data in stock_dict.items():
                    api.sell(sym, data['hldg_qty'])
                    api.send_message(f"{sym} 잔여수량 매도합니다.")
                    bought_list.remove(sym)
            if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수
                for sym in self.symbol_list:  

                    # sell
                    if sym in stock_dict.keys() and sym in bought_list:
                        try:
                            stock, i = api.get_stock_balance(False)
                            stock = stock[sym]
                        except:
                            pass
                        loss = float(stock['evlu_pfls_rt'])
                        if loss < -STOP_LOSS_RATIO:
                            result = api.sell(sym,int(stock['hldg_qty']))
                            if result:
                                stock_dict,i = api.get_stock_balance(True)
                                bought_list.remove(sym)
                                time.sleep(0.11)
                    
                    # buy
                    elif len(bought_list) < target_buy_count and not(sym in bought_list) :
                        target_price = api.get_target_price(sym)
                        current_price = api.get_current_price(sym)
                        if target_price < current_price:
                            buy_qty = 0  # 매수할 수량 초기화
                            buy_qty = buy_amount//current_price
                            if buy_qty > 0:
                                api.send_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
                                result = api.buy(sym, buy_qty)
                                if result:
                                    stock_dict, i = api.get_stock_balance(True)
                                    bought_list.append(sym)
                                    time.sleep(0.11)
                if t_now.minute %30 == 0 and t_now.second <= 5: 
                    api.get_stock_balance(True)
                    time.sleep(5)
            if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
                for sym, data in stock_dict.items():
                    api.sell(sym, data['hldg_qty'])
            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                api.send_message("장이 닫히므로 프로그램을 종료합니다.")
                evaluation = api.get_evaluation()
                myseed = float(evaluation[0]['nass_amt'])   #순자산금액
                with open('Daily Record.p','a') as recordfile:
                    recordfile.write(f"{t_now.date()}-{myseed}\n")
                break

class Rebal(threading.Thread):
    def __init__(self, name=''):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.symbol_list = ["005930","035720","000660","005380","035420","003550","015760"]
        self.flag = True
    
    def stop(self):
        self.flag = False
    
    def run(self):
        symbol = "409820"
        total_asset = float(api.get_evaluation()[0]['nass_amt']) # 보유 현금 조회
        stock_dict, i = api.get_stock_balance(True) # 보유 주식 조회
        bought_list = []
        for sym in stock_dict.keys():
            bought_list.append(sym)

        while self.flag:
            t_now = datetime.datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.datetime.today().weekday()
            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                api.send_message("주말이므로 프로그램을 종료합니다.")
                break
            if t_9 < t_now < t_exit :  # AM 09:00 ~ PM 03:20 : 매수
                stock_dict, i = api.get_stock_balance(False)
                if not(symbol in bought_list):
                    new_balance = total_asset/2
                    current_price = float(api.get_current_price(symbol))
                    qty = new_balance//current_price
                    api.send_message(f"{symbol} {current_price} 매수를 시도합니다.")
                    result = api.buy(symbol, qty)
                    if result:
                            stock_dict, i = api.get_stock_balance(True)
                            bought_list.append(symbol)
                            time.sleep(0.11)
                            continue
                if symbol in stock_dict.keys() and symbol in bought_list:
                    if (t_now.hour == 15 and t_now.minute == 15 and t_now.second <= 5) or (abs(float(stock_dict[symbol]['evlu_erng_rt'])) >= 3) :
                        new_balance = total_asset/2
                        unbalanced = new_balance - float(stock_dict[symbol]['evlu_amt'])
                        current_price = float(api.get_current_price(symbol))
                        qty = unbalanced//current_price
                        if qty < 0:
                            api.send_message(f"리밸런싱 {-(qty+1)}주 매수를 시도합니다 새로운 균형 : {new_balance}")
                            result = api.sell(symbol, -(qty+1))
                            if result:
                                stock_dict, i = api.get_stock_balance(True)
                                time.sleep(0.11)
                        elif qty > 0:
                            api.send_message(f"리밸런싱 {qty}주 매도를 시도합니다 새로운 균형 : {new_balance}")
                            result = api.buy(symbol, qty)
                            if result:
                                    stock_dict, i = api.get_stock_balance(True)
                                    time.sleep(0.11)
                        time.sleep(0.11)
                if t_now.minute%30 == 0 and t_now.second <= 5: 
                    api.get_stock_balance(True)
                    time.sleep(5)
            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                api.send_message("장이 닫히므로 프로그램을 종료합니다.")
                evaluation = api.get_evaluation()
                myseed = float(evaluation[0]['nass_amt'])   #순자산금액
                with open('Daily Record.p','a') as recordfile:
                    recordfile.write(f"{t_now.date()}-{myseed}\n")
                break

class Vp(threading.Thread):
    def __init__(self, name=''):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.symbol_list = ["005930","035720","000660","005380","035420","003550","015760"]
        self.flag = True
    
    def stop(self):
        self.flag = False

    def run(self):
        total_cash = float(api.get_balance(True)) # 보유 현금 조회
        stock_dict, i = api.get_stock_balance(True) # 보유 주식 조회
        target_buy_count = 3 # 매수할 종목 수
        buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
        bought_list = []
        for sym in stock_dict.keys():
            bought_list.append(sym)

        while self.flag:
            t_now = datetime.datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.datetime.today().weekday()
            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                api.send_message("주말이므로 프로그램을 종료합니다.")
                break
            if t_9 < t_now < t_sell:  # AM 09:00 ~ PM 03:15 : 매수

                for sym in self.symbol_list:
                    now_volpow = api.get_volume_power(sym)

                    # sell
                    if sym in stock_dict.keys() and sym in bought_list:
                        if now_volpow < 150:
                            try:
                                stock, i = api.get_stock_balance(False)
                                stock = stock[sym]
                                result = api.sell(sym,int(stock['hldg_qty']))
                                if result:
                                    stock_dict,i = api.get_stock_balance(True)
                                    bought_list.remove(sym)
                                    time.sleep(0.11)
                            except KeyError:
                                pass
                    
                    # buy
                    elif len(bought_list) < target_buy_count and not(sym in bought_list):
                        if now_volpow > 150:
                            buy_qty = 0
                            current_price = api.get_current_price(sym)
                            buy_qty = buy_amount//current_price
                            if buy_qty > 0:
                                api.send_message(f"{sym} 체결강도 150이상 {current_price} 매수를 시도합니다.")
                                result = api.buy(sym, buy_qty)
                                if result:
                                    stock_dict,i = api.get_stock_balance(True)
                                    bought_list.append(sym)
                                    time.sleep(0.11)
                if t_now.minute%30 == 0 and t_now.second < 3: 
                    api.get_stock_balance(True)
                    time.sleep(5)
            if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
                for sym, data in stock_dict.items():
                    api.sell(sym, data['hldg_qty'])
                    bought_list.remove(sym)
            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                api.send_message("장이 닫히므로 프로그램을 종료합니다.")
                evaluation = api.get_evaluation()
                myseed = float(evaluation[0]['nass_amt'])   #순자산금액
                with open('Daily Record.p','a') as recordfile:
                    recordfile.write(f"{t_now.date()}-{myseed}\n")
                break

class Mas(threading.Thread):
    def __init__(self, name=''):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.symbol_list = ["005930","035720","000660","005380","035420","003550","015760"]
        self.flag = True
    
    def stop(self):
        self.flag = False
    
    def run(self):      
        total_cash = float(api.get_balance(True)) # 보유 현금 조회
        stock_dict,i = api.get_stock_balance(True) # 보유 주식 조회
        target_buy_count = 3 # 매수할 종목 수
        buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
        bought_list = []
        for sym in stock_dict.keys():
            bought_list.append(sym)
        STOP_LOSS_RATIO = 10

        while self.flag:
            t_now = datetime.datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.datetime.today().weekday()
            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                api.send_message("주말이므로 프로그램을 종료합니다.")
                break
            if t_9 < t_now < t_exit :  # AM 09:00 ~ PM 03:15 : 매수
                for sym in self.symbol_list:
                    current_price = api.get_current_price(sym)
                    bollinger = api.get_moving_average(sym)
        
                    # sell
                    if sym in stock_dict.keys() and sym in bought_list:
                        try:
                            stock, i = api.get_stock_balance(False)
                            stock = stock[sym]
                        except:
                            pass
                        if current_price > bollinger[0]+bollinger[1]*2:
                            result = api.sell(sym,int(stock['hldg_qty']))
                            if result:
                                stock_dict,i = api.get_stock_balance(True)
                                bought_list.remove(sym)
                                time.sleep(0.11)
                    
                    # buy
                    else:
                        if len(bought_list) < target_buy_count and not(sym in bought_list):
                            if current_price < bollinger[0]-bollinger[1]*2:
                                buy_qty = 0  # 매수할 수량 초기화
                                buy_qty = buy_amount//current_price
                                if buy_qty > 0:
                                    api.send_message(f"{sym} 볼린저 밴드 하단선 접촉, {current_price} 매수를 시도합니다.")
                                    result = api.buy(sym, buy_qty)
                                    if result:
                                        stock_dict,i = api.get_stock_balance(True)
                                        bought_list.append(sym)
                                        time.sleep(0.11)
                if t_now.minute%30 == 0 and t_now.second <= 5: 
                    api.get_stock_balance(True)
                    time.sleep(5)
            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                api.send_message("장이 닫히므로 프로그램을 종료합니다.")
                evaluation = api.get_evaluation()
                myseed = float(evaluation[0]['nass_amt'])   #순자산금액
                with open('Daily Record.p','a') as recordfile:
                    recordfile.write(f"{t_now.date()}-{myseed}\n")
                break

class switch:
    def __init__(self, strategy_code=0):
        self.strategy_code = strategy_code
    
    def switchSub(sub):
        symbol = []
        for i in sub:
            symbol.append(i)
        return symbol