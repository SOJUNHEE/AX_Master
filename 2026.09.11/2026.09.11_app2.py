# 대화 기록을 기억하는 멀티턴 챗봇(스트리밍 응답)
# st.session_state 에 대화 기록을 저장해서, 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 streamlit의 채팅 전용 위젯을 사용합니다.
# stream=True 옵션으로 답변이 실시간으로 타이핑 되듯 출력됩니다.
# streamlit run 2026.09.11_app2.py
# 시스템 메시지를 사용자가 설정하도록
# 대화 기록 초기화 버튼


import streamlit as st
from openai import OpenAI

st.set_page_config(page_title='멀티턴 챗봇', page_icon='💬', layout='wide')
st.title('예제2) 멀티턴 스트리밍 챗봇 💬')
st.caption('대화 기록을 기억하며 실시간 타이핑 효과로 응답하는 챗봇입니다.')

# 1. 사이드바 설정
with st.sidebar:
    st.header('⚙️ 설정')
    api_key = st.text_input('OpenAI API Key', type='password', help='sk-로 시작하는 API Key를 입력하세요')
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o'], index=0)
    
    # 사용자 정의 시스템 메시지 (페르소나 설정)
    system_prompt = st.text_area(
        '시스템 메시지 (챗봇의 성격/역할 설정)',
        value='당신은 친절하고 전문적인 AI 도우미입니다.',
        help='챗봇의 역할과 어조를 지시할 수 있습니다.'
    )
    
    st.markdown('[API 발급 받기](https://platform.openai.com/api-keys)')
    st.divider()

    # 대화 기록 초기화 버튼
    if st.button('대화 초기화', type='secondary', use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 2. 세션 상태(st.session_state) 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 3. 기존 대화 기록 화면 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# 4. 사용자 입력 받기 (채팅 전용 위젯)
if prompt := st.chat_input('메시지를 입력하세요...'):
    if not api_key:
        st.error('사이드바에 OpenAI API Key를 먼저 입력해 주세요.')
    else:
        # 사용자 입력을 대화 기록에 추가 및 화면 출력
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        # AI 응답 생성 및 스트리밍 출력
        with st.chat_message('assistant'):
            try:
                client = OpenAI(api_key=api_key)

                # API에 전송할 메시지 배열 (시스템 메시지 + 이전 대화 맥락 전체)
                api_messages = [{'role': 'system', 'content': system_prompt}] + [
                    {'role': m['role'], 'content': m['content']} for m in st.session_state.messages
                ]

                # stream=True 설정으로 청크 단위 수신
                stream = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    stream=True
                )

                # st.write_stream을 통해 실시간 타이핑 효과 구현 및 전체 텍스트 수집
                response_text = st.write_stream(stream)

                # 완성된 응답을 세션 상태에 저장 (다음 대화 맥락으로 유지)
                st.session_state.messages.append({'role': 'assistant', 'content': response_text})

            except Exception as e:
                st.error(f'응답 생성 중 오류가 발생했습니다: {e}')