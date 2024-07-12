import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import os


class Main():
    def __init__(self):
        self.stocks = {}  # KRX의 모든 종목을 가져옴
        self.stockDict = {}  # 필터 조건을 만족한 종목 딕셔너리
        self.tmpStockDict = {}  # 종목별 dataframe을 한번만 수행하도록 담아두는 딕셔너리
        self.myStockDict = {}

        #self.read_code02()
        self.getKRXStocks()
        self.filterStocks()

    '''    
    [일]0봉전 5봉 평균거래량 10000이상 999999999이하
    기간내 등락봉수 : [일]0봉전 100봉이내 1봉 상승발생
    주가범위: 0일전 종가가 1000이상 50000 이하
    체결강도 100.0이상 1000.0이하
    주가비교 : [일]1봉전 종가 < 0봉전 종가
    시가총액“ 현재가기준 100십억원 이상
    총부채증감율 : 최근결산기의 전년대비 증감률 200% 이하
    유보율 : 최근결산 500% 이상
    '''

    def getEachData(self, sCode, days=365):
        ea = days
        df = fdr.DataReader(sCode)
        dfOpen = df['Open'].to_list()
        dfHigh = df['High'].to_list()
        dfLow = df['Low'].to_list()
        dfClose = df['Close'].to_list()
        dfVolume = df['Volume'].to_list()
        self.tmpStockDict.update(
            {sCode: {'Open': dfOpen, 'High': dfHigh, 'Low': dfLow, 'Close': dfClose, 'Volume': dfVolume}})

        #if len(df) < days:
        #   ea = len(df)
#
        #return df.tail(ea)

    # 코드의 종목 이름을 가져온다.
    def getStockName(self, sCode):
        return self.stocks[self.stocks['Code'] == sCode]['Name'].iloc[0]

    def getStockData(self, sCode):
        data = self.tmpStockDict[sCode]
        data = pd.DataFrame(data)

        return data
    # 02. 기간내 등락봉수 : [일]0봉전 100봉이내 1봉 상승발생
    def condition02(self, sCode):
        rtnVal = False
        data = self.getStockData(sCode)
        compareData = data.tail(100)

        if any(compareData['Close'] > compareData['Open']):
            rtnVal = True

        return rtnVal

    # [일]0봉전 5봉 평균거래량 10000이상 999999999이하
    def condition01(self, sCode, start, end=5):
        rtnVal = False
        data = self.getStockData(sCode)

        data['avgVol'] = data['Volume'].rolling(window=end).mean()

        if 10000 < data['avgVol'].iloc[-1] < 999999999:
            rtnVal = True
#
        return rtnVal

    # KRX의 모든 종목을 가져옴
    def getKRXStocks(self):
        self.stocks = fdr.StockListing('KRX')
        #self.stocks.to_excel("xlsx/krx.xlsx", index=True)
        #print(self.stocks)

    def filterStocks(self):
        i = 0
        for i in range(len(self.stocks)):
            if (self.stocks.iloc[i]['Market'] == 'KOSDAQ' or self.stocks.iloc[i]['Market'] == 'KOSPI'):
                if self.stocks.iloc[i]['Dept'] in ['우량기업부','기술성장기업부','중견기업부','벤처기업부','']:
                    sCode = self.stocks.iloc[i]['Code']
                    self.getEachData(sCode, 365)

                    rslt01 = self.condition01(sCode, 0, 5)
                    #rslt02 = self.condition02(sCode)

                    if rslt01 == True:
                        print(sCode)





if __name__ == "__main__":
    Main()