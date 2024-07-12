import pandas as pd

def CCI(df):
    df['pt'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['sma'] = df['pt'].rolling(20).mean()
    df['mad'] = df['pt'].rolling(20).apply(lambda x: pd.Series(x).mad())
    df['CCI'] = (df['pt'] - df['sma']) / (0.015 * df['mad'])

    df.to_excel('New Excel.xlsx')
    return df

df = pd.read_excel("samsung.xlsx", index_col=0, engine='openpyxl')
df = CCI(df)

print(df)