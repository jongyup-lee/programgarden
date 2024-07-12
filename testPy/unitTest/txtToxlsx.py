import os
from datetime import datetime
import FinanceDataReader as fdr
def getLowData(sCode):
    now = datetime.now()
    df = fdr.DataReader(sCode, now.year)
    if len(df) < 600:
        df = fdr.DataReader(sCode, now.year-1, now.year)

    df = df.tail(600)
    df.to_excel('../../testXlsx/'+sCode+'.xlsx', index=True)

def txtToxlsx():
    if os.path.exists("../../testFiles/condition_stock.txt"):
        f = open("../../testFiles/condition_stock.txt", "r", encoding="utf8")

        lines = f.readlines()
        for line in lines:
            if line != "":
                ls = line.split("\t")

                stock_code = ls[0]
                stock_name = ls[1]
                stock_price = int(ls[2].split("\n")[0])
                stock_price = abs(stock_price)

                getLowData(stock_code)
        f.close()
    else:
        print("없어")

txtToxlsx()