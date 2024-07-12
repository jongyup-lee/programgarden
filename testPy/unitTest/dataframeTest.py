import pandas as pd
df = pd.DataFrame({'A':[1,30,70],'B':[2,30,80],'C':[3,40,90]})
df = df.T

df = df.mean()
print(df)

for value in df[len(df)-len(df):len(df)]:
    print(value)