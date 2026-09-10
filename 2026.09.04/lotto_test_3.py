# random 모듈을 이용해서 1~45중 중복 없는 번호 6개를 뽑고
# 자료 구조 set, 버튼을 누르면 5세트를 한번에 생성
# datetime 으로 생성 시간도 함께 보여준다.
# 로또 ver1
# 로또 ver2
# 로또 ver3
# 다시 확인용



#import streamlit as st
#import random
#from datetime import datetime

#st.title('🎱로또 번호 자동 생성기')
#st.caption('버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다.')
#st.markdown('---')


#def lotto_one_set() -> list :
    #""" 1~45 에서 중복 없이 번호 6개 뽑아 정렬된 리스트로 반환"""     

    #number = set[int]()  
    #while len(number) < 6 :
        #number.add(random.randint(1,45)) # 1이상 45이하 정수 하나 뽑기
    #return sorted(number)

#st.markdown('---')

#st.button('🍀5세트 번호 생성하기', key='widget_lotto_btn')
#now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#st.write(f'생성시각: **{now_str}**')

#for set_index in range(1,6) :
    #lotto_num = lotto_one_set()
    #st.write(f'{set_index}세트 : {lotto_num}')


# random 모듈을 이용해서 1~45중 중복 없는 번호 6개를 뽑고
# 자료 구조 set, 버튼을 누르면 5세트를 한번에 생성
# datetime 으로 생성 시간도 함께 보여준다.

import streamlit as st
import random
from datetime import datetime

st.title('🎱 로또 번호 자동 생성기')
st.caption('버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다.')
st.markdown('---')


def lotto_one_set() -> list:
    """1~45 에서 중복 없이 번호 6개 뽑아 정렬된 리스트로 반환"""
    numbers = set()
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))  # 1이상 45이하 정수 하나 뽑기
    return sorted(numbers)


def get_ball_emoji(num: int) -> str:
    """실제 로또 번호 대역별 공 색상 이모지 반환"""
    if num <= 10:
        return f"🟡 {num}"   # 1~10번: 노란색
    elif num <= 20:
        return f"🔵 {num}"  # 11~20번: 파란색
    elif num <= 30:
        return f"🔴 {num}"  # 21~30번: 빨간색
    elif num <= 40:
        return f"⚪ {num}"  # 31~40번: 회색/은색
    else:
        return f"🟢 {num}"  # 41~45번: 초록색


# 버튼 생성 및 클릭 여부 확인
btn = st.button('🍀 5세트 번호 생성하기', key='widget_lotto_btn')

# 버튼을 눌렀을 때만 실행
if btn:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.write(f'생성시각: **{now_str}**')
    st.markdown('---')

    for set_index in range(1, 6):
        lotto_num = lotto_one_set()
        formatted_balls = "  ".join([get_ball_emoji(n) for n in lotto_num])
        st.write(f"**{set_index}세트** : {formatted_balls}")