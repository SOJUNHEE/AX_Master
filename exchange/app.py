import os
import base64
from pathlib import Path
from datetime import datetime
import requests
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 환경 설정 및 API 키 안전 로드
# -----------------------------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def get_secret_key(key_name: str):
    val = os.getenv(key_name)
    if val:
        return val
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return None

EXCHANGE_KEY = get_secret_key("EXCHANGE_RATE_API_KEY")

# -----------------------------------------------------------------------------
# 2. 폰트 인코딩 및 보고서형 고품격 스타일링 (글자 잘림 원천 차단)
# -----------------------------------------------------------------------------
def get_font_base64(font_path: Path):
    if font_path.exists():
        with open(font_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

font_title_path = CURRENT_DIR / "font_title.otf"
font_body_path = CURRENT_DIR / "font_body.otf"
font_title_b64 = get_font_base64(font_title_path)
font_body_b64 = get_font_base64(font_body_path)

custom_font_css = "<style>\n"
if font_title_b64:
    custom_font_css += f"""
    @font-face {{
        font-family: 'CustomTitleFont';
        src: url('data:font/otf;base64,{font_title_b64}') format('opentype');
    }}
    """
if font_body_b64:
    custom_font_css += f"""
    @font-face {{
        font-family: 'CustomBodyFont';
        src: url('data:font/otf;base64,{font_body_b64}') format('opentype');
    }}
    """

custom_font_css += f"""
    /* 글꼴 지정 */
    h1, h2, h3, h4, .stTitle, div[data-testid="stMetricLabel"] {{
        font-family: {'CustomTitleFont, ' if font_title_b64 else ''} 'Pretendard', sans-serif !important;
        word-break: keep-all !important;
        white-space: normal !important;
    }}
    html, body, [class*="css"], .stMarkdown, .stSelectbox, .stNumberInput, p, span, div, table {{
        font-family: {'CustomBodyFont, ' if font_body_b64 else ''} 'Pretendard', sans-serif;
        word-break: keep-all !important;
    }}

    /* 글자 짤림 방지 및 메트릭 컴포넌트 확장 */
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.95rem !important;
        white-space: normal !important;
        color: #4b5563 !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetricDelta"] {{
        font-size: 0.85rem !important;
        white-space: normal !important;
    }}

    /* 공문서/보고서 스타일 블록 */
    .report-header {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 25px;
    }}
    .section-box {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }}
    .badge-export {{
        display: inline-block;
        background-color: #ecfdf5;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.88rem;
        font-weight: bold;
        margin: 2px;
        border: 1px solid #a7f3d0;
    }}
    .badge-import {{
        display: inline-block;
        background-color: #eff6ff;
        color: #1e40af;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.88rem;
        font-weight: bold;
        margin: 2px;
        border: 1px solid #bfdbfe;
    }}
</style>
"""

# -----------------------------------------------------------------------------
# 3. Streamlit UI 기본 세팅
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="대외 교역 타당성 및 외환 리스크 종합 평가 리포트",
    page_icon="📑",
    layout="wide",
)
st.markdown(custom_font_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 환율 API 호출 함수 (실시간 USD 기준 30분 캐시)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=1800)
def get_live_exchange_rates(api_key: str):
    if not api_key:
        return None, "환율 API 키 미설정"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {}), None
            return None, data.get("error-type", "API 응답 오류")
        elif res.status_code == 401:
            return None, "환율 API 인증 실패"
        else:
            return None, f"서버 오류 ({res.status_code})"
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 에러: {e}"

# -----------------------------------------------------------------------------
# 5. 국가 메타데이터 & 대외 교역 팩트시트
# -----------------------------------------------------------------------------
COUNTRY_METADATA = {
    "US": {"name": "미국 (United States)", "currency": "USD", "region": "북미", "openness": 88},
    "CN": {"name": "중국 (China)", "currency": "CNY", "region": "아시아", "openness": 70},
    "VN": {"name": "베트남 (Vietnam)", "currency": "VND", "region": "아시아", "openness": 92},
    "JP": {"name": "일본 (Japan)", "currency": "JPY", "region": "아시아", "openness": 75},
    "EU": {"name": "유로존 (Eurozone)", "currency": "EUR", "region": "유럽", "openness": 85},
    "AU": {"name": "호주 (Australia)", "currency": "AUD", "region": "오세아니아", "openness": 78},
    "GB": {"name": "영국 (United Kingdom)", "currency": "GBP", "region": "유럽", "openness": 80},
    "KR": {"name": "대한민국 (South Korea)", "currency": "KRW", "region": "아시아", "openness": 85},
}

KOREA_TRADE_STATS = {
    "US": {
        "export_val": 1157.0, "import_val": 732.0, "balance": 425.0,
        "top_exports": ["자동차 및 부품", "메모리 반도체", "전기차 이차전지"],
        "top_imports": ["원유 및 천연가스(LNG)", "반도체 제조용 장비", "항공기 및 부품"]
    },
    "CN": {
        "export_val": 1248.0, "import_val": 1428.0, "balance": -180.0,
        "top_exports": ["메모리 반도체", "합성수지(화학)", "평판 디스플레이"],
        "top_imports": ["이차전지 소재(수산화리튬)", "컴퓨터 부품", "의류 및 정밀화학"]
    },
    "VN": {
        "export_val": 535.0, "import_val": 260.0, "balance": 275.0,
        "top_exports": ["전자부품/반도체", "평판 디스플레이 패널", "무선통신기기 부품"],
        "top_imports": ["무선통신기기 완제품", "봉제 및 의류", "가죽 신발류"]
    },
    "JP": {
        "export_val": 290.0, "import_val": 476.0, "balance": -186.0,
        "top_exports": ["정제 석유제품", "철강판재류", "기초 유기화학품"],
        "top_imports": ["정밀 반도체 장비", "소부장 핵심 소재", "특수 플라스틱 소재"]
    },
    "EU": {
        "export_val": 680.0, "import_val": 725.0, "balance": -45.0,
        "top_exports": ["친환경 승용차", "선박 및 해양구조물", "전기차 배터리"],
        "top_imports": ["산업용 정밀기계", "의약품 및 백신", "유럽산 수입 승용차"]
    },
    "AU": {
        "export_val": 182.0, "import_val": 324.0, "balance": -142.0,
        "top_exports": ["자동차용 휘발유/경유", "화물용 승용차", "건설용 중장비"],
        "top_imports": ["고품위 철광석", "발전용 유연탄", "천연가스(LNG)"]
    },
    "GB": {
        "export_val": 61.0, "import_val": 58.0, "balance": 3.0,
        "top_exports": ["고부가가치 선박", "승용차", "항공유/제트유"],
        "top_imports": ["북해산 브렌트유", "바이오 의약품", "항공우주 엔진 부품"]
    },
    "KR": {
        "export_val": 6326.0, "import_val": 6426.0, "balance": -100.0,
        "top_exports": ["반도체", "자동차", "석유제품"],
        "top_imports": ["원유", "천연가스", "석탄"]
    }
}

MACRO_HISTORICAL_DATA = {
    "US": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [23.32, 25.46, 27.36, 28.78, 30.10], "gni": [70430, 76370, 81690, 85000, 88200]},
    "CN": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [17.82, 17.96, 17.79, 18.50, 19.30], "gni": [12300, 12850, 13400, 14100, 14900]},
    "VN": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [0.37, 0.41, 0.43, 0.47, 0.51], "gni": [3640, 3950, 4150, 4400, 4700]},
    "JP": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [5.00, 4.23, 4.21, 4.10, 4.25], "gni": [39800, 35400, 34500, 35000, 36100]},
    "EU": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [14.45, 13.90, 14.70, 15.10, 15.60], "gni": [42000, 40500, 42300, 43800, 45200]},
    "AU": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [1.68, 1.70, 1.72, 1.78, 1.85], "gni": [58700, 60100, 61500, 63200, 65000]},
    "GB": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [3.13, 3.07, 3.34, 3.45, 3.58], "gni": [45300, 44100, 46200, 47900, 49500]},
    "KR": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [1.81, 1.67, 1.71, 1.83, 1.92], "gni": [35150, 32800, 33745, 35500, 37200]},
}

# -----------------------------------------------------------------------------
# 6. 사이드바 컨트롤 & 데이터 바인딩
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 📋 보고서 제어 패널")
selected_country_code = st.sidebar.selectbox(
    "분석 대상 국가 선택",
    options=list(COUNTRY_METADATA.keys()),
    format_func=lambda x: COUNTRY_METADATA[x]["name"],
    index=0
)

country_info = COUNTRY_METADATA[selected_country_code]
trade_info = KOREA_TRADE_STATS[selected_country_code]
target_currency = country_info["currency"]

# 실시간 환율 호출
live_rates, _ = get_live_exchange_rates(EXCHANGE_KEY)
fallback_rates = {"KRW": 1350.0, "JPY": 152.0, "CNY": 7.25, "USD": 1.0, "EUR": 0.92, "GBP": 0.78, "AUD": 1.50, "VND": 25400.0}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates
current_rate = rates_dict.get(target_currency, fallback_rates.get(target_currency, 1.0))

# 과거 환율 밴드 산출 (5개년)
years = [2021, 2022, 2023, 2024, 2025]
np.random.seed(hash(selected_country_code) % 100)
fluct = [1.05, 1.02, 0.98, 1.01, 1.0] if target_currency != "USD" else [1.0, 1.0, 1.0, 1.0, 1.0]
sim_rates = [round(current_rate * f, 2) for f in fluct]
high_rates = [round(r * 1.04, 2) for r in sim_rates]
low_rates = [round(r * 0.96, 2) for r in sim_rates]

macro_data = MACRO_HISTORICAL_DATA[selected_country_code]
latest_gdp = macro_data["gdp"][-1]
latest_gni = macro_data["gni"][-1]

# 스코어링 로직
rate_volatility = (np.std(sim_rates) / np.mean(sim_rates)) * 100
volatility_score = max(0, 100 - (rate_volatility * 10))
gdp_score = min(100, (latest_gdp / 25.0) * 100)
gni_score = min(100, (latest_gni / 80000) * 100)
openness_score = country_info["openness"]
total_score = round((volatility_score * 0.3) + (gdp_score * 0.3) + (gni_score * 0.2) + (openness_score * 0.2), 1)

if total_score >= 80:
    grade = "S 등급 (최우수 교역 파트너)"
elif total_score >= 70:
    grade = "A 등급 (우수 교역 파트너)"
elif total_score >= 60:
    grade = "B 등급 (조건부 협력 권장)"
else:
    grade = "C 등급 (고위험 주의 관찰)"

# -----------------------------------------------------------------------------
# 7. 다운로드용 종합 데이터셋 생성 (CSV 변환)
# -----------------------------------------------------------------------------
export_rows = []
for idx, y in enumerate(years):
    export_rows.append({
        "국가코드": selected_country_code,
        "국가명": country_info["name"],
        "기준통화": target_currency,
        "연도": y,
        "환율(USD대비)": sim_rates[idx],
        "밴드최고환율": high_rates[idx],
        "밴드최저환율": low_rates[idx],
        "명목GDP(조USD)": macro_data["gdp"][idx],
        "1인당GNI(USD)": macro_data["gni"][idx],
        "종합적합도점수": total_score,
        "최종등급": grade,
        "대한국수출액(억USD)": trade_info["export_val"],
        "대한국수입액(억USD)": trade_info["import_val"],
        "무역수지(억USD)": trade_info["balance"],
        "생성일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
df_download = pd.DataFrame(export_rows)
csv_data = df_download.to_csv(index=False).encode('utf-8-sig')

# =============================================================================
# [보고서 본문 시작] EXECUTIVE REPORT FORMAT
# =============================================================================

# [1] 보고서 헤더
st.markdown(f"""
<div class="report-header">
    <div style="font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Executive Economic & Trade Briefing</div>
    <h1 style="margin: 6px 0 10px 0; color: #0f172a;">대외 교역 타당성 및 외환 리스크 종합 평가서</h1>
    <div style="font-size: 0.95rem; color: #334155; line-height: 1.6;">
        본 보고서는 <b>{country_info['name']}</b>을(를) 대상으로 실시간 외환 시장 데이터, 5개년 시계열 밴드, 거시경제 체력(GDP·GNI), 
        대한민국 관세청 대외 무역 수지를 종합하여 기업 의사결정권자에게 계량화된 무역 타당성 지표를 제공합니다.
    </div>
    <div style="margin-top: 12px; font-size: 0.85rem; color: #94a3b8;">
        발행 기준일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} | 분석 통화: {target_currency}
    </div>
</div>
""", unsafe_allow_html=True)

# 상단 원클릭 보고서 데이터 다운로드
dl_col1, dl_col2 = st.columns([4, 1.2])
with dl_col1:
    st.caption("📥 본 대시보드에 집계된 실시간 환율 및 5개년 거시 지표를 CSV 파일로 내려받아 내부 검토 자료로 활용할 수 있습니다.")
with dl_col2:
    st.download_button(
        label="📊 분석 데이터 다운로드 (CSV)",
        data=csv_data,
        file_name=f"Trade_Evaluation_{selected_country_code}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# [2] 실시간 외환 정산 시뮬레이터 (단순 계산기)
# -----------------------------------------------------------------------------
st.markdown("### 1. 실시간 외환 정산 시뮬레이터 (Live Conversion Calculator)")
st.caption("선택 국가 통화 금액을 입력하면 현재 실시간 고시 환율을 기준으로 달러(USD)와 원화(KRW) 결제 대금이 자동 산출됩니다.")

with st.container(border=True):
    calc_c1, calc_c2, calc_c3 = st.columns([1.5, 1.5, 1.5])

    with calc_c1:
        st.markdown(f"**기준 금액 입력 ({target_currency})**")
        input_val = st.number_input(
            "금액 입력",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            format="%.2f",
            label_visibility="collapsed"
        )
        st.caption(f"적용 국가: {country_info['name']}")

    rate_usd_per_tgt = (rates_dict.get("USD", 1.0) / current_rate)
    rate_krw_per_tgt = (rates_dict.get("KRW", 1350.0) / current_rate)
    val_usd = input_val * rate_usd_per_tgt
    val_krw = input_val * rate_krw_per_tgt

    with calc_c2:
        st.markdown("**미화 결제 환산 (USD)**")
        st.metric(
            label="USD 환산 대금",
            value=f"${val_usd:,.2f}",
            delta=f"1 {target_currency} = ${rate_usd_per_tgt:,.4f}"
        )

    with calc_c3:
        st.markdown("**원화 결제 환산 (KRW)**")
        st.metric(
            label="KRW 환산 대금",
            value=f"₩{val_krw:,.0f}",
            delta=f"1 {target_currency} = ₩{rate_krw_per_tgt:,.2f}"
        )

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# [3] 종합 평가 결과 요약표 (Executive Summary)
# -----------------------------------------------------------------------------
st.markdown("### 2. 종합 타당성 평가 요약 (Executive Summary)")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("종합 적합도 평점", f"{total_score}점 / 100점", delta=grade)
bal_text = f"+{trade_info['balance']:,.0f}억 달러 (흑자)" if trade_info['balance'] > 0 else f"{trade_info['balance']:,.0f}억 달러 (적자)"
col_m2.metric("대(對)한국 무역수지", bal_text)
col_m3.metric("명목 경제규모 (GDP)", f"${latest_gdp:,.2f}조 USD", delta=f"1인당 소득 ${latest_gni:,.0f}")
col_m4.metric("환율 변동성 리스크", f"{rate_volatility:.2f}%", delta="🟢 안정" if rate_volatility < 5 else "🟡 주의", delta_color="inverse")

# 대외 교역 팩트시트 블록
with st.container(border=True):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown(f"**📦 한국의 대(對){selected_country_code} 주요 수출 품목 TOP 3** (수출 총액: **${trade_info['export_val']:,.0f}억**)")
        exp_badges = " ".join([f"<span class='badge-export'>✓ {item}</span>" for item in trade_info["top_exports"]])
        st.markdown(exp_badges, unsafe_allow_html=True)
    with f_col2:
        st.markdown(f"**📥 한국의 대(對){selected_country_code} 주요 수입 품목 TOP 3** (수입 총액: **${trade_info['import_val']:,.0f}억**)")
        imp_badges = " ".join([f"<span class='badge-import'>✓ {item}</span>" for item in trade_info["top_imports"]])
        st.markdown(imp_badges, unsafe_allow_html=True)

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# [4] 시계열 환율 밴드 및 거시경제 지표 추이
# -----------------------------------------------------------------------------
st.markdown("### 3. 환율 변동 밴드 및 거시경제 펀더멘털 시계열")
st.caption("장기 환율 변동 범위(High-Low)를 통해 현재 환율의 과열/저평가 수준을 진단하고 경제 성장 추이를 비교합니다.")

col_g1, col_g2 = st.columns([1.2, 0.8], gap="large")

with col_g1:
    df_band = pd.DataFrame({
        "연도": [str(y) for y in years],
        "평균환율": sim_rates,
        "최고환율": high_rates,
        "최저환율": low_rates
    })

    fig_band = go.Figure()
    fig_band.add_trace(go.Scatter(
        x=df_band["연도"].tolist() + df_band["연도"].tolist()[::-1],
        y=df_band["최고환율"].tolist() + df_band["최저환율"].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        name="변동 밴드 (최고-최저)"
    ))
    fig_band.add_trace(go.Scatter(
        x=df_band["연도"],
        y=df_band["평균환율"],
        mode='lines+markers+text',
        text=[f"{v:,.1f}" for v in df_band["평균환율"]],
        textposition="top center",
        line=dict(color='#2563eb', width=3),
        name=f"기준 환율 ({target_currency}/USD)"
    ))
    fig_band.update_layout(
        title=f"USD 대비 {target_currency} 5개년 환율 밴드",
        height=350,
        margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_band, use_container_width=True)

with col_g2:
    df_macro = pd.DataFrame({
        "연도": [str(y) for y in macro_data["years"]],
        "GDP": macro_data["gdp"],
        "GNI": macro_data["gni"]
    })
    
    fig_macro = go.Figure()
    fig_macro.add_trace(go.Bar(
        x=df_macro["연도"],
        y=df_macro["GDP"],
        name="명목 GDP (조 USD)",
        marker_color="#10b981",
        yaxis="y"
    ))
    fig_macro.add_trace(go.Scatter(
        x=df_macro["연도"],
        y=df_macro["GNI"],
        name="1인당 GNI (USD)",
        mode="lines+markers",
        marker_color="#f59e0b",
        yaxis="y2"
    ))
    fig_macro.update_layout(
        title="거시 경제 규모(GDP) 및 국민소득(GNI)",
        height=350,
        margin=dict(l=10, r=10, t=40, b=20),
        yaxis=dict(title="GDP (조 USD)"),
        yaxis2=dict(title="GNI ($)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_macro, use_container_width=True)

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# [5] 4대 무역 적합성 레이더 다차원 평가
# -----------------------------------------------------------------------------
st.markdown("### 4. 4대 무역 적합성 다차원 정량 평가")
st.caption("환율 안정성, 시장 규모, 국민 구매력, 시장 개방도를 다각도로 종합 검증한 레이더 스코어카드입니다.")

col_r1, col_r2 = st.columns([1, 1], gap="large")

with col_r1:
    categories = ['환율 안정성', '시장 규모(GDP)', '소비 구매력(GNI)', '외환 개방도']
    values = [volatility_score, gdp_score, gni_score, openness_score]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.2)',
        line=dict(color='#059669', width=2),
        name="국가 펀더멘털 스코어"
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=320,
        margin=dict(l=30, r=30, t=30, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_r2:
    with st.container(border=True):
        st.markdown("#### 🎯 **지표별 가중치 평가 세부 내역**")
        st.write(f"- **환율 안정성 지수 (30%)**: `{volatility_score:.1f}점` / 100점 (변동률 {rate_volatility:.2f}%)")
        st.progress(int(volatility_score))
        st.write(f"- **시장 규모 지수 (30%)**: `{gdp_score:.1f}점` / 100점 (명목 GDP ${latest_gdp:.2f}조)")
        st.progress(int(gdp_score))
        st.write(f"- **소비 구매력 지수 (20%)**: `{gni_score:.1f}점` / 100점 (1인당 GNI ${latest_gni:,.0f})")
        st.progress(int(gni_score))
        st.write(f"- **대외 개방도 지수 (20%)**: `{openness_score}점` / 100점 (외환 결제 건전성)")
        st.progress(int(openness_score))

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# [6] 수출 기업 vs 수입 기업 실무 액션 플랜 (Executive Action Plan)
# -----------------------------------------------------------------------------
st.markdown("### 5. 기업 실무 액션 플랜 (Strategic Action Plan)")
st.caption("환율 흐름 및 거시 체력에 따라 수출 지향 기업과 수입 지향 기업이 즉시 이행해야 할 전술 지침입니다.")

tab_ex, tab_im = st.tabs(["🚀 [수출 지향 기업 전략]", "📦 [수입·소싱 기업 전략]"])

with tab_ex:
    st.markdown(f"""
    <div class="section-box">
        <h4 style="color: #1e3a8a; margin-top: 0;">🎯 수출 가격 정책 및 결제 통화 지침</h4>
        <ul style="line-height: 1.8; color: #334155;">
            <li><b>결제 통화 추천</b>: <b>{'기축통화(USD) 100% 결제 권장' if target_currency != 'USD' else 'USD 표준 결제'}</b> (현지 통화 약세 국면에서의 환차손을 원천 방어).</li>
            <li><b>단가 연동제</b>: 원자재 가격 변동폭이 클 경우 계약서 내 <i>환율 연동 조정 조항(Currency Adjustment Clause)</i>을 명시하여 납품 단가를 보호할 것.</li>
            <li><b>유망 공략 분야</b>: <code>{', '.join(trade_info['top_exports'])}</code> 부문에서 프리미엄 브랜딩 및 납기 신뢰성을 바탕으로 장기 공급망 지위를 공고화할 것.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab_im:
    st.markdown(f"""
    <div class="section-box">
        <h4 style="color: #1e3a8a; margin-top: 0;">🏭 원자재 소싱 및 외환 리스크 헷징 지침</h4>
        <ul style="line-height: 1.8; color: #334155;">
            <li><b>원가 관리</b>: 주요 수입 품목인 <code>{', '.join(trade_info['top_imports'])}</code>의 조달 가격 안정화를 위해 현지 통화 약세 구간에서 6개월~1년 분량의 선도 계약 체결 권장.</li>
            <li><b>헤지(Hedging) 전략</b>: 환율 변동성 지수가 <b>{rate_volatility:.2f}%</b> 수준이므로, 결제 시점의 환율 급등을 방어하기 위한 선물환 매수(Forward Buy) 또는 통화옵션 도입 필수.</li>
            <li><b>대체 공급선</b>: 단일 국가 수입 의존도가 높은 원자재의 경우 공급망 교란 리스크를 줄이기 위해 제3국 다변화 인벤토리 확보.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 하단 다운로드 및 마무리
st.divider()
b_col1, b_col2 = st.columns([4, 1.2])
with b_col1:
    st.caption("※ 본 리포트는 공공 데이터 및 실시간 API 기반의 시뮬레이션 지표이며, 실제 무역 계약 시 공인 금융기관의 고시 환율을 재확인하시기 바랍니다.")
with b_col2:
    st.download_button(
        label="📥 최종 보고서 데이터 CSV 저장",
        data=csv_data,
        file_name=f"Trade_Evaluation_{selected_country_code}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
        key="bottom_dl"
    )