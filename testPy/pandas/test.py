import pandas as pd

# 예제 데이터프레임 생성
data = {'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e']}
df = pd.DataFrame(data)

# 'A' 열에서 값이 3인 행(row) 가져오기
filtered_row = df[df['A'] == 3]
print(filtered_row)

# 위에서 가져온 행에서 'B' 열의 값을 가져오기
if not filtered_row.empty:
    value_B = filtered_row['B'].iloc[0]
    print("A 열에서 값이 3인 행에서 B 열의 값:", value_B)
else:
    print("값이 3인 행이 없습니다.")