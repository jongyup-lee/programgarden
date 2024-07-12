import FinanceDataReader as fdr

print(fdr.__version__)
# KRX stock symbol list
# stocks = fdr.StockListing('KRX') # 코스피, 코스닥, 코넥스 전체
# stocks = fdr.StockListing('KOSPI') # 코스피
stocks = fdr.StockListing('KRX') # 코스닥
# stocks = fdr.StockListing('KONEX') # 코넥스
#
# # NYSE, NASDAQ, AMEX stock symbol list
# stocks = fdr.StockListing('NYSE')   # 뉴욕거래소
# stocks = fdr.StockListing('NASDAQ') # 나스닥
# stocks = fdr.StockListing('AMEX')   # 아멕스
#
# # S&P 500 symbol list
# stocks = fdr.StockListing('S&P500')
#
# # 기타 주요 거래소 상장종목 리스트
# stocks = fdr.StockListing('SSE') # 상해 거래소
# stocks = fdr.StockListing('SZSE') # 신천 거래소
# stocks = fdr.StockListing('HKEX') # 홍콩거래소
# stocks = fdr.StockListing('TSE') # 도쿄 증권거래소
# stocks = fdr.StockListing('HOSE') # 호치민 증권거래소
# 가져온 데이터를 엑셀 파일로 저장
stocks.to_excel('xlsx/krxdata1.xlsx', index=False)

print("KRX 데이터를 krxdata.xlsx 파일로 저장하였습니다.")
