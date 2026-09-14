import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title='세계 여행 가이드 포털', page_icon='🌏', layout='centered')

# 사이드바 라디오 버튼 메뉴
menu = st.sidebar.radio('메뉴', ['홈', '미국', '중국', '일본'])

# 메뉴별 화면 구성
if menu == '홈':
    st.title('🌏 세계 여행 가이드 포털')
    st.subheader('대한민국 (Republic of Korea)')
    st.write('''
    아름다운 사계절과 유구한 역사, 그리고 현대적인 K-컬처가 공존하는 대한민국에 오신 것을 환영합니다!
    사이드바에서 원하는 국가를 선택하여 각국의 여행 정보와 공식 관광 사이트를 확인해보세요.
    ''')

elif menu == '미국':
    st.title('🇺🇸 미국 여행 가이드')
    st.subheader('미합중국 (United States of America)')
    st.write('''
    광활한 대자연의 국립공원부터 뉴욕, 로스앤젤레스 같은 세계적인 대도시까지 
    다양한 문화와 볼거리를 즐길 수 있는 여행지입니다.
    ''')
    # 새 탭으로 열리는 공식 관광청 링크 버튼
    st.link_button('미국 공식 관광청 바로가기 (GoUSA)', 'https://www.gousa.or.kr/')

elif menu == '중국':
    st.title('🇨🇳 중국 여행 가이드')
    st.subheader('중화인민공화국 (People\'s Republic of China)')
    st.write('''
    만리장성과 자금성 등 유구한 역사를 간직한 유적지와 
    장자제(장가계), 구채구와 같은 웅장하고 신비로운 자연경관을 만날 수 있습니다.
    ''')
    # 새 탭으로 열리는 공식 관광청 링크 버튼
    st.link_button('중국 국가여유국 공식 사이트 바로가기', 'https://www.travelchina.org.cn/')

elif menu == '일본':
    st.title('🇯🇵 일본 여행 가이드')
    st.subheader('일본 (Japan)')
    st.write('''
    가까운 거리, 다채로운 미식 탐방, 온천 휴양, 그리고 전통과 현대가 어우러진 
    도쿄, 오사카, 교토 등 매력적인 도시들이 가득합니다.
    ''')
    # 새 탭으로 열리는 공식 관광청 링크 버튼
    st.link_button('일본 정부관광국(JNTO) 바로가기', 'https://www.japan.travel/ko/kr/')