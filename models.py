# coding: utf-8
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Logininfo(db.Model):
    
    __tablename__ = 'logininfo'

    no = db.Column(db.Integer, primary_key=True)
    try_id = db.Column(db.String(10), nullable=False)
    try_ip = db.Column(db.String(15), nullable=False)
    try_login_time = db.Column(db.DateTime, nullable=False)
    login_success = db.Column(db.String(1), nullable=False)
    reason_fail = db.Column(db.Integer)



class Orderinfo(db.Model):
    __tablename__ = 'orderinfo'

    no = db.Column(db.Integer, primary_key=True)
    order_price = db.Column(db.Integer, nullable=False)
    order_kind = db.Column(db.String(4), nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, nullable=False)
    order_str = db.Column(db.String(100), nullable=False)
    order_allprice = db.Column(db.Integer, nullable=False)



class Tradeinfo(db.Model):
    __tablename__ = 'tradeinfo'

    no = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(8), nullable=False)
    pr_account = db.Column(db.String(2), nullable=False)
    trade_start = db.Column(db.String(2))
    order_possible_cash = db.Column(db.String(45), nullable=False)
    benefit_percent = db.Column(db.Float(asdecimal=True), nullable=False)


