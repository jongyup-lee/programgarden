import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
from pykiwoom.kiwoom import *
import os
import time
from openpyxl import load_workbook

class Main():
    def __init__(self):
        print('Main')
        kiwoom = Kiwoom()
        kiwoom.CommConnect(block=True)

        #조건식을 PC로 다운로드
        kiwoom.GetConditionLoad()

        #전체조건식 리스트 획득
        conditions = kiwoom.GetConditionNameList()
        # print('conditions : %s' % conditions)

        condition_index = conditions[0][0]
        condition_name = conditions[0][1]
        # print(condition_name)
        codes = kiwoom.SendCondition('0101', condition_name, condition_index, 0)

        self.stocks = fdr.StockListing('KRX')
        self.stockDict = {} # 필터 조건을 만족한 종목 딕셔너리
        self.tmpStockDict = {} # 종목별 dataframe을 한번만 수행하도록 담아두는 딕셔너리
        self.myStockDict = {}

        self.myKiwoomConditionStockList = []
        self.myHaveStockList = []

        for code in codes:
            self.myKiwoomConditionStockList.append(code)


        #
        #보유주식 동기화할때 종종 사용하는 함수
        self.setMyHaveStockList()

        #기존 서칭 주식 신규 세팅
        #self.read_code02()

        #키움증권 꾸러기주식 검색식 엑셀로 저장하기
        #self.setKiwoomConditionStockList()
#
    '''    
    총부채증감율 : 최근결산기의 전년대비 증감률 200% 이하
    유보율 : 최근결산 500% 이상
    '''

    def returnAverageVal(self, sCode, col, data, ndays=50, day=3):
        # print('returnAverageVal')
        avrp = data[col]
        moving_average_price = 0

        # 0봉 기준 ndays+day 위치부터 0봉기준 day전까지의 위치까지 계산
        for price in avrp[(len(avrp) - (ndays + day)):((len(avrp) - 1) - day)]:
            moving_average_price += price

        return moving_average_price / ndays

    def upTrendCheck(self, sCode, day1=0, day2=3, day3=6, ndays=50):
        # print('upTrendCheck')
        data = self.getStockData(sCode)
        avr0ago = self.returnAverageVal(sCode, 'Close', data, ndays, day1)
        avr3ago = self.returnAverageVal(sCode, 'Close', data, ndays, day2)
        avr6ago = self.returnAverageVal(sCode, 'Close', data, ndays, day3)
        if avr0ago > avr3ago > avr6ago:
            return True
        else:
            return False

    def downTrendCheck(self, sCode, day1=0, day2=3, day3=6, ndays=50):
        # print('downTrendCheck')
        data = self.getStockData(sCode)
        avr0ago = self.returnAverageVal(sCode, 'Close', data, ndays, day1)
        avr3ago = self.returnAverageVal(sCode, 'Close', data, ndays, day2)
        avr6ago = self.returnAverageVal(sCode, 'Close', data, ndays, day3)
        print('[%s] avr0ago : %s / avr3ago : %s / avr6ago : %s' % (sCode, avr0ago,avr3ago,avr6ago))
        if avr0ago > avr3ago > avr6ago:
            return True
        else:
            return False
    
    def getStockName(self, sCode):
        return self.stocks[self.stocks['Code'] == sCode]['Name'].iloc[0]

    def getStockData(self, sCode):
        data = self.stockDict[sCode]
        data = pd.DataFrame(data)

        return data

    def getEachData(self, sCode, days=365):
        ea = days
        df = fdr.DataReader(sCode)

        dfDate = df.index.to_list()
        dfOpen = df['Open'].to_list()
        dfHigh = df['High'].to_list()
        dfLow = df['Low'].to_list()
        dfClose = df['Close'].to_list()
        dfVolume = df['Volume'].to_list()
        self.stockDict.update({sCode:{'Date':dfDate, 'Open':dfOpen, 'High':dfHigh, 'Low':dfLow, 'Close':dfClose, 'Volume':dfVolume}})

        #if len(df) < days:
        #    ea = len(df)
#
        #return df.tail(ea)

    def read_code02(self):
        # print('read_code02')
        # 디렉토리 내의 모든 파일에 대해 루프를 돌면서 파일명 추출
        for filename in os.listdir("xlsx"):
            if os.path.isfile(os.path.join("xlsx", filename)):
                sCode = filename.split(".")[0]
                sName = filename.split(".")[1]
                # print('=======================================================================')
                self.start_time = time.time()
                # print('-----------------------------------------------------------------------')
                # print('sCode : %s' % sCode)

                # 오늘 날짜 구하기
                today = datetime.datetime.today().strftime('%Y-%m-%d')
                # finance_datareader를 사용하여 오늘의 데이터를 불러오기
                #data = fdr.DataReader(sCode)
                #finalData = data.tail(1)
                #print('finalData:%s' % finalData)
                ## 새로운 행 생성
                #new_row = {
                #    'Date': finalData.index[0],
                #    'Open': finalData['Open'][0],
                #    'High': finalData['High'][0],
                #    'Low': finalData['Low'][0],
                #    'Close': finalData['Close'][0],
                #    'Volume': finalData['Volume'][0],
                #    'Change': finalData['Change'][0]
                #}
                #print('new_row : %s' % new_row)
                ## 엑셀 파일 경로
                #excel_file = 'xlsx/'+sCode+'.'+sName+'.xlsx'
                ## 엑셀 파일 로드
                #wb = load_workbook(excel_file)
                ## 해당 시트 선택
                #ws = wb.active
                ## 행 추가
                ##ws.append(new_row.values())
                #ws.append(list(new_row.values()))
                ## 엑셀 파일 저장
                #wb.save(excel_file)


                self.getEachData(sCode)
                data = self.stockDict[sCode]
                df = pd.DataFrame(data)
                df.tail(365).to_excel("xlsx/"+sCode+"."+sName+".xlsx", index=True)
#
                self.end_time = time.time()
                execution_time = self.end_time - self.start_time
                # print("Execution time:", execution_time, "seconds")



    def setKiwoomConditionStockList(self):
        # print('setKiwoomConditionStockList')

        i = 0
        for sCode in self.myKiwoomConditionStockList:
            self.getEachData(sCode, 365)

            condition06 = self.downTrendCheck(sCode, 0, 3, 6, 50)
            condition07 = self.downTrendCheck(sCode, 0, 3, 6, 20)

            if condition06 == True and condition07 == True:
                print('[%s / %s] 종목명 : %s' % (i, len(self.myKiwoomConditionStockList), self.getStockName(sCode)))

                data = self.stockDict[sCode]
                df = pd.DataFrame(data)
                df.to_excel("xlsx/" + sCode + "." + self.getStockName(sCode) + ".xlsx", index=True)
            i += 1

    # 'KRX' 전주식 정보와 KONEX를 제외한 KRX 주식 정보를 구하여 self.stockDict에 담는다.
    def setMyHaveStockList(self):
        # print('setMyHaveStockList')
        self.myHaveStockList = ['001440','011200']

        i = 0
        for sCode in self.myHaveStockList:
            self.getEachData(sCode, 365)
            # print('[%s / %s] 종목명 : %s' % (i, len(self.stocks), self.getStockName(sCode)))

            data = self.stockDict[sCode]
            df = pd.DataFrame(data)
            df.to_excel("xlsx/" + sCode + "." + self.getStockName(sCode) + ".xlsx", index=True)
    # if i == 1:
    #    break
    #if i == 1:
    #    break

if __name__ == "__main__":
    Main()