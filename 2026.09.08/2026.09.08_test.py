# raw_trade_data.csv 파일 활용
# HS코드가 85로 시작하는 반도체 + 국가명 미국 또는 베트남 + 수출금액 0 보다 큰 수(실제 수출실적) 행만
# 다중 조건으로 필터링 한 뒤, 수출금액 상위 10건을 화면에 보여주고 report.csv 로 저장
# streamlit 사용 streamlit run 2026.09.08_test.py
# git hub 올리기
# 다시
# 다시
# 다시
# 다시





import os
import pandas as pd
import streamlit as st
import altair as alt

# Page Configuration
st.set_page_config(
    page_title="반도체 수출 실적 분석기",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 반도체 수출 실적 분석 및 보고서 생성기")
st.markdown("""
이 애플리케이션은 **HS코드 85로 시작하는 반도체** 품목의 **미국 및 베트남** 대상 실제 수출 실적(수출금액 > 0)을 분석합니다.  
분석 필수 컬럼의 **결측치(NA)를 사전에 제거**한 뒤, 필터링된 **수출금액 상위 10건**을 화면에 제공하고 `report.csv`로 저장합니다.
""")

# Path resolution
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.abspath(os.path.join(script_dir, "..", "common", "raw_trade_data.csv"))
report_path = os.path.join(script_dir, "report.csv")

# If relative path doesn't exist, use fallback absolute path
if not os.path.exists(csv_path):
    csv_path = r"C:\Users\user\AX_Master_2\common\raw_trade_data.csv"

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Ensure proper data types
        df['hs_code'] = df['hs_code'].astype(str)
        return df
    else:
        st.error(f"데이터 파일을 찾을 수 없습니다: {path}")
        return None

# Load the raw data
raw_df = load_data(csv_path)

if raw_df is not None:
    # -------------------------------------------------------------
    # 🧹 결측치(NaN) 처리 로직 추가
    # -------------------------------------------------------------
    # 분석에 필수적인 핵심 컬럼 지정
    essential_cols = ['hs_code', '품목명', '국가명', '수출금액']
    existing_cols = [col for col in essential_cols if col in raw_df.columns]
    
    # 원본 건수 및 결측치 제거 후 건수 계산
    total_raw_count = len(raw_df)
    df = raw_df.dropna(subset=existing_cols).copy()
    dropped_na_count = total_raw_count - len(df)

    # -------------------------------------------------------------
    # 🔍 사이드바 검색 및 필터 옵션
    # -------------------------------------------------------------
    st.sidebar.header("🔍 검색 및 필터 옵션")
    
    # 1. HS Code Filter
    hs_prefix = st.sidebar.text_input("HS코드 시작 패턴 (예: 85)", value="85")
    
    # 2. Product Name Filter
    item_options = sorted(df['품목명'].dropna().unique())
    default_item_idx = item_options.index("반도체") if "반도체" in item_options else 0
    selected_item = st.sidebar.selectbox("품목명", options=item_options, index=default_item_idx)
    
    # 3. Country Filter
    country_options = sorted(df['국가명'].dropna().unique())
    default_countries = [c for c in ["미국", "베트남"] if c in country_options]
    selected_countries = st.sidebar.multiselect("국가명", options=country_options, default=default_countries)
    
    # 4. Export Amount Filter
    min_export = st.sidebar.number_input("최소 수출금액 (0 초과)", value=0, min_value=0)
    
    # -------------------------------------------------------------
    # 🎯 다중 조건 필터링 로직 (결측치가 제거된 df 기준)
    # -------------------------------------------------------------
    cond_hs = df['hs_code'].str.startswith(hs_prefix)
    cond_item = df['품목명'] == selected_item
    cond_country = df['국가명'].isin(selected_countries)
    cond_export = df['수출금액'] > min_export
    
    # 결측치 제외 + 다중 조건 적용
    filtered_df = df[cond_hs & cond_item & cond_country & cond_export]
    
    # Sort and get Top 10
    top_10 = filtered_df.sort_values(by='수출금액', ascending=False).head(10)
    
    # Automatic saving of report.csv
    save_success = False
    save_error_msg = ""
    try:
        top_10.to_csv(report_path, index=False, encoding='utf-8-sig')
        save_success = True
    except Exception as e:
        save_success = False
        save_error_msg = str(e)
    
    # -------------------------------------------------------------
    # 📈 요약 통계 출력 (4컬럼으로 너비 확보 및 금액 잘림 방지)
    # -------------------------------------------------------------
    st.markdown("### 📈 요약 통계")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("조건 부합 총 건수", f"{len(filtered_df):,} 건")
    with col2:
        top_sum = top_10['수출금액'].sum() if len(top_10) > 0 else 0
        st.metric("상위 10건 총 수출금액", f"${top_sum:,.0f}")
    with col3:
        top_max = top_10['수출금액'].max() if len(top_10) > 0 else 0
        st.metric("상위 10건 최고 수출금액", f"${top_max:,.0f}")
    with col4:
        top_avg = top_10['수출금액'].mean() if len(top_10) > 0 else 0
        st.metric("상위 10건 평균 수출금액", f"${top_avg:,.0f}")

    # 결측치 제외 정보는 하단에 별도 표시
    if dropped_na_count > 0:
        st.warning(f"ℹ️ 데이터 정제: 필수 분석 항목에 결측치(NA)가 포함된 **{dropped_na_count:,}건**의 행을 분석 대상에서 사전 제외했습니다.")
    else:
        st.info("ℹ️ 데이터 정제: 분석 대상 데이터에 결측치(NA)가 존재하지 않습니다. (제외된 행: 0건)")

    st.markdown("---")

    # -------------------------------------------------------------
    # 📋 상위 10건 데이터 테이블 표시
    # -------------------------------------------------------------
    st.markdown("### 🏆 수출금액 상위 10건 상세 내역 (결측치 제외 데이터 기준)")
    
    if len(top_10) > 0:
        display_df = top_10.copy().reset_index(drop=True)
        display_df.index = display_df.index + 1
        
        st.dataframe(
            display_df.style.format({'수출금액': '{:,.0f}'}),
            use_container_width=True
        )
        
        # 파일 저장 상태 알림 및 다운로드 버튼
        if save_success:
            st.success(f"✅ `report.csv` 파일이 성공적으로 저장되었습니다. (경로: `{report_path}`)")
        else:
            st.error(f"❌ 파일 자동 저장 실패: {save_error_msg}")
            
        csv_data = top_10.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 report.csv 직접 다운로드",
            data=csv_data,
            file_name="report.csv",
            mime="text/csv"
        )

        # -------------------------------------------------------------
        # 📊 시각화 (x축 라벨 가로 정렬 고정)
        # -------------------------------------------------------------
        st.markdown("### 📊 상위 10건 수출금액 비교 차트")
        
        chart_data = top_10.copy()
        if '기간' in chart_data.columns:
            chart_data['label'] = chart_data['기간'].astype(str) + " (" + chart_data['국가명'].astype(str) + ")"
        else:
            chart_data['label'] = chart_data['국가명'].astype(str)

        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X('label:N', title='구분', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('수출금액:Q', title='수출금액'),
                color=alt.Color('국가명:N', legend=alt.Legend(title="국가명")),
                tooltip=['국가명', '수출금액']
            )
            .properties(height=380)
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("⚠️ 선택하신 조건에 부합하는 유효 데이터가 존재하지 않습니다.")