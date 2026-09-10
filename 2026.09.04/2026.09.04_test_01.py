import streamlit as st
import pandas as pd
import os


raw_trade = os.path.join(os.path.dirname(__file__), '..', 'common', 'raw_trade_data.csv') #1번
# raw_trade = os.path.join(os.path.dirname(__file__), 'raw_trade_data.csv') #2번
# os.path.dirname(__file__) 작성하고 있는 파일의 기준으로  .. 방나가서 common 들어가서 csv 연다. 1번
# 같은 경로에 있을 때는 2번에 쓴다
# 실행 방법에 따라 1번과 2번 사용 해야 함


# 환율샘플 데이터
# 딕셔너리로 표만들기

exchange_data = {
    '통화' : ['USD', 'EUR', 'JYP(100엔)', 'CNY'],
    '환율(KRW)' : [1390.5, 1503.2, 930.0, 191.3],   
    '전일대비' : [5.2, -3.1, 1.0, -0.4],
}
# Python에서 숫자 리스트 안에 1,390.5와 같이 쉼표(,)를 1,000 단위 구분 기호로 사용하면, 
# 파이썬은 이를 하나의 숫자가 아닌 두 개의 별도 원소(1과 390.5)로 인식합니다.


df_exchange = pd.DataFrame(exchange_data)    #파이썬 대,소문자 구분


st.title('💱오늘의 환율 대시보드')
st.caption('아래 데이터는 실제 환율이 아닌 실습용 데이터입니다.')

st.subheader('1)환율 표 보기')
st.write('▶ st.DataFrame(상호작용 가능한 표)')
st.dataframe(df_exchange, use_container_width=True)    # False 창 크기가 데이터에 따라 고정됨
# st.dataframe은 streamlit에서 소문자로 써준다.
#use_container_width=True (스위치 ON)
#글씨가 적든 많든 상관없이, 표를 화면 가로 끝까지 시원하게 쫙 늘려서 채웁니다.
#빈 공간 없이 꽉 차 보여서 보기가 깔끔합니다.


st.write('▶ st.table(정적인 표)')
st.table(df_exchange)

st.markdown('---')

st.subheader('2) 주요 환율 카드 (st.metric)')
# st.metric(라벨, 현재값, 증감값)
   
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label='USD/KRW', value='1,450.2', delta='+5.2')
with col2:
    st.metric(label='EUR/KRW', value='1,503.3', delta='-3.1')
with col3:
    st.metric(label='JPY(100엔)/KRW', value='930.8', delta='+1.0')

st.markdown('---')

st.subheader('3)보너스: 무역 원본 데이터 미리보기')
st.write('공용 데이터 파일 raw_trade_data.csv를 읽어온 상위 5행입니다.')
#df_trade = pd.read_csv(raw_trade)
#st.dataframe(df_trade.head(5))                   #한글이 깨지면 encoding

df_trade = pd.read_csv(raw_trade, encoding='utf-8')          #글자 깨지기 않기 위해
st.dataframe(df_trade.head(5), use_container_width=True)


# import streamlit as st
# import pandas as pd
# import os

# # [1번 경로] 내 방(__file__)에서 나가서(..) -> 옆방 common 가서 -> raw_trade_data.csv 파일 찾기
# raw_trade = os.path.join(os.path.dirname(__file__), '..', 'common', 'raw_trade_data.csv') #1번
# # [2번 경로] 내 방 안에 파일이 바로 있을 때 쓰는 방법
# # raw_trade = os.path.join(os.path.dirname(__file__), 'raw_trade_data.csv') #2번

# # 가짜 환율 메모장(딕셔너리) 만들기
# # ⚠️ [발생했던 오류 1]: '환율(KRW)'에 1,390.5처럼 쉼표(,)를 쓰면 컴퓨터는 1과 390.5 두 개의 숫자로 오해해요!
# #    -> 통화는 4개인데 환율 숫자는 6개가 되어 "개수가 안 맞는다(ValueError)"며 삐쳐버립니다.
# #    -> 해결: 쉼표를 싹 빼고 1390.5로 적어줘야 합니다.
# exchange_data = {
#     '통화' : ['USD', 'EUR', 'JYP(100엔)', 'CNY'],
#     '환율(KRW)' : [1390.5, 1503.2, 930.0, 191.3],   
#     '전일대비' : [5.2, -3.1, 1.0, -0.4],
# }

# # # 메모장에 적힌 내용을 깔끔한 네모 칸 표(데이터프레임)로 변신시키기
# # df_exchange = pd.DataFrame(exchange_data)    

# # # 화면 맨 위에 커다란 제목과 작은 안내문 달기
# # st.title('💱오늘의 환율 대시보드')
# # st.caption('아래 데이터는 실제 환율이 아닌 실습용 데이터입니다.')

# # 1번 구역 제목
# st.subheader('1)환율 표 보기')
# st.write('▶ st.DataFrame(상호작용 가능한 표)')

# # st.dataframe: 마우스로 클릭하고 정렬할 수 있는 '움직이는 장난감 표' (명령어 쓸 땐 전부 소문자!)
# # use_container_width=True: 표를 화면 가로 끝까지 고무줄처럼 쫙 늘려서 꽉 채워주는 스위치 ON!
# st.dataframe(df_exchange, use_container_width=True)    

# # st.table: 마우스로 건드릴 수 없는 '종이에 인쇄된 박제 표'
# st.write('▶ st.table(정적인 표)')
# st.table(df_exchange)

# # 구분선(도화지 가로지르는 줄 긋기)
# st.markdown('---')

# # 2번 구역 제목
# st.subheader('2) 주요 환율 카드 (st.metric)')
# # st.metric: 주식이나 날씨 앱처럼 '이름 / 오늘 숫자 / 어제보다 오른 내린 점수(빨강, 파랑)'를 예쁜 네모 카드로 보여주는 도구
   
# # 화면을 세 칸(왼쪽, 가운데, 오른쪽 방)으로 쪼개기
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric(label='USD/KRW', value='1,450.2', delta='+5.2') # 1번째 칸에 미국 달러 카드 쏙 넣기
# with col2:
#     st.metric(label='EUR/KRW', value='1,503.3', delta='-3.1') # 2번째 칸에 유럽 유로 카드 쏙 넣기
# with col3:
#     st.metric(label='JPY(100엔)/KRW', value='930.8', delta='+1.0') # 3번째 칸에 일본 엔화 카드 쏙 넣기

# # 다시 줄 긋기
# st.markdown('---')

# # 3번 구역 제목
# st.subheader('3)보너스: 무역 원본 데이터 미리보기')
# st.write('공용 데이터 파일 raw_trade_data.csv를 읽어온 상위 5행입니다.')

# # ⚠️ [발생했던 오류 2]: pands.read_csv(raw_trade_data.csv)라고 쓰면 두 가지 문제가 생겨요!
# #    1. pandas 별명은 위에서 'pd'로 지어줬는데 'pands'라고 부르면 "누구세요?(NameError)"라고 물어요.
# #    2. 따옴표 없이 파일 이름을 쓰면 변수로 착각하는데, 파일 위치는 위에서 만든 'raw_trade' 변수에 들어있어요.
# #
# # pd.read_csv: 엑셀처럼 생긴 csv 파일을 읽어오기 (encoding='utf-8'은 한글 외계어로 깨지지 않게 해주는 번역 안경)
# df_trade = pd.read_csv(raw_trade, encoding='utf-8')          

# # ⚠️ [발생했던 오류 3]: df.trade.head(5)처럼 점(.)을 찍으면 컴퓨터가 헷갈려해요!
# #    -> 이름표를 위에서 'df_trade'(언더스코어)로 붙여놓고 'df.trade'(점)를 부르면 그런 이름은 없다고 에러가 납니다.
# #
# # head(5): 데이터가 100만 줄 있어도 욕심내지 말고 맨 위에서 딱 5줄만 맛보기로 보기
# st.dataframe(df_trade.head(5), use_container_width=True)