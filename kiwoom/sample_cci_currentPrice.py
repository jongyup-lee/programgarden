import pandas as pd
import ta

def load_data(file_name):
    # 엑셀 파일 불러오기
    df = pd.read_excel(file_name, index_col=0)
    return df

def calculate_cci(df, window=50):
    # CCI 계산
    df['CCI'] = ta.trend.cci(df['High'], df['Low'], df['Close'], window=window)
    return df

def detect_crossup(df):
    # Crossup 시그널 계산
    df['Crossup'] = (df['CCI'] > 0) & (df['CCI'].shift(1) <= 0)
    return df

def check_signal(df):
    # 시그널이 당일 발생하는지 확인
    if df.iloc[-1]['Crossup']:
        return "당일 Crossup 시그널 발생"
    else:
        return "당일 Crossup 시그널 없음"

def update_close_price(df, current_price):
    # 실시간 현재가로 마지막 'Close' 값을 업데이트
    df.at[df.index[-1], 'Close'] = current_price
    return df

# 파일명 지정
excel_file_name = '005930.KS.xlsx'

# 데이터 로드
data = load_data(excel_file_name)

# 실시간 현재가 예제 (실제로는 실시간 데이터를 여기에 넣어야 함)
current_price = 60000  # 예제용 실시간 현재가

# 실시간 현재가로 데이터 업데이트
data = update_close_price(data, current_price)

# CCI 계산
data_with_cci = calculate_cci(data)

# Crossup 시그널 계산
data_with_signals = detect_crossup(data_with_cci)

# 시그널 확인
signal_status = check_signal(data_with_signals)
print(signal_status)
