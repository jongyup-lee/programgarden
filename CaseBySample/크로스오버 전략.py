import yfinance as yf
import pandas as pd
import numpy as np

# KRX 전체 종목 리스트 (예시: 실제로는 KRX API를 사용하여 전체 목록을 가져와야 합니다)
# 예시로 일부 KOSPI와 KOSDAQ 종목을 사용합니다
krx_tickers = ['005930.KS', '000660.KS', '035420.KS', '051910.KS', '035720.KQ', '005935.KS']

# 필터링을 위한 조건 (여기서는 예시로 코넥스 종목이 포함되지 않도록)
# 실제 코넥스 종목 리스트를 포함하여 제외하는 것이 필요합니다

# 각 종목의 데이터를 가져와서 분석
for ticker in krx_tickers:
    data = yf.download(ticker, start='2023-01-01', end='2023-12-31')
    if len(data) >= 50:
        # 이동평균 계산
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['SMA200'] = data['Close'].rolling(window=200).mean()

        # 이동평균 크로스오버 조건
        data['Signal'] = 0
        data['Signal'][50:] = np.where(data['SMA50'][50:] > data['SMA200'][50:], 1, 0)
        data['Position'] = data['Signal'].diff()

        # 현재 크로스오버 상태 확인
        if data['Position'][-1] == 1:
            print(f"{ticker}는 상승 신호가 발생했습니다.")
    else:
        print(f"{ticker}는 50일치 데이터가 부족하여 계산이 불가")
