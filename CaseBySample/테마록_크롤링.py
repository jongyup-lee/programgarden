import requests
from bs4 import BeautifulSoup

# URL 설정
# url = 'https://finance.finup.co.kr/Lab/ThemeLog?_gl=1*1gq1ohp*_gcl_au*NjcxODQ4MzU1LjE3MTc5ODg0ODg.*_ga*ODAwNjE0MzE5LjE3MTc5ODg0ODk.*_ga_MGH4S0DLJE*MTcxODAxNjQwNy4zLjAuMTcxODAxNjQwOC41OS4wLjA.'
url = 'https://finance.finup.co.kr/Lab/ThemeLog?_gl=1*1gq1ohp*_gcl_au*NjcxODQ4MzU1LjE3MTc5ODg0ODg.*_ga*ODAwNjE0MzE5LjE3MTc5ODg0ODk.*_ga_MGH4S0DLJE*MTcxODAxNjQwNy4zLjAuMTcxODAxNjQwOC41OS4wLjA.'
# 웹 페이지 요청
response = requests.get(url)
response.raise_for_status()  # 요청이 성공했는지 확인

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)

# div id가 "treemap"인 요소 찾기
treemap_div = soup.find('div', id='treemap')

# treemap_div의 내용 출력
if treemap_div:
    print(treemap_div.prettify())
else:
    print("div id가 'treemap'인 요소를 찾을 수 없습니다.")
