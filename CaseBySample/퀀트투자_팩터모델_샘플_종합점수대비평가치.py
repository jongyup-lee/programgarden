import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import openpyxl

# KOSDAQ 종목 리스트 가져오기
df_krx = fdr.StockListing('KOSDAQ')

# 상위 30개 종목 선택 (예시)
top_30 = df_krx.sort_values(by='Marcap', ascending=False).head(30)


# 종목별 팩터 계산 (예시: P/E 비율, ROE, 모멘텀)
def calculate_factors(ticker):
    data = fdr.DataReader(ticker, '2023-01-01', '2023-12-31')
    if data.empty:
        return None

    factors = {}
    factors['P/E'] = data['Close'].iloc[-1] / (data['EPS'].mean() if 'EPS' in data.columns else 1)  # 예시 P/E 계산
    factors['ROE'] = data['ROE'].mean() if 'ROE' in data.columns else 0  # 예시 ROE 계산
    factors['Momentum'] = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]  # 모멘텀 계산
    factors['Close'] = data['Close'].iloc[-1]  # 현주가

    return factors


# 종목별 팩터 계산 및 점수화
scores = []
for idx, row in top_30.iterrows():
    ticker = row['Code']
    name = row['Name']
    factors = calculate_factors(ticker)
    if factors:
        score = 0.5 * (1 / factors['P/E']) + 0.3 * factors['ROE'] + 0.2 * factors['Momentum']  # 가중치를 적용한 점수 계산
        scores.append({'종목명': name, '티커': ticker, '점수': score, '현주가': factors['Close']})

# 결과를 데이터프레임으로 변환
scores_df = pd.DataFrame(scores)

# 점수의 표준화
mean_score = scores_df['점수'].mean()
std_score = scores_df['점수'].std()
scores_df['표준화 점수'] = (scores_df['점수'] - mean_score) / std_score


# 적정 예상 주가 계산
def calculate_fair_price(row):
    return mean_score + std_score * row['표준화 점수']


scores_df['적정 예상 주가'] = scores_df.apply(calculate_fair_price, axis=1)

# 적정 주가와 현주가 차이 계산
scores_df['적정 주가 대비 차이'] = scores_df['적정 예상 주가'] - scores_df['현주가']


# 평가치 계산
def evaluate(row):
    if row['현주가'] < row['적정 예상 주가']:
        return '저평가'
    elif row['현주가'] > row['적정 예상 주가']:
        return '고평가'
    else:
        return '적정'


scores_df['평가치'] = scores_df.apply(evaluate, axis=1)

# 점수에 따른 종목 정렬
sorted_scores_df = scores_df.sort_values(by='점수', ascending=False)
print(sorted_scores_df)

# 엑셀로 저장
sorted_scores_df.to_excel('xlsx/quant_top_30_scores_evaluation.xlsx', index=False, engine='openpyxl')
