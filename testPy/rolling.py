import pandas as pd

# dataframe.rolling(window, min_periods=None, center=False, axis=0, win_type=None, on=None, closed=None)

# 시계열 데이터 생성
data = {'value': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
df = pd.DataFrame(data)

# 이동 평균 계산
rolling_mean = df['value'].rolling(3).mean() # 평균
rolling_max = df['value'].rolling(3).max() # 최대값
rolling_sum = df['value'].rolling(3).sum() # 총합
rolling_min = df['value'].rolling(3).min() # 최소값
rolling_median = df['value'].rolling(3).median() # 중간값
rolling_std = df['value'].rolling(3).std() # 표준편차

print(type(rolling_std))