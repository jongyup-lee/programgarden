import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import os

# KRX stock symbol list
# stocks = fdr.StockListing('KRX') # 코스피, 코스닥, 코넥스 전체
# stocks = fdr.StockListing('KOSPI') # 코스피
stocks = fdr.StockListing('KRX') # 코스닥
# stocks = fdr.StockListing('KONEX') # 코넥스
# 가져온 데이터를 엑셀 파일로 저장
# stocks.to_excel('xlsx/krxdata.xlsx', index=False)

# 특정 시작 일을 기준으로 특정 거래 일간의 평균을 구하는 함수
# 예를 들어 0봉기준 1, 3, 6거래일전 종가 50일 평균값을 각각 구해서 50일 평균선이 상승세인지 하락세인지 확인하기 위한 함수
# sCode : 종목 코드
# ndays : 몇 일간의 값을 구할 것인지
# day : 몇 봉 전 까지의 값을 구할 것인지

finalStockDict ={}
existDict = {}

###CCI구하는 함수
def getCCI(sCode, data, ndays=50):
    # 각 코드에 해당하는 엑셀 파일을 오픈한다.
    tp = (data['High'] + data['Low'] + data['Close']) / 3
    result_cci = pd.Series((tp - tp.rolling(ndays).mean()) / (0.015 * tp.rolling(ndays).std()), name='CCI')

    return result_cci

# CCI 보조지표 발생 후 1차 조정받는 주식 선별
# 2. 10거래일 내 cci 0이하로 전환된 적이 있고
# 2-1. cci가 0이하로 전환된 적이 없으며
def adjustCheck(sCode, data):
    rtnValue = False
    cci11value = getCCI(sCode, data, 50)

    for val in range(1, 30):
        if len(cci11value) > 0:
            if cci11value[len(cci11value) - val] > 0:
                if cci11value[len(cci11value) - (val + 1)] < 0:
                    rtnValue = True
            break

    return rtnValue
def returnAverageVal(sCode, data, ndays=50, day=3):
    # 각 코드에 해당하는 엑셀 파일을 오픈한다.
    # dfValues = openXlsx(sCode)
    avrp = data
    moving_average_price = 0

    # 엑셀에서 받아온 df의 0봉 기준 ndays+day 위치부터 0봉기준 day전까지의 위치까지 계산
    for price in data[(len(data) - (ndays + day)):((len(data) - 1) - day)]:
        moving_average_price += price

    return moving_average_price / ndays

# 1. 3일 단위로 50일 평균 값을 구한다. 2ea정도
# 1-1. 현재가 > 3일전 50일 평균 가 > 6일전 50일 평균가
def upTrendCheck(sCode, data, day1=0, day2=3, day3=6):
    avr0ago = returnAverageVal(sCode, data, 50, day1)
    avr3ago = returnAverageVal(sCode, data, 50, day2)
    avr6ago = returnAverageVal(sCode, data, 50, day3)

    if avr0ago > avr3ago > avr6ago:
        return True
    else:
        return False


# 10일, 20일, 60일 등등의 평균값을 구하기 위한 fdr을 이용한 데이터 가져오기
def getLowData(sCode):
    now = datetime.now()
    df = fdr.DataReader(sCode, now.year)
    if len(df) < 365:
        df = fdr.DataReader(sCode, now.year-1, now.year)

    # ("sCode : %s" % sCode)
    # print(df)
    return df.tail(365)

def getStockName(sCode):
    return stocks[stocks['Code'] == sCode]['Name'].iloc[0]

def getRateValue(sCode, data, days=3):
    returnVal = False

    # 20일 이동평균 계산
    data['20MA'] = data['Close'].rolling(window=20).mean()
    # 볼린저 상한선
    data['upper'] = data['20MA'] + 2 * data['Close'].rolling(window=20).std()
    #print(data['upper'])

    if len(data['20MA']) > 0:
        current_price = data['Close'].iloc[-1]  # 현재가
        for i in range(-days, 0):
            # 현재가와 20일 이동평균값 비교 및 이격비율 계산
            ma_20 = data['20MA'].iloc[i]  # 20일 이동평균값
            bb_upper = data['upper'].iloc[i]

            # 이격비율 계산
            divergence_ratio = ((current_price - ma_20) / ma_20) * 100
            # 결과 출력

            # if current_price > ma_20:
            if -2 > divergence_ratio < 4:
            #if divergence_ratio < 4 and current_price > ma_20:
                returnVal = True
            else:
                returnVal = False

        stockNm = getStockName(sCode)
        # print("종목명 : %s | 이격률 : %s | 현재가 : %s | 20평균 : %s" % (stockNm, divergence_ratio, data['Close'].iloc[0], ma_20))

    if returnVal == True:
        finalStockDict.update({sCode:{'StockName':stockNm, 'Ratio':[divergence_ratio], '20MA':[ma_20], 'BBUpper':bb_upper}})

    #if existBool == True:
    #    existDict.update({sCode:{'StockName':stockNm, 'Ratio':[divergence_ratio], '20MA':[ma_20]}})


    return returnVal

def read_code02():
    # 디렉토리 내의 모든 파일에 대해 루프를 돌면서 파일명 추출
    for filename in os.listdir("xlsx"):
        if os.path.isfile(os.path.join("xlsx", filename)):
            sCode = filename.split(".")[0]
            eachStock = getLowData(sCode)
            getRateValue(sCode, eachStock, 3)

read_code02()

# 01. 마켓의 전 종목을 가져온다
# 01-01. 시가총액, 거래량으로 필터링
i = 0
stockDict = {}
print(len(stocks))
for i in range(len(stocks)):
    if stocks.iloc[i]['Marcap'] > 5000000000 and stocks.iloc[i]['Market'] != 'KONEX':
    # if stocks.iloc[i]['Marcap'] > 10000000000 and stocks.iloc[i]['Volume'] > 200000 and stocks.iloc[i]['Market'] != 'KONEX':
        stockDict.update({stocks.iloc[i]['Code']:{}})
        stockDict[stocks.iloc[i]['Code']].update({'종목명': stocks.iloc[i]['Name']})
        stockDict[stocks.iloc[i]['Code']].update({'거래량': stocks.iloc[i]['Volume']})
        stockDict[stocks.iloc[i]['Code']].update({'시가총액': stocks.iloc[i]['Marcap']})
        #print("i : %s" % i)
    i += 1

    # 보유중인 종목에 대해서는 별도의 조치가 필요함
    # 상위 조건에 부합하지 않아도 무조건 stockDict을 유지해야 한다.
    # 기 보유종목에 대해서는 거래량, 시가총액을 활용한 조건식을 대입하지 않으므로
    # 종목코드만 stockDict에 업데이트한다

print(len(stockDict))

# 02.필터링된 개별 종목의 데이터를 가져온다.
# 02-01.
for sCode in stockDict:
    eachStock = getLowData(sCode)

    condition01 = upTrendCheck(sCode, eachStock['Close'], 0, 2, 4)
    condition02 = adjustCheck(sCode, eachStock)
    condition03 = getRateValue(sCode, eachStock, 3)
    print("condition01: %s | condition02 : %s | condition03 : %s" % (condition01, condition02, condition03))

    if condition01 == True and condition02 == True and condition03 == True:
        if sCode in finalStockDict.keys():
            data =finalStockDict[sCode]
            print('======================================= 종목명 %s (%s) : ' % (finalStockDict[sCode]['StockName'], sCode))
#
            df = pd.DataFrame(data)
            df.to_excel("xlsx/"+sCode+"."+finalStockDict[sCode]['StockName']+".xlsx", index=True)

# 02.필터링된 개별 종목의 데이터를 가져온다.
# 02-01.
for sCode in existDict:
    data =existDict[sCode]
    df = pd.DataFrame(data)
    # if os.path.isfile("xlsx/"+sCode+"."+finalStockDict[sCode]['StockName']+".xlsx"):
    #     print('아 진짜 개고생이넹')
    #     os.remove("xlsx/"+sCode+"."+finalStockDict[sCode]['StockName']+".xlsx")
    df.to_excel("xlsx/"+sCode+"."+existDict[sCode]['StockName']+".xlsx", index=True)