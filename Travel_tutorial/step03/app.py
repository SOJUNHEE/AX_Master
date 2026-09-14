import streamlit as st

st.set_page_config(page_title='세계 여행 가이드 포털', page_icon='🌏')

home_page = st.Page('view/home.py', title='홈', icon='🏠', default=True)
us = st.Page('view/us.py', title='미국', icon='🇺🇸')
cn = st.Page('view/cn.py', title='중국', icon='🇨🇳')  # view/cn.py 로 변경
jp = st.Page('view/jp.py', title='일본', icon='🇯🇵')

# 네비게이션 실행
pg = st.navigation([home_page, us, cn, jp])
pg.run()