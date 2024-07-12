import pandas as pd
import numpy as np
import yfinance as yf

# 인텔리안테크 종목 데이터 가져오기
ticker = 'INTC'
stock_data = yf.download(ticker, start='2023-01-01', end='2024-01-01')
print("stock_data %s :" % stock_data)

# CCI(50) 계산
def calculate_CCI(data, window):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    mean_deviation = typical_price.rolling(window=window).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    cci = (typical_price - typical_price.rolling(window=window).mean()) / (0.015 * mean_deviation)
    return cci

# 인텔리안테크 종목의 CCI(50) 계산
stock_data['CCI_50'] = calculate_CCI(stock_data, 50)

# Crossup(CCI(50), 0) 계산
crossup = (stock_data['CCI_50'] > 0) & (stock_data['CCI_50'].shift(1) <= 0)

# Crossup(CCI(50), 0)이 True인 날짜 출력
crossup_dates = stock_data[crossup].index
print("Crossup(CCI(50), 0)이 발생한 날짜:")
print(crossup_dates)
