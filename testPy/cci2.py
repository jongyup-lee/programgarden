import pandas as pd
import numpy as np

def CCI(data, ndays):
    TP = (data['High'] + data['Low'] + data['Close']) / 3
    CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.015* TP.rolling(ndays).std()), name='CCI')

    CCI.to_excel('New Excel.xlsx')
    return CCI

#함수 실행
#np.random.seed(0)
#data = pd.DataFrame({'hight':100, 'low':10, 'close':50})

data = pd.read_excel("samsung.xlsx", index_col=0, engine='openpyxl')

cci = CCI(data, 50) #50일간의 편차를 구한다
print (type(cci))
print(cci[int(len(cci))-1])

# Series는 list 또는 dict 타입으로 변환해서 사용할 수 있다