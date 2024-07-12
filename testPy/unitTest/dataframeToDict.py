import pandas as pd

df = pd.DataFrame([['철수',16,'Seoul'],
                   ['영희',20,'Busan'],
                   ['희철',18,'Seoul']],
                  columns = ['Name','Age','City'])

#print(df.to_dict())
i = 0
for code in range(len(df)):
    #df['이름'] = df['Name']
    testDict=df.to_dict()
    print(testDict)
    i += 1