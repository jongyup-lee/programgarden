# 판다스를 pd라는 별칭으로 사용 선언
import pandas as pd
from datetime import datetime

# FinanceDataReader를 fdr이라는 별칭으로 사용 선언
import FinanceDataReader as fdr

# 받아온 개별 데이터를 xlsx로 저장한다.
def toExcel(data, sCode):
    print("toExcel")
    data.to_excel('testXlsx/' + sCode + '.xlsx', index=True)
def getEachData(sCode):
    ea = 365
    now = datetime.now()
    df = fdr.DataReader(sCode)
    print('getEachData => df : %s | len(df) : %s' % (df, len(df)))
    if len(df) < 365:
        ea = len(df)
    return df.tail(ea)
# 삼성전자, 2017년~현재 일별 시세 받아오기
# 삼성전자의 종목 번호 '005930'
#df = fdr.DataReader('005930', "2017", "2021")
#data = fdr.DataReader('454910')
data = getEachData('454910')
#data['avgVol'] = data['Volume'].rolling(window=5).mean()
print('왜이럴까요? => data : %s | len(data) : %s' % (data, len(data)))
#toExcel(df, '005930')


print("==================================================================================")

