import streamlit as st

# streamlit run 2026.09.03_test.py 실행하는 방법 터미널 cmd 입력

# st.title('내용') 은 페이지에서 가장 크고 굵은 제목을 만든다(h1 느낌)
# ctrl+c 브레이크 걸 수 있음

st.title('무역데이터📅 부트캠프 자기소개')

# st.header('내용')은 title보다 한단계 작은 큰제목(h2 느낌) ,  윈도우 + 마침표 = 이모지
st.header('안녕하세요! Streamlit으로 만든 첫 페이지입니다.')

# st.subheader('내용') header보다 한단계 작은 큰제목(h3 느낌)
st.subheader('오늘 배운 것 : 텍스를 화면에 예쁘게 보여주는 방법')

# st.text('내용') 꾸밈이 전혀 없는 순수 텍스트를 그대로 출력
st.text('st.text 로 출력한 문장입니다, 줄을 바꾸거나 굵게 등이 서식이 적용되지 않는다.')

# caption('내용') 아주 작은 글씨로 보조 설명을 넣을 때
st.caption('이 문장은 st.caption으로 작성한 작은 보조 설명')



# st.markdown('') """ 마크다운 문법: 진하게 쓰거나 기울임(**,***), 목록 """    (shift+alt+a)
st.markdown('---')

st.markdown(
    '''
    ### 📌마크다운으로 작성한 자기소개
    - **이름** : 홍길동
    - **관심분야** : *데이터분석*, 무역데이터시각화
    - **목표** : 나만의 대시보드 만들기
    - 참고 링크 : [네이버]('https://www.naver.com)
    '''
)

st.markdown('---')

st.subheader('오늘 배운 한줄 코드')

# st.code(code로 보임)
st.code(
    '''
    st.title('hello Streamlit!')

'''
)





