"""
넷플릭스 콘텐츠 데이터셋 기초 탐색
pandas head/tail/shape/info/columns 를 사용해서 데이터셋의 기본 정보를 
화면에 순서대로 보여주는 streamlit 앱입니다
실행방법: streamlit run 2026.09.07_test_2.py
"""
import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="넷플릭스 데이터 탐색", page_icon="🎬", layout="wide")

st.title("🎬 넷플릭스 콘텐츠 데이터셋 기초 탐색")
st.caption("pandas의 head/tail/shape/info/columns를 사용해 데이터의 구조를 파악합니다.")

# 기본 로컬 파일 경로 설정
CSV_PATH = "netflix_titles.csv"

# 파일 업로더 제공 (직접 업로드 또는 같은 폴더 파일 읽기)
upload_file = st.file_uploader("netflix_titles.csv 파일을 직접 업로드할 수 있습니다 (선택사항)", type="csv")

if upload_file is not None:
    df = pd.read_csv(upload_file)
else:
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        st.error("❌ netflix_titles.csv 파일을 찾을 수 없습니다.")
        st.info("작업 폴더에 파일을 넣거나 위 업로더를 통해 CSV 파일을 업로드하세요.")
        df = None

if df is not None:
    # 1. head()
    st.subheader("1) head() : 상위 5개 행 미리보기")
    st.dataframe(df.head(), use_container_width=True)

    # 2. tail()
    st.subheader("2) tail() : 하위 5개 행 미리보기")
    st.dataframe(df.tail(), use_container_width=True)

    # 3. shape
    st.subheader("3) shape : 행과 열 크기")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("총 데이터(행) 수", f"{df.shape[0]:,}개")
    with col2:
        st.metric("총 속성(열) 수", f"{df.shape[1]:,}개")

    # 4. columns
    st.subheader("4) columns : 컬럼명 목록")
    st.write(list(df.columns))

    # 5. info() 요약 표
    st.subheader("5) info() : 컬럼별 데이터 타입 및 결측치 현황")
    info_df = pd.DataFrame({
        "데이터 타입": df.dtypes.astype(str),
        "정상 데이터 수": df.notna().sum(),
        "결측치(NaN) 수": df.isna().sum(),
        "결측치 비율(%)": ((df.isna().sum() / len(df)) * 100).round(2)
    })
    st.dataframe(info_df, use_container_width=True)

    st.success("데이터셋 로드 및 기초 탐색이 완료되었습니다.")