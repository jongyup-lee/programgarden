import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
from pykiwoom.kiwoom import *
import os
import time


class Main():
    def __init__(self):
        kiwoom = Kiwoom()
        kiwoom.CommConnect(block=True)

        # 조건식을 PC로 다운로드
        kiwoom.GetConditionLoad()

        # 전체조건식 리스트 획득
        conditions = kiwoom.GetConditionNameList()

        #사용할 조건식 선별
        condition_index = conditions[0][0]
        condition_name = conditions[0][1]

        #해당 조건식으로 선별한 종목들 리스트
        codes = kiwoom.SendCondition('0101', condition_name, condition_index, 0)

        self.stocks = fdr.StockListing('KRX')
        self.stockDict = {}  # 필터 조건을 만족한 종목 딕셔너리
        self.tmpStockDict = {}  # 종목별 dataframe을 한번만 수행하도록 담아두는 딕셔너리
        self.myStockDict = {}

        self.myKiwoomConditionStockList = []
        self.myHaveStockList = []

        for code in codes:
            self.myKiwoomConditionStockList.append(code)

        #
        # self.read_code02()
        # self.getKRXStocks()

        # 키움증권 꾸러기주식 검색식 엑셀로 저장하기
        self.setKiwoomConditionStockList()
        # 보유주식 동기화할때 종종 사용하는 함수
        # self.setMyHaveStockList()

    #
    '''    
    총부채증감율 : 최근결산기의 전년대비 증감률 200% 이하
    유보율 : 최근결산 500% 이상
    '''

    def getExcelValue(self, sCode):
        print('=======================================================================')
        print('종목명 : %s(%s) ' % (self.getStockName(sCode), sCode))
        print('-----------------------------------------------------------------------')
        self.start_time = time.time()
        data = self.getStockData(sCode)

        # 20일 이동평균 계산
        data['20MA'] = data['Close'].rolling(window=20).mean()

        # 볼린저 상한선 기초데이터
        data['std'] = data['Close'].rolling(window=20).std()

        data['upper'] = data['20MA'] + 2 * data['Close'].rolling(window=20).std()
        # print(data['upper'])

        if len(data['20MA']) > 0:
            current_price = data['Close'].iloc[-1]  # 현재가
            ma_20 = data['20MA'].iloc[-1]
            std = data['std'].iloc[-1]
            bb_upper = data['upper'].iloc[-1]
            divergence_ratio = ((current_price - ma_20) / ma_20) * 100

            #return current_price, ma_20, bb_upper, divergence_ratio, std

            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            print("Execution time:", execution_time, "seconds")
            return ma_20

    def getStockName(self, sCode):
        return self.stocks[self.stocks['Code'] == sCode]['Name'].iloc[0]

    def getStockData(self, sCode):
        data = self.tmpStockDict[sCode]
        data = pd.DataFrame(data)

        return data

    def getEachData(self, sCode, days=365):
        print('getEachData - %s' % sCode)
        ea = days
        df = fdr.DataReader(sCode)
        # df.to_excel("xlsxConditions/" + sCode + ".xlsx", index=True)
        print(df)

        dfDate = df.index.to_list()
        dfOpen = df['Open'].to_list()
        dfHigh = df['High'].to_list()
        dfLow = df['Low'].to_list()
        dfClose = df['Close'].to_list()
        dfVolume = df['Volume'].to_list()
        self.tmpStockDict.update(
            {sCode: {'Date':dfDate, 'Open': dfOpen, 'High': dfHigh, 'Low': dfLow, 'Close': dfClose, 'Volume': dfVolume}})

        # if len(df) < days:
        #    ea = len(df)

    #
    # return df.tail(ea)

    def setKiwoomConditionStockList(self):
        print('setKiwoomConditionStockList')
        # self.myHaveStockList = ['000240', '000320', '000720', '001430', '001750', '001820', '002240', '002350', '003570', '003960', '004020', '005810', '005850', '006060', '006890', '007330', '007700', '009830', '009900', '011200', '012630', '018250', '018880', '020000', '025770', '026890', '026960', '028100', '028670', '029960', '030190', '031330', '033160', '034120', '034310', '035150', '035610', '036530', '039340', '039840', '042670', '045660', '049770', '049960', '050890', '051160', '052330', '052400', '056190', '064260', '069260', '071320', '071670', '073490', '078520', '081660', '083930', '084010', '089030', '089600', '089980', '097520', '101490', '104700', '110990', '137400', '138580', '138930', '144960', '161000', '172670', '178320', '187870', '194370', '206650', '211050', '211270', '213420', '214150', '230360', '234340', '241590', '260970', '263860', '285490', '287410', '294870', '298540', '298830', '300720', '319660', '322000', '335890', '370090', '372910', '381970', '417790', '418550', '425040', '439580', '448710']

        i = 0
        for sCode in self.myKiwoomConditionStockList:
            # 해당하는 종목을 모두 self.tmpStockDict에 담는다
            self.getEachData(sCode, 365)

            print('[%s / %s] 종목명 : %s' % (i, len(self.stocks), self.getStockName(sCode)))

            # 20일 평균 구하기
            ma20 = self.getExcelValue(sCode)
        i += 1


if __name__ == "__main__":
    Main()