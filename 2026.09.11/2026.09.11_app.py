# OpenAI + streamlit 앱
# 질문 하나 입력하면 OpenAI chat Completions API 한번 호출
# 답변을 받아오는 가장 단순한 방법
# 대화 기록을 기억하지 않는 단발성 질문,답변
# 실행: streamlit run 2026.09.11_app.py

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title='챗봇입니다.', page_icon='🤖')
st.title('예제1) 첫번째 챗봇')
st.caption('질문 하나만 입력하면 OpenAI chat Completions API 호출, 답변 받아오는 가장 단순한 방법')

# 사이드바 API / MODEL
with st.sidebar:
    st.header('설정')
    api_key = st.text_input('OpenAI API Key', type='password', help='sk-로 시작하는 OpenAI API Key를 입력하세요')
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o'], index=0)
    st.markdown('[API 발급 받기](https://platform.openai.com/api-keys)')

# 메인 화면
with st.form('chat_form'):
    question = st.text_input('질문을 입력하세요', placeholder='예) 인공지능이란 무엇인가요?')
    submitted = st.form_submit_button('질문하기', type='primary')

if submitted:
    if not api_key:
        st.error('OpenAI API Key를 입력하세요.')
    elif not question:
        st.error('질문을 입력하세요.')
    else:
        try:
            with st.spinner('답변을 생각하는 중...'):
                client = OpenAI(api_key=api_key)
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {'role': 'system', 'content': '당신은 언제나 "주인님"이라는 호칭으로 시작하는 극진하고 친절한 도우미입니다.'},
                        {'role': 'user', 'content': question}
                    ]
                )

            answer = response.choices[0].message.content
            st.success('답변 생성 완료!')
            st.markdown(answer)

            usage = response.usage
            st.divider()
            st.caption('📊 **토큰 사용량**')
            col1, col2, col3 = st.columns(3)
            col1.metric('입력 토큰 (Prompt)', f'{usage.prompt_tokens:,}개')
            col2.metric('출력 토큰 (Completion)', f'{usage.completion_tokens:,}개')
            col3.metric('총 토큰 (Total)', f'{usage.total_tokens:,}개')

        except Exception as e:
            st.error(f'API 호출 중 오류가 발생했습니다: {e}')