import os
import pandas as pd
import FinanceDataReader as fdr

from datetime import datetime

code = '024910'


def getLowData(sCode):
    now = datetime.now()
    df = fdr.DataReader(sCode, now.year)
    if len(df) < 120:
        df = fdr.DataReader(sCode, now.year - 1, now.year)

    df.tail(120)
    df.to_excel('xlsx/' + sCode + '.xlsx', index=True)

getLowData(code)