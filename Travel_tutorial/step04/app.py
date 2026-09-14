import streamlit as st

st.set_page_config(page_title='세계 여행 가이드 포털', page_icon='🌏', layout='wide')

# 파일 경로 및 국기 이모지 수정
home_page = st.Page('view/home.py', title='홈', icon='🏠', default=True)
us_page = st.Page('view/us.py', title='미국', icon='🇺🇸')
jp_page = st.Page('view/jp.py', title='일본', icon='🇯🇵')
cn_page = st.Page('view/cn.py', title='중국', icon='🇨🇳')

# 네비게이션 실행
pg = st.navigation([home_page, us_page, jp_page, cn_page])
pg.run()