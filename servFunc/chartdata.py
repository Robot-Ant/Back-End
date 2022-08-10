from flask import Blueprint
from datetime import datetime, timedelta
blue_chart = Blueprint('chartdata', __name__, url_prefix='/chart')

@blue_chart.route('/assetvolatility')
def getAssetvolatility():
    nowTime = datetime.now()
    returnDate = calDate(now=nowTime)
    returnAsset = [424362340, 423431630, 416425430, 461829440, 400029320, 390249130, 300495120]
    res = dict({'title':'자산 변화 차트', 'date':returnDate, 'asset':returnAsset})
    return res

def calDate(now):
    datelist = []
    now = now.today()
    for i in range(6,-1,-1):
        tmpDate = now - timedelta(days=i)
        datelist.append(f"{tmpDate.month}/{tmpDate.day}")
    return datelist
