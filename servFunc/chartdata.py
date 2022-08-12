from flask import Blueprint
from datetime import datetime, timedelta
blue_chart = Blueprint('chartdata', __name__, url_prefix='/chart')

@blue_chart.route('/assetvolatility')
def getAssetvolatility():
    nowTime = datetime.now()
    returnDate = calDate(now=nowTime)
    returnAsset = []
    tempAsset = []
    templine = ''
    with open('Daily Record.p','r') as file:
        while True:
            line = file.readline()
            if line == '':
                break
            temp = line.split('-')
            temp[3] = temp[3].rstrip('\n')
            if line != templine:
                templine = line
                tempAsset.append(temp[3])
                returnAsset = tempAsset[::-1]
    res = dict({'title':'자산 변화 차트', 'date':returnDate, 'asset':returnAsset})
    return res

def calDate(now):
    datelist = []
    now = now.today()
    for i in range(6,-1,-1):
        tmpDate = now - timedelta(days=i)
        datelist.append(f"{tmpDate.month}/{tmpDate.day}")
    return datelist
