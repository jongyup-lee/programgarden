'''
### 50일 평균 값이 상향인 종목을 선정한다.

1. 3일 단위로 50일 평균 값을 구한다. 2ea정도
1-1. 현재가 > 3일전 50일 평균 가 > 6일전 50일 평균가

2-1. 15거래일 전 11거래일 전까지 0이하였던 적이 1회 이상 있고
2-2. 10거래일 내 cci 0이상으로 유지되고 있고
2-3. cci가 0이하로 전환된 적이 없으며

3. 현재가가 20일 평균가보다 높아야 함
3-1. 0봉전 3거래일 내 종가가 20일 평균가와 격차가 +- 5%내외에 근접
'''
import os
import pandas as pd
import FinanceDataReader as fdr

sCode = "000480"


# sCode : 종목코드
# ndays : 몇일간의 CCI값을 구할 것인지
def getCCI(sCode, ndays=50, day=1):
    # 각 코드에 해당하는 엑셀 파일을 오픈한다.
    dfValues = openXlsx(sCode)
    # 기간을 지정하는 라인이었으나 제거
    # data = dfValues[(len(dfValues)-(ndays+10+day)):(ndays+len(dfValues)-day)]
    tp = (dfValues['High'] + dfValues['Low'] + dfValues['Close']) / 3
    result_cci = pd.Series((tp - tp.rolling(ndays).mean()) / (0.015 * tp.rolling(ndays).std()), name='CCI')

    return result_cci
    #else:
    #    print("[getCCI] else문 self.cci_low_data : %s" % self.cci_low_data)
    #    self.getLowData(sCode)

def openXlsx(sCode):
    if os.path.exists("../../testXlsx/" + sCode + ".xlsx"):
        lowdata = pd.read_excel('../../testXlsx/' + sCode + '.xlsx', index_col=0, engine='openpyxl')
    else:
        lowdata = False

    return lowdata

# 평균값만 반환하는 함수
def getAvrValue(data, during):
    return data / during

# 특정 시작 일을 기준으로 특정 거래 일간의 평균을 구하는 함수
# 예를 들어 0봉기준 1, 3, 6거래일전 종가 50일 평균값을 각각 구해서 50일 평균선이 상승세인지 하락세인지 확인하기 위한 함수
# sCode : 종목 코드
# ndays : 몇 일간의 값을 구할 것인지
# day : 몇 봉 전 까지의 값을 구할 것인지
def returnAverageVal(sCode, ndays=50, day=3, unit='Close'):
    # 각 코드에 해당하는 엑셀 파일을 오픈한다.
    dfValues = openXlsx(sCode)
    dfClose = dfValues[unit]
    moving_average_price = 0

    # 엑셀에서 받아온 df의 0봉 기준 ndays+day 위치부터 0봉기준 day전까지의 위치까지 계산
    for price in dfClose[(len(dfClose)-(ndays+day)):((len(dfClose)-1)-day)]:
        moving_average_price += price

    return moving_average_price / ndays

# sCode : 종목코드
# ndays : 몇일간의 CCI값을 구할 것인지
# unit : 시가, 저가, 고가, 종가 등의 구분
# rate만 구하여 반환하는 함수
def getRateValue(sCode, days=-3, unit='Close'):
    returnVal = False
    df = openXlsx(sCode)
    df = df[unit].to_frame()

    # 20일 이동평균 계산
    df['20MA'] = df['Close'].rolling(window=20).mean()
    current_price = df['Close'].iloc[-1]  # 현재가


    for i in range(days, 0):
        # 현재가와 20일 이동평균값 비교 및 이격비율 계산
        ma_20 = df['20MA'].iloc[i]  # 20일 이동평균값

        # 이격비율 계산
        divergence_ratio = ((current_price - ma_20) / ma_20) * 100

        # 결과 출력
        print("현재가(%s) 와 20일 이동평균(%s) 값 간의 이격비율(%s)" % (current_price, ma_20, divergence_ratio))

        if divergence_ratio < 3 and current_price > ma_20:
            returnVal = True
        else:
            returnVal = False


    return returnVal


# 3-1. 0봉전 3거래일 내 종가가 20일 평균가와 격차가 +- 1%내외에 근접
def rateAlmost():
    pass


# CCI 보조지표 발생 후 1차 조정받는 주식 선별
# 2. 10거래일 내 cci 0이상으로 전환된 적이 있고
# 2-1. cci가 0이하로 전환된 적이 없으며
def adjustCheck(sCode):
    record = False
    prevCCIBool = False
    cci11value = getCCI(sCode, 50, 1)
    print(cci11value)
    #if cci11value[len(cci11value)-13] < 0:
    #    for cci11valuecci in cci11value[len(cci11value)-10:len(cci11value)]:
    #        if int(cci11valuecci) > 0:
    #            #print("=====================조건 2-2 양수 출현 통과 : %s" % cci11valuecci)
    #            record = True
    #        else:
    #            #print("=====================조건 2-2 음수 출현 탈락 : %s" % cci11valuecci)
    #            record = False
            #break
    for val in range(1, 50):
        print("val : %s / cci : %s" % (val, cci11value[len(cci11value)-val]))
        if cci11value[len(cci11value)-val] > 0:
            print('양수 출현')
            if cci11value[len(cci11value) - (val+1)] < 0:
                print("전날 음수였음")
                record = True
                break
        else:
            print("음수 출현 조건 안됨")
            #break

        #print("=====================조건 2-2 음수 출현 탈락 : %s" % cci11valuecci)

    return record

# 1. 3일 단위로 50일 평균 값을 구한다. 2ea정도
# 1-1. 현재가 > 3일전 50일 평균 가 > 6일전 50일 평균가
def upTrendCheck(sCode, day1=0, day2=3, day3=6):
    avr0ago = returnAverageVal(sCode, 20, day1, 'Close')
    avr3ago = returnAverageVal(sCode, 20, day2, 'Close')
    avr6ago = returnAverageVal(sCode, 20, day3, 'Close')

    if avr0ago > avr3ago > avr6ago:
        return True
    else:
        return False


condition01 = upTrendCheck(sCode, 0, 3, 6)
condition02 = adjustCheck(sCode)
condition03 = getRateValue(sCode, -3, 'Close')

if condition01:
    print("1차 조건 만족")
if condition02:
    print("2차 조건 만족")
if condition03:
    print("3차 조건 만족")

if condition01 and condition02 and condition03:
    print("모든 조건 만족 매수합시다.")