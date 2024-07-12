import pandas as pd

# 예시 데이터 생성
data = {
    'date': pd.date_range(start='2021-01-01', periods=30),
    'high': [i+1 for i in range(30)],
    'low': [i-1 for i in range(30)],
    'close': [i for i in range(30)]
}


# CCI 계산 함수
def compute_cci(df, window=20, constant=0.015):
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    sma = typical_price.rolling(window=window).mean()
    mean_deviation = (typical_price - sma).abs().rolling(window=window).mean()
    cci = (typical_price - sma) / (constant * mean_deviation)
    return cci

# CCI 계산 및 결과 출력
df['CCI'] = compute_cci(df)
print(df.tail(10))