import pandas as pd
import os

portfolio_stock_dict = {}
excel_data_dict = {}
sCode = '010690'

def read_code02():
    # 디렉토리 내의 모든 파일에 대해 루프를 돌면서 파일명 추출
    for filename in os.listdir("xlsx"):
        if os.path.isfile(os.path.join("xlsx", filename)):
            filecode = filename.split(".")[0]
            stockName = filename.split(".")[1]
            df = pd.read_excel('xlsx/' + filecode + '.xlsx', index_col=0, engine='openpyxl')
            excel_data_dict.update({filecode:{}})
            excel_data_dict[filecode].update({'StockName':stockName, 'Ratio':df['Ratio'][0], '20MA':df['20MA'][0]})

            #print('StockCode : %s | StockName : %s' %(filecode, stockName))
            if stockName != 'xlsx':
                compareCpWithRatio(filecode, 10000, 5, 9000)


            #stock_nm = self.dynamicCall("GetMasterCodeName(QString)", filecode)  # 종목코드 1개의 종목 한글명을 반환한다.
            #portfolio_stock_dict.update({filecode: {"종목명": stock_nm}})

    #print("excel_data_dict : %s" % excel_data_dict)

def compareCpWithRatio(sCode, cp, ratio, ma):
    returnVal = False
    if ratio < 4 and cp > ma:
        returnVal = True


    print('종목명 : %s | Ratio : %s | 20MA : %s' % (excel_data_dict[sCode]['StockName'], excel_data_dict[sCode]['20MA'], excel_data_dict[sCode]['Ratio']))
    return returnVal

read_code02()