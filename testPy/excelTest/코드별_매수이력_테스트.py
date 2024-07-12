import pandas as pd

# 엑셀 파일 읽기
df = pd.read_excel('xlsx/history.xlsx')

print(df.to_dict())

# 동적으로 받아야 하는 값
search_code = [214420, 214421]

# 기준이 되는 'code' 컬럼에서 특정 값에 해당하는 행 찾기
for code in search_code:
    found_row = df[df['code'] == code]

# 결과 확인
def foundRow():
    if not found_row.empty:
        # buy, add_buy, partial_sale 컬럼의 값 확인
        buy_value = found_row['buy'].iloc[0]
        add_buy_value = found_row['add_buy'].iloc[0]
        partial_sale_value = found_row['partial_sale'].iloc[0]

        # 결과 출력
        print(f"buy 컬럼 값: {buy_value}")
        print(f"add_buy 컬럼 값: {add_buy_value}")
        print(f"partial_sale 컬럼 값: {partial_sale_value}")
    else:
        print("해당 코드를 가진 행이 발견되지 않았습니다.")
