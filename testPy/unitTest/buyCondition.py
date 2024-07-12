import os
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime

sCode = "000210"

def getMoving20_average_price(sCode, ndays=20):
    if os.path.exists("testXlsx/" + sCode + ".xlsx"):
        print("있어")
        lowdata = pd.read_excel('testXlsx/' + sCode + '.xlsx', index_col=0, engine='openpyxl')

        dfValues = lowdata['Close']

        moving20_average_price = 0
        for price in dfValues[100:120]:
            moving20_average_price += price

        return moving20_average_price / 20
    else:
        print("없어")
def getCCI(sCode, ndays=50):
    # 엑셀 불러온다
    if os.path.exists("testXlsx/" + sCode + ".xlsx"):
        data = pd.read_excel('testXlsx/' + sCode + '.xlsx', index_col=0, engine='openpyxl')
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        result_cci = pd.Series((tp - tp.rolling(ndays).mean()) / (0.015 * tp.rolling(ndays).std()), name='CCI')

        return result_cci[len(result_cci)-1]

def getLowData(sCode):
    now = datetime.now()
    df = fdr.DataReader(sCode, now.year)
    if len(df) < 120:
        df = fdr.DataReader(sCode, now.year-1, now.year)

    df = df.tail(120)
    df.to_excel('testXlsx/'+sCode+'.xlsx', index=True)

if 0 < getCCI(sCode, 50) and "당일 체결순간의 현재가" > getMoving20_average_price(sCode):
    print("매수조건 부합 - 매수하자")
else:
    print("매수조건에 부합하지 않음")
    print("getCCI(sCode, 50) : %s" % getCCI(sCode, 50))
    print("getMoving20_average_price(sCode) : %s" % getMoving20_average_price(sCode))