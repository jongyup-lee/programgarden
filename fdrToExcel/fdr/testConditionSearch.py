import sys
import os
import pandas as pd
import logging
import numpy as np
# FinanceDataReader를 fdr이라는 별칭으로 사용 선언
import FinanceDataReader as fdr

from datetime import datetime
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *

class ConditionSearch():

    def __init__(self):
        super().__init__()
        print("ConditionSearch")

        sCode = "001540"
        self.dataToExcel_dict = {}
        self.upgradeDict(sCode)

    ############################################################################################################
    # 매수 조건
    ############################################################################################################
    def openXlsx(self, sCode):
        if os.path.exists("../xlsx/" + sCode + ".xlsx"):
            lowdata = pd.read_excel('../xlsx/' + sCode + '.xlsx', index_col=0, engine='openpyxl')
        else:
            lowdata = None

        return lowdata

    # 이격률을 계산하여 리턴한다
    # fdr로 받아 놓은 엑셀에서 미리 한번에 값을 구하여 엑셀에 담아 놓는다
    #  : 대상 값 1
    #  : 대상 값 2
    def getDivergence_ratio(self):
        pass

    # 평균을 구하여 리턴한다.
    # data : dataframe
    # nadys : 평균을 구하고자 하는 기간
    # unit : High, Low, Close 등
    def getAverageValue(self, sCode, ndays, unit):
        print("속도 체크 1")
        df = self.openXlsx(sCode)
        print("속도 체크 2")
        df = df[unit].to_frame()
        df["ma_"+str(ndays)] = df[unit].rolling(window=20).mean()

        return df["ma_"+str(ndays)]

    # 특정 시작 일을 기준으로 특정 거래 일간의 평균을 구하는 함수
    # 예를 들어 0봉기준 1, 3, 6거래일전 종가 50일 평균값을 각각 구해서 50일 평균선이 상승세인지 하락세인지 확인하기 위한 함수
    # sCode : 종목 코드
    # ndays : 몇 일간의 값을 구할 것인지
    # day : 몇 봉 전 까지의 값을 구할 것인지
    def returnAverageVal(self, sCode, ndays=50, day=3, unit='Close'):
        print("returnAverageVal")
        # 각 코드에 해당하는 엑셀 파일을 오픈한다.
        dfValues = self.openXlsx(sCode)
        dfClose = dfValues[unit]
        moving_average_price = 0

        # 엑셀에서 받아온 df의 0봉 기준 ndays+day 위치부터 0봉기준 day전까지의 위치까지 계산
        for price in dfClose[(len(dfClose) - (ndays + day)):((len(dfClose) - 1) - day)]:
            moving_average_price += price

        return moving_average_price / ndays

    # 1. 3일 단위로 50일 평균 값을 구한다. 2ea정도
    # 1-1. 현재가 > 3일전 50일 평균 가 > 6일전 50일 평균가
    def upTrendCheck(self, sCode, day1=0, day2=2, day3=4):
        print("upTrendCheck")
        avr0ago = self.returnAverageVal(sCode, 50, day1, 'Close')
        avr3ago = self.returnAverageVal(sCode, 50, day2, 'Close')
        avr6ago = self.returnAverageVal(sCode, 50, day3, 'Close')

        if avr0ago > avr3ago > avr6ago:
            return True
        else:
            return False

    # CCI 보조지표 발생 후 1차 조정받는 주식 선별
    # 2. 10거래일 내 cci 0이하로 전환된 적이 있고
    # 2-1. cci가 0이하로 전환된 적이 없으며
    def adjustCheck(self, sCode):
        print("adjustCheck")
        returnVal = False
        cci11value = self.getCCI(sCode, 50)

        # print(cci11value)
        for val in range(1, 20):
            if cci11value[len(cci11value) - val] > 0:
                if cci11value[len(cci11value) - (val + 1)] < 0:
                    returnVal = True
                    break
            else:
                break
        return returnVal

    def getRateValue(self, sCode, cp, avrData, days=3, unit='Close'):
        print("getRateValue1")
        returnVal = False
        for i in range(-3, 0):
            print("getRateValue2 : %s" % i)

            avr = self.getAverageValue(sCode, 20, unit).iloc[i]
            # 이격비율 계산
            divergence_ratio = ((cp - avr) / avr) * 100
            # 결과 출력

            if divergence_ratio < 3 and cp > avr:
                returnVal = True
            else:
                returnVal = False
        print("현재가(%s) 와 20일 이동평균(%s) 값 간의 이격비율(%s)" % (cp, avr, divergence_ratio))

        return returnVal

    ###CCI구하는 함수
    def getCCI(self, sCode, ndays=50):
        print("getCCI")
        # 각 코드에 해당하는 엑셀 파일을 오픈한다.
        dfValues = self.openXlsx(sCode)

        tp = (dfValues['High'] + dfValues['Low'] + dfValues['Close']) / 3

        result_cci = pd.Series((tp - tp.rolling(ndays).mean()) / (0.015 * tp.rolling(ndays).std()), name='CCI')

        return result_cci

    def upgradeDict(self, sCode):
        print("upgradeDict %s " % sCode)
        navr = self.getAverageValue(sCode, 20, 'Close')
        print("upgradeDict2 %s " % sCode)
        cp = navr.iloc[-1]  # 현재가

        self.dataToExcel_dict.update({sCode: {}})  # 추가한다.

        self.dataToExcel_dict[sCode].update({'condition01': self.upTrendCheck(sCode, 0, 2, 4)}) # 당일 50일 평균가 > n일전 50일 평균 가 > nn일전 50일 평균가 결과
        self.dataToExcel_dict[sCode].update({'condition02': self.adjustCheck(sCode)}) # cci가 n일에 양수이고 n-1에 음수인 결과 => 시그널 발생 후 상승 이후 조정 받는 종목 발굴
        self.dataToExcel_dict[sCode].update({'condition03': self.getRateValue(sCode, cp, navr,3, 'Close')}) # 0봉 ~ 3봉 내에 각 종가가 각 봉기준 20일 평균가가 2%내에 있는지 확인 결과

        print(self.dataToExcel_dict)
        # 실시간으로 확인해야 할 사항
        # self.dataToExcel_dict[sCode].update({'result4': a}) # 현재가가 20일 평균보다 위에 있어야 함

if __name__ == "__main__":
    ConditionSearch()