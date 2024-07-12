import pandas as pd
import os

df1 = None
df2 = None
df3 = None

# 엑셀 파일에서 데이터프레임으로 읽어오기
if os.path.isfile(os.path.join("historyXlsx", 'buyHistory.xlsx')):
    df1 = pd.read_excel('historyXlsx/buyHistory.xlsx', dtype=str)
    if df1 is not None:
        buyHistory = df1['buyHistory'].astype(str).tolist()
        print('buyHistory : %s' % buyHistory)
    else:
        # 파일을 읽는 데 문제가 있을 때의 처리
        print("Error: DataFrame is None, file may not be readable.")

if os.path.isfile(os.path.join("historyXlsx", 'addBuyHistory.xlsx')):
    df2 = pd.read_excel('historyXlsx/addBuyHistory.xlsx', dtype=str)
    if df2 is not None:
        addBuyHistory = df2['addBuyHistory'].astype(str).tolist()
        print('addBuyHistory : %s' % addBuyHistory)
    else:
        # 파일을 읽는 데 문제가 있을 때의 처리
        print("Error: DataFrame is None, file may not be readable.")

if os.path.isfile(os.path.join("historyXlsx", 'partialSalelist.xlsx')):
    df3 = pd.read_excel('historyXlsx/partialSalelist.xlsx', dtype=str)
    if df3 is not None:
        partialSalelist = df3['partialSalelist'].tolist()
        print('partialSalelist : %s' % partialSalelist)
    else:
        # 파일을 읽는 데 문제가 있을 때의 처리
        print("Error: DataFrame is None, file may not be readable.")

#print(df1)
