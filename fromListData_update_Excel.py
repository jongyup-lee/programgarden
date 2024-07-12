# ==============================================================
# 관심종목을 엑셀화 시킨 후 자동 매매를 실행 할 경우
# 보유종목은 관심종목에 해당하지 않을 수 있음
# 이 경우 엑셀화 되지 않은 보유 종목을 엑세스 하려고 하는 과정이 발생
# 오류가 발생하게 되므로 본 파일을 수행하여 보유 종목도 엑셀화하는 과정을 선행해야 함
# ==============================================================

import pandas as pd

# 업데이트할 데이터
buyHistory = ['001440', '232140']

# 엑셀 파일 경로
excel_file = 'historyXlsx/buyHistory.xlsx'

# 기존 데이터 불러오기
try:
    existing_data = pd.read_excel(excel_file)
except FileNotFoundError:
    # 파일이 없을 경우 새로운 DataFrame 생성
    existing_data = pd.DataFrame(columns=['buyHistory'])

existing_data_list = existing_data['buyHistory'].tolist()

new_list = [str(element) for element in buyHistory]
# 중복된 데이터 제거 후 기존 데이터에 새로운 데이터 추가
new_list = list(set(existing_data_list + new_list))

# 리스트를 데이터프레임으로 변환
df1 = pd.DataFrame({'buyHistory': new_list})

# 업데이트된 데이터를 엑셀 파일에 저장
df1.to_excel(excel_file, index=True)
