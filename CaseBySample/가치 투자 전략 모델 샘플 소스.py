import pandas as pd
import yfinance as yf

# KRX 전체 종목 리스트 가져오기 (예시: KOSPI와 KOSDAQ 일부 티커)
krx_tickers = ['005930.KS', '000660.KS', '035420.KS', '051910.KS', '035720.KQ', '005935.KS']

# 가상의 KRX 종목 데이터 생성 (각 리스트의 길이를 동일하게 맞춤)
data = {
    'Ticker': krx_tickers,
    'Price': [70000, 150000, 130000, 270000, 120000, 71000],
    'Earnings': [5000, 12000, 10000, 15000, 8000, 4900],  # 주당 순이익 (EPS)
    'Book Value': [50000, 100000, 90000, 200000, 70000, 51000],  # 주당 순자산 (BVPS)
    'Market': ['KOSPI', 'KOSPI', 'KOSPI', 'KOSPI', 'KOSDAQ', 'KOSPI'],
    'Preferred Stock': [False, False, False, False, False, True],
    'Trading Halted': [False, False, False, False, False, False],
    'SPAC': [False, False, False, False, False, False],
    'Delisting': [False, False, False, False, False, False],
    'Investment Warning': [False, False, False, False, False, False],
    'ETF': [False, False, False, False, False, False],
    'Management Stock': [False, False, False, False, False, False]
}

# 데이터프레임 생성
df = pd.DataFrame(data)

# 필터링 조건 적용
filtered_df = df[
    (df['Market'] != 'KONEX') &
    (df['Preferred Stock'] == False) &
    (df['Trading Halted'] == False) &
    (df['SPAC'] == False) &
    (df['Delisting'] == False) &
    (df['Investment Warning'] == False) &
    (df['ETF'] == False) &
    (df['Management Stock'] == False)
]

# P/E Ratio와 P/B Ratio 계산
filtered_df['P/E Ratio'] = filtered_df['Price'] / filtered_df['Earnings']
filtered_df['P/B Ratio'] = filtered_df['Price'] / filtered_df['Book Value']

# 가치주 선정 기준 설정 (예: P/E < 20, P/B < 3)
value_stocks = filtered_df[(filtered_df['P/E Ratio'] < 20) & (filtered_df['P/B Ratio'] < 3)]

# 결과 출력
print("Value Stocks:")
print(value_stocks[['Ticker', 'Price', 'P/E Ratio', 'P/B Ratio']])
