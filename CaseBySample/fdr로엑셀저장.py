import FinanceDataReader as fdr
import pandas as pd

# KRX 전체 종목 리스트 가져오기
krx = fdr.StockListing('KRX')

# 코스닥 종목 제외
krx_no_kosdaq = krx[krx['Market'] != 'KOSDAQ']

# 엑셀 파일로 저장
output_path = 'xlsx/KRX_no_KOSDAQ.xlsx'
krx_no_kosdaq.to_excel(output_path, index=False)

print(f"엑셀 파일로 저장되었습니다: {output_path}")
