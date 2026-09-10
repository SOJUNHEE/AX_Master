"""
타이타닉 데이터셋 기초 탐색
pandas  head/tail/shape/info/colunms 를 사용해서 데이터셋의 기본 정보를 
화면에 순서대로 보여주는 streamlit 앱니다
실행방법 streamlit run 2026.09.07_test_1.py
"""
import os
import pandas as pd
import streamlit as st
import io

st.title("🛳️타이타닉 데이터셋 기초 탐색")
st.caption("pandas의 head/tail/shape/info/colunms 를 사용해서 데이터셋의 기본 정보를 확인합니다")


#titanic.csv 가져오기
CSV_PATH = "Titanic.csv"

#st.file_uploader로 파일을 직접 올릴 수 있다, 아무것도 올리지 않으면
#아래의 기존 로직대로 같은 폴더 타이타닉 파일을 그대로 찾아서 읽는다
upload_file = st.file_uploader("Titanic.csv 파일을 직접 업로드 할 수 있습니다(선택사항)", type="csv")

if upload_file is not None : 
    df = pd.read_csv(upload_file)
else :
    try: 
        # 이 스크립트와 같은 폴더에 있는 타이타닉 파일 읽어 온다
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError :
        #파일이 없을 때 사용자가 무엇을 해야 하는지 화면에 안내한다
        st.error("❌타이타닉 파일을 찾을수가 없습니다")
        st.info("같은 경로에 파일을 업로드 하거나 csv 파일을 폴더에 넣고 새로고침하세요")
        df = None


if df is not None : 
    st.subheader("1) head() : 데이터의 앞부분 5개 행 미리보기")
    st.dataframe(df.head(), use_container_width=True) # 기본행 5개

    st.subheader("2) tail() : 데이터의 뒷부분 5개 행 미리보기")
    st.dataframe(df.tail(), use_container_width=True) # 기본행 5개


    st.subheader("3) shape() : 행 갯수, 열 갯수")
    col1, col2 = st.columns(2)
    with col1 :
        st.metric("행 개수", f"{df.shape[0]}개")

    with col2 :
        st.metric("열 개수", f"{df.shape[1]}개")

    st.subheader("4) columns : 전체 열(컬럼) 이름 목록")
    # st.write(df.columns) 이러면 표 형태
    # st.write(list[int](df.columns))
    st.write(list(df.columns))

    st.subheader("5) info() : 각 열의 자료형과 결측치(NaN) 여부 요약")
    # df.info 는 값을 리턴하지 않고 화면에 직접 출력만 해주는 함수라서 
    # io.StringIO() 라는 "메모리 위에 가짜 파일"에 결과를 받아낸 뒤 그 내용을 text로 보여 준다.

    # buffer = io.StringIO()
    # df.info(buf=buffer)
    # st.text(buffer.getvalue())
    # # 1방법
    

    info_df = pd.DataFrame({
        "타입" : df.dtypes,
        "결측치 아닌 개수": df.notna().sum(),
        "결측치 개수": df.isna().sum(),
    })
    st.dataframe(info_df, use_container_width=True)
    # 2방법

    st.success('기초 정보 확인 끝났습니다. 다음 예제에서 전처리 필터링을 할께요')
