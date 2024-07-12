import pandas as pd

# 샘플 데이터프레임 생성
df = pd.DataFrame({'numbers': [1, 2, 3], 'letters': ['a', 'b', 'c']})

# 데이터프레임을 리스트로 변환
list_from_df = df.values.tolist()
print(list_from_df)