import pandas as pd

# 데이터 생성
data = {'Ratio': 1.022579095463592, '20MA': 72855.0}

# 데이터프레임 생성
df = pd.DataFrame(data)

# 엑셀 파일로 저장
df.to_excel('xlsx/data.xlsx', index=False)  # index=False로 설정하면 인덱스를 엑셀 파일에 저장하지 않습니다.
