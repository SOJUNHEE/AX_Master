# 파일 업로드 문서 요약앱 만들거야
# 왼쪽
# 사이드바에는 API 키 입력, 모델 선택
# 요약옵션 선택 : 1. 짧게 2.보통 3.자세히
# 요약스타일 : 1. 알아듣기 쉽게 2. 일반적 3. 전문가
# 오른쪽
# 업로드 할 파일은 TXT,MD,CSV,엑셀파일
# 업로드 창 만들어주고
# 업로드한 문서 미리보여주고
# 버튼식으로 요약하기 버튼 누를 수 있게
# 현재 올려준 코드를 활용해서 다시 생성할 수 있도록 시작

import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title='문서 요약 AI', page_icon='📄', layout='wide')
st.title('📄 문서 업로드 & AI 요약기')
st.caption('다양한 형식(TXT, MD, CSV, Excel)의 문서를 업로드하고 원하는 조건에 맞춰 요약해 보세요.')

# 1. 사이드바 설정 (API, 모델, 요약 조건)
with st.sidebar:
    st.header('⚙️ 설정')
    api_key = st.text_input('OpenAI API Key', type='password', help='sk-로 시작하는 API Key를 입력하세요')
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o'], index=0)
    
    st.divider()
    st.subheader('요약 옵션')
    summary_length = st.radio(
        '요약 길이 선택',
        options=['짧게 (핵심 3줄 내외)', '보통 (문단 단위 정리)', '자세히 (상세 분석 및 주요 내용 포괄)'],
        index=1
    )
    
    summary_style = st.radio(
        '요약 스타일 선택',
        options=['알아듣기 쉽게 (초등학생도 이해할 수 있는 비유와 쉬운 표현)', '일반적 (표준적이고 명확한 어조)', '전문가 (전문 용어 및 학술/비즈니스 분석 어조)'],
        index=1
    )
    
    st.markdown('[API 발급 받기](https://platform.openai.com/api-keys)')

# 파일에서 텍스트를 추출하는 함수
def extract_text_from_file(uploaded_file):
    file_name = uploaded_file.name
    try:
        if file_name.endswith(('.txt', '.md')):
            return uploaded_file.read().decode('utf-8')
        elif file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            return df
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
            return df
    except UnicodeDecodeError:
        # 한글 인코딩(CP949) 대응
        uploaded_file.seek(0)
        if file_name.endswith('.csv'):
            return pd.read_csv(uploaded_file, encoding='cp949')
        return uploaded_file.read().decode('cp949')
    except Exception as e:
        st.error(f'파일을 읽는 도중 오류가 발생했습니다: {e}')
        return None

# 2. 메인 화면 (파일 업로드 & 미리보기 & 요약)
uploaded_file = st.file_uploader(
    '문서 파일을 업로드하세요 (TXT, MD, CSV, XLSX, XLS)',
    type=['txt', 'md', 'csv', 'xlsx', 'xls']
)

if uploaded_file is not None:
    extracted_data = extract_text_from_file(uploaded_file)
    content_for_llm = ""

    # 문서 미리보기 영역
    st.subheader('📋 업로드한 문서 미리보기')
    if isinstance(extracted_data, pd.DataFrame):
        st.dataframe(extracted_data.head(50), use_container_width=True)
        st.caption(f'전체 행: {len(extracted_data)}개 / 열: {len(extracted_data.columns)}개 (최대 상위 50개 행만 미리 표시합니다)')
        content_for_llm = extracted_data.to_string(index=False)
    elif isinstance(extracted_data, str):
        with st.expander('텍스트 내용 펼치기 / 접기', expanded=True):
            st.text_area('본문 내용', extracted_data, height=250, disabled=True)
        content_for_llm = extracted_data

    # 요약 실행 버튼
    if st.button('요약하기', type='primary'):
        if not api_key:
            st.error('사이드바에서 OpenAI API Key를 먼저 입력해 주세요.')
        elif not content_for_llm.strip():
            st.warning('문서 내용이 비어 있어 요약할 수 없습니다.')
        else:
            # 프롬프트 구성
            system_prompt = (
                f"당신은 전문 문서 요약 어시스턴트입니다.\n"
                f"- 요청된 요약 길이: {summary_length}\n"
                f"- 요청된 요약 스타일: {summary_style}\n"
                f"사용자가 제공한 문서의 맥락을 정확하게 반영하여 위 기준에 맞춰 한국어로 명확히 요약해 주세요."
            )
            
            user_prompt = f"다음 문서를 주어진 조건에 맞추어 요약해 주세요:\n\n{content_for_llm[:100000]}"

            st.divider()
            st.subheader('✨ AI 요약 결과')
            
            try:
                client = OpenAI(api_key=api_key)
                
                with st.spinner('문서를 분석하고 요약하는 중...'):
                    stream = client.chat.completions.create(
                        model=model,
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_prompt}
                        ],
                        stream=True
                    )
                    
                    # 실시간 스트리밍 출력
                    st.write_stream(stream)

            except Exception as e:
                st.error(f'요약 생성 중 오류가 발생했습니다: {e}')