import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

# 삼성전자 종목코드
stock_code = '005930'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 수집 시작일 설정 (2026년 9월 1일)
start_date = datetime.date(2026, 9, 1)

data = []
page = 1
is_collecting = True

while is_collecting:
    url = f'https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    rows = soup.select('table.type2 tr')
    valid_rows_in_page = 0
    
    for tr in rows:
        cols = tr.find_all('td')
        if len(cols) < 7:
            continue
            
        date_text = cols[0].text.strip()
        if not date_text:
            continue
            
        valid_rows_in_page += 1
        row_date = datetime.datetime.strptime(date_text, '%Y.%m.%d').date()
        
        # 9월 1일 이전 데이터는 수집 제외 및 중단
        if row_date < start_date:
            is_collecting = False
            break
            
        close_price = cols[1].text.strip().replace(',', '')
        diff = cols[2].text.strip().replace(',', '').replace('\n', '').replace('\t', '')
        open_price = cols[3].text.strip().replace(',', '')
        high_price = cols[4].text.strip().replace(',', '')
        low_price = cols[5].text.strip().replace(',', '')
        volume = cols[6].text.strip().replace(',', '')
        
        data.append([
            row_date.strftime('%Y-%m-%d'), 
            int(close_price), 
            diff, 
            int(open_price), 
            int(high_price), 
            int(low_price), 
            int(volume)
        ])

    if valid_rows_in_page == 0:
        break
        
    page += 1

# 데이터프레임 변환 및 날짜 오름차순 정렬
columns = ['날짜', '종가', '전일비', '시가', '고가', '저가', '거래량']
df = pd.DataFrame(data, columns=columns)
df = df.sort_values(by='날짜').reset_index(drop=True)

# 엑셀 파일로 저장 (openpyxl 라이브러리 필요)
file_name = 'samsung_stock_september.xlsx'
df.to_excel(file_name, index=False)
print(f"총 {len(df)}영업일 데이터 수집 완료 ('{file_name}' 저장 완료)")