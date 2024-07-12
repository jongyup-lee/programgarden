import pandas as pd

# 리스트 생성

buyHistory = ['050110', '109610', '290550', '001680', '047810', '079160', '036930', '019180']

# 리스트를 데이터프레임으로 변환
df1 = pd.DataFrame({'buyHistory': buyHistory})

# 엑셀 파일로 저장
#df1.to_excel('xlsx/buyHistory.xlsx', index=True)
pd.DataFrame({'buyHistory': buyHistory}).to_excel('historyXlsx/buyHistory.xlsx', index=True)