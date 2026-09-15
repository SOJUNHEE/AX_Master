# from bs4 import BeautifulSoup
# # pip install beautifulsoup4
# import requests
# import pandas as pd

# response = requests.get('https://www.google.com')

# html = response.txt

# soup = BeautifulSoup(html, 'html.parser')

# logo = soup.select_one('.naW5gc.uZekje').text
# subtitle = soup.select_one('.naW5gc.mL3MVc.DYz2A').text

# print(logo, subtitle)

# # <div class="naW5gc uZekje"><style>.uZekje{max  -height:92px;position:relative}.ESTs9d{max-height:100%;max-width:100%;object-fit:contain;object-position:center bottom;width:auto}</style><svg class="ESTs9d" aria-label="Google" height="92" role="img" viewBox="0 0 272 92" width="272" xmlns="http://www.w3.org/2000/svg"><path d="M31.32 70.33c17.65.17 29.67-11.68 29.67-29.92q.01-2.29-.43-5.08H31.2v8.76h20.6c-1.1 11.47-9.18 17.44-20.27 17.44-12.44 0-21.96-9.35-21.96-22.94 0-13.41 9.1-22.77 21.96-22.77 6.48 0 11.26 2 16.04 6.9l6.14-6.43c-5.38-6.3-13.16-9.31-22.3-9.31C13.7 6.98 0 20.27 0 38.46c0 17.4 13.25 31.7 31.32 31.87" fill="#3186FF"></path><path d="M88.2 70.33c13.2 0 22.77-9.69 22.77-23.15 0-13.2-9.35-22.98-22.77-22.98-12.7 0-22.68 9.02-22.68 22.98 0 13.33 9.43 23.15 22.68 23.15m0-8.04c-8.04 0-13.67-6.6-13.67-15.1s5.93-14.95 13.67-14.95c8.17 0 13.67 6.6 13.67 14.94 0 8.64-5.63 15.11-13.67 15.11" fill="#FC413D"></path><path d="M137.42 70.33c13.29 0 22.77-9.73 22.77-23.15 0-13.2-9.35-22.98-22.77-22.98-12.7 0-22.68 9.02-22.68 22.98 0 13.33 9.43 23.15 22.68 23.15m0-8.04c-8.04 0-13.67-6.6-13.67-15.1s5.93-14.95 13.67-14.95c8.17 0 13.67 6.6 13.67 14.94 0 8.64-5.63 15.11-13.67 15.11" fill="#FFBE00"></path><path d="M185.37 88.57q21.51 0 21.5-24.63V25.77h-8.8v5.37h-.17c-2.75-4.27-7.96-6.68-13.84-6.68-12.7 0-20.44 9.69-20.44 22.6 0 12.86 7.53 22.34 20.78 22.34 6.52 0 11.34-3.72 13.37-6.77h.3v3.94c0 8.67-4.49 13.8-12.82 13.8-5.46 0-9.1-3.01-11.77-8.05l-7.96 3.52c4.2 8.84 10.16 12.73 19.85 12.73m0-27.55c-7.74 0-12.7-5.71-12.7-14.22 0-8.2 4.92-14.13 12.75-14.13s12.65 5.5 12.65 14.09c0 8.68-5.08 14.26-12.7 14.26" fill="#3186FF"></path><path d="M222.91 8.33h-9.22v60.6h9.22z" fill="#00AF57"></path><path d="M250.17 70.25a22.1 22.1 0 0 0 19-10.54l-6.86-4.49c-3 4.2-7.1 6.6-11.72 6.6a13.6 13.6 0 0 1-11.93-7.23l30.93-13.12a20 20 0 0 0-.84-3.22c-3.69-9.48-10.12-13.8-18.8-13.8-13.24 0-22.25 9.66-22.25 23.03 0 13.67 9.47 22.77 22.47 22.77m-13.5-22.81v-.51c0-8.76 5.03-14.64 12.95-14.64 3.76 0 7.15 1.69 9.44 5.67z" fill="#FC413D"></path></svg></div>
# # <div class="naW5gc mL3MVc DYz2A" aria-level="1" role="heading"><style>.DYz2A{display:flex;flex-direction:column;justify-content:flex-end;align-items:center}.HeJfy{font-family:Arial,sans-serif,Noto Color Emoji;font-size:32px;line-height:40px;font-weight:400;margin-bottom:24px;color:var(--YLNNHc);text-align:center}.dPg0Ze{color:transparent;background-image:linear-gradient(to bottom,var(--YLNNHc) 0%,var(--YLNNHc) 20%,#408bf2 30%,#a9a8ff 50%,#a9a8ff 60%,var(--YLNNHc) 80%,var(--YLNNHc) 100%);-webkit-background-clip:text;background-clip:text;background-size:auto 700%;will-change:background-position}.wf0Hmb .dPg0Ze{animation:usernameShimmer 967ms cubic-bezier(0.2,0,0.6,1) both;animation-delay:333ms}@keyframes usernameShimmer {0%{background-position:50% 0%}100%{background-position:50% 100%}}</style><span class="HeJfy"><span class="dPg0Ze">준희</span>님, 안녕하세요. 지금 무슨 생각을 하고 계시나요?</span></div>

# import requests
# from bs4 import BeautifulSoup

# headers = {
#     'User-Agent': (
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#         'AppleWebKit/537.36 (KHTML, like Gecko) '
#         'Chrome/120.0.0.0 Safari/537.36'
#     )
# }

# # 1. response.text 로 수정
# response = requests.get('https://www.google.com', headers=headers)
# html = response.text

# soup = BeautifulSoup(html, 'html.parser')

# # 2. NoneType 체크를 포함한 안전한 요소 탐색
# logo_tag = soup.select_one('.naW5gc.uZekje svg')
# subtitle_tag = soup.select_one('.naW5gc.mL3MVc.DYz2A')

# logo = logo_tag.get('aria-label') if logo_tag else '로고를 찾을 수 없음'
# subtitle = subtitle_tag.text.strip() if subtitle_tag else '자막/문구를 찾을 수 없음'

# print(logo, subtitle)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl



data = []

for i in range(1,5):
    response = requests.get(f'https://startcoding.pythonanywhere.com/basic?page={i}')
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('.product')

                # print(f"가져온 상품개수 : {len(items)}개 \n" + "-"*30)
    for item in items:
        category = item.select_one('.product-category').text #카테고리
        category_name = item.select_one('.product-name').text #상품명
        category_link = item.select_one('.product-name > a').attrs['href'] #상품 상제페이지 링크 부등호의 의미
        price = item.select_one('.product-price').text.split('원')[0].replace(',','') #가격
        data.append([category, category_name, category_link, price])
        print(category, category_name, category_link, price)

df = pd.DataFrame(data, columns=['카테고리', '상품명', '상세페이지링크', '가격'])
df.to_excel('data.xlsx', index=False)