import os
import FinanceDataReader as fdr
import pandas as pd
import time
import datetime
import numpy as np
from pykiwoom.kiwoom import *


class Main():
    def __init__(self):
        kiwoom = Kiwoom()
        kiwoom.CommConnect(block=True)

        # 조건식을 PC로 다운로드
        kiwoom.GetConditionLoad()

        # 전체조건식 리스트 획득
        conditions = kiwoom.GetConditionNameList()
        condition_index = conditions[0][0]
        condition_name = conditions[0][1]
        codes = kiwoom.SendCondition('0101', condition_name, condition_index, 0)

        print('codes : %s' % codes)

        self.stocks = {}  # KRX의 모든 종목을 가져옴
        self.stockDict = {}  # 필터 조건을 만족한 종목 딕셔너리
        self.tmpStockDict = {}  # 종목별 DataReader를 한번만 수행하도록 담아두는 딕셔너리
        self.myKiwoomConditionStockList = [] # 사용할 키움 증권의 검색식에 포함된 종목 코드 담아 둘 리스트

        for code in codes:
            #data = pd.DataFrame(data)
            self.myKiwoomConditionStockList.append(code)

        '''
        아래 
        self.setKiwoomConditionStockList() 와
        
        self.stocks = fdr.StockListing('KRX')
        self.read_excel()
        는 서로 on/off해가며 번갈아 가면서 사용하도록 한다.
        '''
        #키움증권 꾸러기주식 검색식 엑셀로 저장하기
        # self.setKiwoomConditionStockList()

        # 상위 self.setKiwoomConditionStockList()는 검색식에 포함된 종목을 가져와서
        # 엑셀로 저장하고 모두 저장이 된 이후에 self.read_excel()을 실행하여 정보를 활용하는데
        # pd.DataReader를 사용하게 되면 너무 시간이 걸려서 개발 테스트 중에는 self.setKiwoomConditionStockList()를 주석처리하고
        # 대상 종목의 엑셀 파일이 저장되어 있다는 전제하에 self.read_excel()를 바로 실행시킨다.

        #self.stocks의 용도는 종목의 이름을 가져오기 위해 사용하고 있음 (2024.07.05 현재 까지는 향후에 더 쓸일이 있겠지)
        self.stocks = fdr.StockListing('KRX')
        self.read_excel()

    '''    
    총부채증감율 : 최근결산기의 전년대비 증감률 200% 이하
    유보율 : 최근결산 500% 이상
    '''

    def returnAverageVal(self, sCode, col, data, ndays=50, day=3):
        avrp = data[col]
        moving_average_price = 0

        # 0봉 기준 ndays+day 위치부터 0봉기준 day전까지의 위치까지 계산
        for price in avrp[(len(avrp) - (ndays + day)):((len(avrp) - 1) - day)]:
            moving_average_price += price

        return moving_average_price / ndays

    def upTrendCheck(self, sCode, day1=0, day2=3, day3=6, ndays=50):
        data = self.getStockData(sCode)
        avr0ago = self.returnAverageVal(sCode, 'Close', data, ndays, day1)
        avr3ago = self.returnAverageVal(sCode, 'Close', data, ndays, day2)
        avr6ago = self.returnAverageVal(sCode, 'Close', data, ndays, day3)
        if avr0ago > avr3ago > avr6ago:
            return True
        else:
            return False

    def getExcelValue(self, sCode):
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

            return current_price, ma_20, bb_upper, divergence_ratio, std

    def getStockName(self, sCode):
        return self.stocks[self.stocks['Code'] == sCode]['Name'].iloc[0]

    def getStockData(self, sCode):
        data = self.tmpStockDict[sCode]
        data = pd.DataFrame(data)

        return data


    # def initSet(self):
    #     dfOpen = df['Open'].to_list()
    #     dfHigh = df['High'].to_list()
    #     dfLow = df['Low'].to_list()
    #     dfClose = df['Close'].to_list()
    #     dfVolume = df['Volume'].to_list()
    #     self.tmpStockDict.update(
    #         {sCode: {'Open': dfOpen, 'High': dfHigh, 'Low': dfLow, 'Close': dfClose, 'Volume': dfVolume}})

    def setKiwoomConditionStockList(self):
        self.stocks = fdr.StockListing('KRX')

        i = 1
        for sCode in self.myKiwoomConditionStockList:

            ea = 365
            df = fdr.DataReader(sCode)
            # print('[%s / %s] 종목명 : %s' % (i, len(self.myKiwoomConditionStockList), self.getStockName(sCode)))
            print('[%s/%s]' % (i, len(self.myKiwoomConditionStockList)))
            df.to_excel("xlsxTimeTestConditions/" + sCode + ".xlsx", index=True)
            i += 1

            if i == len(self.myKiwoomConditionStockList):
                self.read_excel()

    def read_excel(self):
        # cci용 디렉토리 내의 모든 파일에 대해 루프를 돌면서 파일명 추출
        for filename in os.listdir("xlsxTimeTestConditions"):
            if os.path.isfile(os.path.join("xlsxTimeTestConditions", filename)):
                cciFileCode = filename.split(".")[0]

                # ==========================================================================================
                # ==========================================================================================
                cciDF = pd.read_excel('xlsxTimeTestConditions/' + cciFileCode + '.xlsx', engine='openpyxl')
                self.tmpStockDict.update({cciFileCode:{}})
                self.tmpStockDict[cciFileCode].update({'Date':cciDF['Date'].to_list(), 'High':cciDF['High'].to_list(), 'Low':cciDF['Low'].to_list(), 'Close':cciDF['Close'].to_list()})

                crossup_signals = self.getCCI(cciFileCode)
                # ==========================================================================================
                # ==========================================================================================
                
                if self.getTodaySignalCheck(crossup_signals) == 'Today':
                    '''
                    당일 신호 1차 매수 조건
                        1-1. CCI가 시그널 발생이 당일이어야 함
                    '''
                    print('01-1. 당일 CCI 발생 - 매수 조건 부합')
                    print('01-2. 50일선이 20일선보다 위에 있을 수 있나')
                    print('01-3. 50선과 20선의 이격도가 크지 않았으면 좋겠다.')
                    print('01-4. ')
                    '''
                    당일 신호 2차 매수 조건
                        2-1. 시가가 20일 선 위에 있어야 하고
                        2-2. 20일 이동평균이 상승세여야 함
                    '''
                    current_price, ma_20, bb_upper, divergence_ratio, std = self.getExcelValue(cciFileCode)
                    print('ma_20 : %s | 당일 시가가 20 이동 평균보다 상위에 있어야 함 ' % ma_20)

                elif self.getTodaySignalCheck(crossup_signals) == 'Past':
                    print('02. 마지막 신호일 : %s' % crossup_signals["Date"].iloc[-1].date())
                    print('02-1. 발생일로부터 당일까지의 최고가를 구할수 있나')
                    print('02-2. 발생일의 시가와 최고가의 절반가를 구한다')
                    print('02-3. 현재가가 절반가보다 낮지 않고 현재가가 20일 이동평균 값보다 높아야한다.')
                    print('02-4. 현재가가 시가보다 높아야 한다')
                else:
                    print('신호발생 이력이 없습니다')


    def getCCI(self, sCode, highVal = 10000, lowVal = 5000, closeVal = 6000, ndays=50):
        print('=======================================================================')
        print(self.getStockName(sCode))
        print('-----------------------------------------------------------------------')
        self.start_time = time.time()
        rtnVal = False

        data = self.tmpStockDict[sCode]
        data = pd.DataFrame(data)

        # 신규 삽입할 데이터
        new_data = {'Date': datetime.datetime.today(), 'High': highVal, 'Low': lowVal, 'Close': closeVal}

        # DataFrame에 새로운 행 삽입
        #data.loc[len(data)] = new_data
        
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        tp_rolling_mean = tp.rolling(window=50).mean()
        mean_deviation = tp.rolling(window=50).std()

        cciData = (tp - tp_rolling_mean) / (0.015 * mean_deviation)

        data['CCI'] = cciData

        # Crossup 신호 검색
        crossup_signals = data[(data['CCI'].shift(1) < 0) & (data['CCI'] > 0)]

        # DataFrame의 마지막 행 제거
        data.drop(data.index[-1])

        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        print("Execution time:", execution_time, "seconds")
        return crossup_signals

    def getTodaySignalCheck(self, data):
        if len(data) > 0 and data["Date"].iloc[-1].date() == datetime.datetime.today().date():
            return 'Today'
        elif len(data) > 0 and data["Date"].iloc[-1].date() != datetime.datetime.today().date():
            return 'Past'
        else:
            return 'None'


if __name__ == "__main__":
    Main()