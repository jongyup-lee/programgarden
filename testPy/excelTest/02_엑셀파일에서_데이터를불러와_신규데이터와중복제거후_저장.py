import pandas as pd

# 업데이트할 데이터
buyHistory = ['036640', '050110', '096530', '158430']

# 엑셀 파일 경로
excel_file = 'historyXlsx/buyHistory.xlsx'

# 기존 데이터 불러오기
try:
    existing_data = pd.read_excel(excel_file)
except FileNotFoundError:
    # 파일이 없을 경우 새로운 DataFrame 생성
    existing_data = pd.DataFrame(columns=['buyHistory'])

existing_data_list = existing_data['buyHistory'].tolist()

# 중복된 데이터 제거 후 기존 데이터에 새로운 데이터 추가
new_list = list(set(existing_data_list + buyHistory))
new_list = [str(element) for element in buyHistory]

# 리스트를 데이터프레임으로 변환
df1 = pd.DataFrame({'buyHistory': new_list})

# 업데이트된 데이터를 엑셀 파일에 저장
df1.to_excel(excel_file, index=True)
