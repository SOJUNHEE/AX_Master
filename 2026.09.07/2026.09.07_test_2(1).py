"""
넷플릭스 콘텐츠 데이터셋 결측치 정리
director(감독) 열의 결측치(NaN) 확인 및 제거
netflix_cleaned.csv로 저장
실행방법: streamlit run 2026.09.07_test_1.py
"""
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="넷플릭스 데이터 결측치 정리", page_icon="🎬", layout="wide")

st.title("🎬 넷플릭스 데이터 결측치 정리")
st.caption("특정 열의 결측치를 확인하고, 제거한 뒤 새 CSV 파일로 저장합니다.")

# 기본 파일 경로 설정
csv_path = "netflix_titles.csv"

# 파일 업로더
upload_file = st.file_uploader("netflix_titles.csv 파일을 직접 업로드할 수 있습니다 (선택사항)", type="csv")

if upload_file is not None:
    df = pd.read_csv(upload_file)
else:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error("❌ netflix_titles.csv 파일을 찾을 수 없습니다.")
        st.info("작업 폴더에 파일을 넣거나 위 업로더를 통해 CSV 파일을 업로드하세요.")
        df = None

if df is not None:
    st.metric("원본 데이터 행 개수", f"{len(df):,}행")
    st.markdown("---")

    # 1. 결측치(NaN) 확인 및 dropna 처리
    st.subheader("1) 감독(director) 열 결측치 처리")
    
    # isna().sum()으로 결측치 개수 파악
    missing_director_count = df["director"].isna().sum()
    st.write(f"director 열의 결측치 개수: **{missing_director_count:,}개**")

    # subset=["director"]: director 열이 비어있는 행만 제거
    df_clean = df.dropna(subset=["director"])

    # 제거 전/후 비교
    col1, col2 = st.columns(2)
    with col1:
        st.metric("제거 전", f"{len(df):,}행")
    with col2:
        st.metric("제거 후", f"{len(df_clean):,}행")

    st.markdown("---")

    # 2. 정리된 데이터를 csv 파일로 저장
    st.subheader("2) 정제된 파일 저장")
    output_path = "netflix_cleaned.csv"
    df_clean.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    st.success(f"'{output_path}' 파일로 저장을 완료했습니다!")
    st.dataframe(df_clean[["title", "type", "director", "release_year", "rating"]].head(10), use_container_width=True)