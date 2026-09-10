
# 설문조사 앱
# 전송버튼, 체크박스, 라디오단추, 셀렉트박스, 멀티셀렉트박스(드롭다운), 슬라이더, 텍스트입력창
# 위젯이라 표현한다.

import streamlit as st

st.title('✏️ 미니 선호도 조사')
st.caption("위젯을 조작하면 화면 아래 '실시간 응답 요약'이 바로 바뀝니다.")

st.markdown('---')

# 1) 텍스트 입력 위젯 : key 를 지정해서 다른 위젯과 이름이 겹치지 않게 한다. 단일1줄
name = st.text_input('1) 이름을 입력하세요.', value='홍길동', key='widget_name')

# 2) 슬라이더 위젯 : 최소/최대/기본값 순서대로 지정해서 숫자로 선택하게 한다.
age = st.slider('2) 나이를 선택하세요.', min_value=10, max_value=80, value=25, key='widget_age')

# 3) 라디오 버튼 : 여러 선택지 중에서 하나만 고를 때 사용한다.

job = st.radio(
    '3) 직군을 선택하세요.',
    options=['학생','직장인','취업준비생','기타'],   # 기본값 options의 list의 맨처음값 , value = 값은 넣지 않음(오류)
    key='widget_job'
    # index=3 기타가 기본값으로 지정하고 싶을때
)

# 4) 셀렉트 박스(드롭다운) : 라디오와 비슷하지만 목록이 길 때, 공간을 절약할 수 있다.
country = st.selectbox(
    '4) 가장 관심있는 무역 상대국은?', 
    options=['미국','중국','일본','베트남','EU','동아시아'],
    key='widget_country'
    # index=  로 기본값 지정 가능
)

# 5) 멀티 셀렉트 박스 : 여러개를 동시에 선택할 수 있다.
interests = st.multiselect(
    '5) 관심있는 데이터 분야를 모두 고르세요.',
    options=['무역통계','환율','관습','날씨','인구통계','수출입'],
    key='widget_interests',
    default=['무역통계']
)

# 6) 체크박스 : 참/거짓 값 하나를 받을 때
agree = st.checkbox('6) 강의 내용에 만족하시나요?', key='widget_agree')

# 7) 슬라이더 만족도
score = st.slider('7) 이 강의 만족도 점수(1~10점)', min_value=1, max_value=10, value=3, key='widget_score')
# score = st.slider('7) 이 강의 만족도 점수(1~10점)', 1,10,5, key='widget_score')

# 8) 텍스트 영역 : 여러줄의 입력 필요할 때, 자유 의견 입력
feedback = st.text_area('8) 자유롭게 의견을 남겨주세요.', key='widget_feedback')

# 9) 버튼(전송) : 클릭여부 (true/false) 를 반환한다. 클릭 했을때만 아래 코드가 실행된다.
submit = st.button('✅제출하기', key='widget_submit_btn')

st.markdown('---')

st.subheader('📊실시간 응답 요약')

# 위젯 값들을 버튼을 누르지 않아도 조작하는 즉시 바로 갱신된다.
# if 버튼 제출하기가 Ture일 때, 밑의 내용이 나오고 False면 else 로 별도 입력 내용이 나온다.
if submit :
    st.write(f'- 이름: **{name}** / 나이: **{age}**')            # {} f''에서는 변수형태로 가져오기 위함
    st.write(f'- 직군: **{job}** / 관심 국가: **{country}**')
    # st.write(f'- 관심 분야: **{",".join(interests) if interests else '선택없음'**')    # list 대괄호 없애기
    st.write(f"- 관심 분야: **{', '.join(interests) if interests else '선택없음'}**")    
    st.write(f"- 강의 만족 여부: **{'만족' if agree else '미체크'}** / 만족도 점수: **{score}**")
    st.write(f'- 자유 의견: **{feedback if feedback else "작성안함"}**')

    # f', f" 둘 중 하나로 시작 될때는 내부는 다르게 가줘야함 전체가 묶여야되는데 중간에 같은게 들어오면 충돌 발생함
    # # ",' 충돌함
else:
    st.write('위의 항목을 입력한 뒤 제출하기 버튼을 눌러주세요.')


# 일반적 if
# if a != b:
    # result = '같지 않다'
# else:
    # result = '같다'
# 삼항연산자
# result = '같지않다' if a != b else '같다'