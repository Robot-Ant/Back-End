from datetime import datetime
from sqlalchemy import text, select
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import Session
import sqlalchemy.orm as orm

Base = declarative_base()

# 아래 3개 클래스이 return __repr__(self)는 db에 접속해서 data를 변경할때 사용

class Logininfo(Base):
    # DB table logininfo format
    __tablename__ = 'logininfo'

    no = Column(Integer, primary_key=True)
    try_id = Column(String(10), nullable=False)
    try_ip = Column(String(15), nullable=False)
    try_login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    login_success = Column(String(1), nullable=False)
    reason_fail = Column(Integer)
    def __repr__(self):
        return f"Logininfo(no={self.no!r}, try_id={self.try_id!r}, try_ip={self.try_ip!r}, try_login_time={self.try_login_time}, login_success={self.login_success}, reason_fail={self.reason_fail} "

class Orderinfo(Base):
    # DB table orderinfo format
    # order_str = 매매전략
    # order_allprice = 현재 주문한 주식의 총 가격
    # 주문할 때 DB에 저장
    __tablename__ = 'orderinfo'

    no = Column(Integer, primary_key=True)
    order_price = Column(Integer, nullable=False)
    order_kind = Column(String(4), nullable=False)
    order_qty = Column(Integer, nullable=False)
    order_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    order_str = Column(String(100), nullable=False)
    order_allprice = Column(Integer, nullable=False)
    def __repr__(self):
        return f"no={self.no}, order_price={self.order_price}, order_kind={self.order_kind}, order_qty={self.order_qty}, order_time={self.order_time}, order_str={self.order_str}, order_allprice={self.order_allprice}"

class Tradeinfo(Base):
    #DB table tradeinfo format
    #client가 조회할때마다 저장
    # order_possible_cash = 잔액
    __tablename__ = 'tradeinfo'

    no = Column(Integer, primary_key=True)
    account = Column(String(8), nullable=False)
    pr_account = Column(String(2), nullable=False)
    trade_start = Column(String(2))
    order_possible_cash = Column(String(45), nullable=False)
    benefit_percent = Column(Float(asdecimal=True), nullable=False)
    def __repr__(self):
        return f"no={self.no}, account={self.account}, pr_account={self.pr_account}, trade_start={self.trade_start}, order_possible_cash={self.order_possible_cash}, benefit_percent={self.benefit_percent}"

def getengine():
    return create_engine("mysql+mysqldb://root@127.0.0.1:3306/mydb")

def insertLogininfo(no=0, try_id='', try_ip='', login_success='', reson_fail=''):
    engine = getengine()
    try:
        with engine.connect() as conn:
            Base.metadata.create_all(engine)
            session = Session(engine)
            num = getNo(obj=Logininfo, session=session)
            no = num[0]+1
            logininfo = Logininfo(no=no, try_id=try_id, try_ip=try_ip ,login_success=login_success, reason_fail=reson_fail)
            session.flush()
            session.add(logininfo)
            session.commit()  
        return 1
    except AttributeError:
        return -1
    except Exception as e:
        print(e)

def insertOrderinfo(no=0, order_price=0, order_kind='', order_qty=0, order_time=None, order_str=''):
    order_allprice = order_price * order_qty
    engine = getengine()
    try:
        with engine.connect() as conn:
            Base.metadata.create_all(engine)
            session = Session(bind=engine)
            num = getNo(obj=Orderinfo, session=session)
            no = num[0]+1
            orderinfo = Orderinfo(no=no, order_price=order_price, order_kind=order_kind, order_qty=order_qty, order_time=order_time, order_str=order_str, order_allprice=order_allprice)
            session.flush() 
            session.add(orderinfo)
            session.commit()  
        return 1
    except AttributeError:
        return -1
    except Exception as ex:
        print(ex)

def insertTradeinfo(no=0, account='', pr_account='', trade_start='', order_possible_cash=0, benefit_percent=0.0):
    engine = getengine()
    try:
        with engine.connect() as conn:
            Base.metadata.create_all(engine)
            session = Session(bind=engine)
            num = getNo(Tradeinfo, session=session)
            no = num[0]+1
            tradeinfo = Tradeinfo(no=no, account=account, pr_account=pr_account, trade_start=trade_start, order_possible_cash=order_possible_cash, benefit_percent=benefit_percent)
            session.flush() 
            session.add(tradeinfo)
            session.commit()  
        return 1
    except AttributeError:
        return -1
    except Exception as ex:
        print(ex)

def getNo(obj, session):
    row = session.execute(select(obj.no)).all()
    if len(row) == 0:
        return (0,)
    else:    
        no = row[len(row) - 1]
        return no
