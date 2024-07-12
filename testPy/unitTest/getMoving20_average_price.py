import os
import pandas as pd
import FinanceDataReader as fdr

sCode = "000210"


def getMoving20_average_price(sCode, ndays=20):
    if os.path.exists("testXlsx/" + sCode + ".xlsx"):
        print("있어")
        lowdata = pd.read_excel('testXlsx/' + sCode + '.xlsx', index_col=0, engine='openpyxl')

        dfValues = lowdata['Close']
        print("dfValues : %s / %s : " % (dfValues, type(dfValues)))

        moving20_average_price = 0
        for price in dfValues[100:120]:
            moving20_average_price += price

        return moving20_average_price / 20
    else:
        print("없어")

print("getMoving20_average_price : %s" % getMoving20_average_price(sCode))