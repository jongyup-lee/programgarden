import pandas as pd

# 예시로 가상의 KRX 데이터프레임을 생성합니다.
data = {
    'Stock': ['A', 'B', 'C'],
    'Amount': [965536000000.12345, 123456789012.34567, 9876543210.98765]
}

krx_df = pd.DataFrame(data)

# Amount 컬럼의 출력 형식을 설정합니다.
pd.set_option('display.float_format', '{:.2f}'.format)

# 엑셀 파일로 데이터프레임을 저장합니다.
krx_df.to_excel('krx_data.xlsx', index=False)
