import os
import pandas as pd
import FinanceDataReader as fdr

sCode = "000210"

def getCCI(sCode, ndays=50):
    print('[getCCI] sCode : %s' % sCode)

    # 엑셀 불러온다
    if os.path.exists("testXlsx/" + sCode + ".xlsx"):
        data = pd.read_excel('testXlsx/' + sCode + '.xlsx', index_col=0, engine='openpyxl')
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        result_cci = pd.Series((tp - tp.rolling(ndays).mean()) / (0.015 * tp.rolling(ndays).std()), name='CCI')

        return result_cci[len(result_cci)-1]

cciVal = getCCI(sCode, 50)

print(cciVal)

