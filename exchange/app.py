import os
import base64
from pathlib import Path
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
# 2. 커스텀 폰트(OTF) 로드 및 CSS 인젝션
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
    h1, h2, h3, .stTitle, div[data-testid="stMetricLabel"] {{
        font-family: {'CustomTitleFont, ' if font_title_b64 else ''} 'Pretendard', sans-serif !important;
    }}
    html, body, [class*="css"], .stMarkdown, .stSelectbox, .stNumberInput, p, span, div {{
        font-family: {'CustomBodyFont, ' if font_body_b64 else ''} 'Pretendard', sans-serif;
    }}
    @media (max-width: 768px) {{
        div[data-testid="stMetricValue"] {{ font-size: 1.3rem !important; }}
        div[data-testid="stMetricLabel"] {{ font-size: 0.8rem !important; }}
        .stMarkdown h1 {{ font-size: 1.5rem !important; }}
        .stMarkdown h2 {{ font-size: 1.25rem !important; }}
        .stMarkdown h3 {{ font-size: 1.05rem !important; }}
        div[data-testid="column"] {{ margin-bottom: 0.5rem; }}
    }}
    .badge-export {{ background-color: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 0.85rem; }}
    .badge-import {{ background-color: #e3f2fd; color: #1565c0; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 0.85rem; }}
</style>
"""

# -----------------------------------------------------------------------------
# 3. Streamlit UI 기본 세팅
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="글로벌 환율 & 무역 적합도 분석 인텔리전스",
    page_icon="🌐",
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
# 5. 국가별 메타데이터, 거시경제 및 한국과의 실제 무역 통계
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
        "top_exports": ["자동차", "반도체", "전기차 배터리"],
        "top_imports": ["원유/천연가스", "반도체 제조용 장비", "항공기 부품"]
    },
    "CN": {
        "export_val": 1248.0, "import_val": 1428.0, "balance": -180.0,
        "top_exports": ["메모리 반도체", "합성수지", "평판 디스플레이"],
        "top_imports": ["배터리 원자재(리튬 등)", "컴퓨터 부품", "의류/정밀화학"]
    },
    "VN": {
        "export_val": 535.0, "import_val": 260.0, "balance": 275.0,
        "top_exports": ["전자부품/반도체", "평판 디스플레이", "무선통신기기 부품"],
        "top_imports": ["무선전화기 완성품", "의류", "신발"]
    },
    "JP": {
        "export_val": 290.0, "import_val": 476.0, "balance": -186.0,
        "top_exports": ["석유제품", "철강판", "정밀화학원료"],
        "top_imports": ["반도체 제조장비", "정밀 화학원료(소부장)", "특수 플라스틱"]
    },
    "EU": {
        "export_val": 680.0, "import_val": 725.0, "balance": -45.0,
        "top_exports": ["자동차/전기차", "선박해양플랜트", "이차전지"],
        "top_imports": ["정밀기계", "의약품/백신", "수입 승용차"]
    },
    "AU": {
        "export_val": 182.0, "import_val": 324.0, "balance": -142.0,
        "top_exports": ["정제 석유제품", "자동차", "건설기계"],
        "top_imports": ["철광석", "석탄", "천연가스(LNG)"]
    },
    "GB": {
        "export_val": 61.0, "import_val": 58.0, "balance": 3.0,
        "top_exports": ["선박", "자동차", "제트유"],
        "top_imports": ["원유", "의약품", "항공우주 부품"]
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
# 6. 상단 헤더 및 목적 가이드
# -----------------------------------------------------------------------------
st.title("🌐 글로벌 환율 & 무역 파트너 적합도 분석")
st.caption("USD 기준 장기 환율 변동 밴드와 거시경제(GDP·GNI), 대외 무역 수지를 결합한 데이터 기반 의사결정 대시보드")

with st.expander("📌 [필독] 대시보드 기획 목적 및 분석 체계", expanded=False):
    st.markdown("""
    - **목적**: 해외 진출 및 원자재 소싱 시 단순 가격이 아닌 **환율 변동 밴드 리스크**와 **국가 펀더멘털**, **실제 대한(對韓) 무역 밸런스**를 통합 검증
    - **4대 분석 축**: 통화 안정성(30%), 시장 규모(30%), 구매력(20%), 대외 개방도(20%)
    - **기업별 행동 요령**: 환율 강/약세 시나리오에 따라 [수출 기업]과 [수입 기업]의 맞춤형 대응 플랜 분리 제공
    """)

# -----------------------------------------------------------------------------
# 7. 사이드바 및 환율 데이터 로드
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ 국가 선택")
selected_country_code = st.sidebar.selectbox(
    "분석 대상 교역국",
    options=list(COUNTRY_METADATA.keys()),
    format_func=lambda x: COUNTRY_METADATA[x]["name"],
    index=0
)

country_info = COUNTRY_METADATA[selected_country_code]
trade_info = KOREA_TRADE_STATS[selected_country_code]
target_currency = country_info["currency"]

live_rates, _ = get_live_exchange_rates(EXCHANGE_KEY)
fallback_rates = {"KRW": 1350.0, "JPY": 152.0, "CNY": 7.25, "USD": 1.0, "EUR": 0.92, "GBP": 0.78, "AUD": 1.50, "VND": 25400.0}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates
current_rate = rates_dict.get(target_currency, fallback_rates.get(target_currency, 1.0))

# -----------------------------------------------------------------------------
# 8. [전진 배치] 심플 실시간 환율 계산기 (보내는/받는 통화 선택 제거, 자동 연동)
# -----------------------------------------------------------------------------
st.subheader("💱 실시간 환율 계산기 (Live Currency Converter)")

with st.container(border=True):
    col_calc_input, col_calc_result1, col_calc_result2 = st.columns([1.2, 1.4, 1.4])
    
    with col_calc_input:
        st.markdown(f"**📍 선택 국가 통화 ({target_currency})**")
        input_amount = st.number_input(
            "금액 입력",
            min_value=0.0,
            value=1000.0,
            step=100.0,
            format="%.2f",
            label_visibility="collapsed"
        )
        st.caption(f"현재 선택된 국가: **{country_info['name']}**")

    # 환율 계산 로직 (USD 기준 크로스 계산)
    # 1 USD 당 target_currency 비율 = current_rate
    # 따라서 target_currency 1단위 = (1 / current_rate) USD
    # KRW 환산: target_currency 1단위 = (rates_dict['KRW'] / current_rate) KRW
    rate_usd_per_target = rates_dict.get("USD", 1.0) / current_rate
    rate_krw_per_target = rates_dict.get("KRW", 1350.0) / current_rate

    val_usd = input_amount * rate_usd_per_target
    val_krw = input_amount * rate_krw_per_target

    with col_calc_result1:
        st.markdown("**💵 미화 환산 (USD)**")
        st.metric(
            label="USD 변환 금액",
            value=f"${val_usd:,.2f} USD",
            delta=f"1 {target_currency} = ${rate_usd_per_target:,.4f}"
        )

    with col_calc_result2:
        st.markdown("**🇰🇷 원화 환산 (KRW)**")
        st.metric(
            label="KRW 변환 금액",
            value=f"{val_krw:,.2f} KRW",
            delta=f"1 {target_currency} = ₩{rate_krw_per_target:,.2f}"
        )

st.divider()

# -----------------------------------------------------------------------------
# 9. 📊 무역 적합도 스코어카드 & 韓-대상국 무역 팩트시트
# -----------------------------------------------------------------------------
years = [2021, 2022, 2023, 2024, 2025]
np.random.seed(hash(selected_country_code) % 100)
fluct = [1.05, 1.02, 0.98, 1.01, 1.0] if target_currency != "USD" else [1.0, 1.0, 1.0, 1.0, 1.0]
sim_rates = [round(current_rate * f, 2) for f in fluct]

high_rates = [round(r * 1.04, 2) for r in sim_rates]
low_rates = [round(r * 0.96, 2) for r in sim_rates]

macro_data = MACRO_HISTORICAL_DATA[selected_country_code]
latest_gdp = macro_data["gdp"][-1]
latest_gni = macro_data["gni"][-1]

rate_volatility = np.std(sim_rates) / np.mean(sim_rates) * 100
volatility_score = max(0, 100 - (rate_volatility * 10))
gdp_score = min(100, (latest_gdp / 25.0) * 100)
gni_score = min(100, (latest_gni / 80000) * 100)
openness_score = country_info["openness"]
total_score = round((volatility_score * 0.3) + (gdp_score * 0.3) + (gni_score * 0.2) + (openness_score * 0.2), 1)

if total_score >= 80:
    grade = "S 등급 (최우수 파트너)"
elif total_score >= 70:
    grade = "A 등급 (우수 파트너)"
elif total_score >= 60:
    grade = "B 등급 (조건부 협력)"
else:
    grade = "C 등급 (고위험 주의)"

st.subheader(f"📊 [{country_info['name']}] 무역 적합도 & 대외 교역 팩트시트")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("종합 적합도 등급", total_score, delta=grade)
balance_sign = "+" if trade_info["balance"] > 0 else ""
m_col2.metric("대(對)한국 무역수지", f"{balance_sign}{trade_info['balance']:,.0f} 억 달러", delta="흑자국" if trade_info["balance"] > 0 else "적자국")
m_col3.metric("한국 대상 수출액 / 수입액", f"${trade_info['export_val']:,.0f}억 / ${trade_info['import_val']:,.0f}억")
m_col4.metric("외환 변동성 리스크", f"{rate_volatility:.2f}%", delta="안정권" if rate_volatility < 5 else "주의", delta_color="inverse")

with st.container(border=True):
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown(f"**📦 한국의 대(對){selected_country_code} 주요 수출 품목 TOP 3**")
        badges = " ".join([f"<span class='badge-export'>✓ {item}</span>" for item in trade_info["top_exports"]])
        st.markdown(badges, unsafe_allow_html=True)
    with p_col2:
        st.markdown(f"**📥 한국의 대(對){selected_country_code} 주요 수입 품목 TOP 3**")
        badges = " ".join([f"<span class='badge-import'>✓ {item}</span>" for item in trade_info["top_imports"]])
        st.markdown(badges, unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# 10. 환율 변동 밴드 차트 vs 레이더 종합 진단
# -----------------------------------------------------------------------------
col_chart_left, col_chart_right = st.columns([1.1, 0.9], gap="large")

with col_chart_left:
    st.markdown("### 📈 USD 기준 환율 변동 밴드 (High-Low-Close)")
    st.caption("연도별 최고·최저 환율 밴드를 통해 현재 환율의 역사적 저평가/고평가 구간을 진단합니다.")

    df_band = pd.DataFrame({
        "Year": [str(y) for y in years],
        "Mean": sim_rates,
        "High": high_rates,
        "Low": low_rates
    })

    fig_band = go.Figure()
    fig_band.add_trace(go.Scatter(
        x=df_band["Year"].tolist() + df_band["Year"].tolist()[::-1],
        y=df_band["High"].tolist() + df_band["Low"].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name="환율 변동 밴드 (High-Low)"
    ))
    fig_band.add_trace(go.Scatter(
        x=df_band["Year"],
        y=df_band["Mean"],
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        name=f"기준 환율 ({target_currency}/USD)"
    ))
    fig_band.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_band, use_container_width=True)

with col_chart_right:
    st.markdown("### 🕸️ 4대 무역 적합성 레이더(방사형) 진단")
    st.caption("국가의 펀더멘털과 외환 리스크의 균형도를 한눈에 평가합니다.")

    categories = ['환율 안정성', '시장 규모(GDP)', '소비 구매력(GNI)', '시장 개방도']
    values = [volatility_score, gdp_score, gni_score, openness_score]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(46, 125, 50, 0.25)',
        line=dict(color='#2e7d32', width=2),
        name=country_info['name']
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=340,
        margin=dict(l=30, r=30, t=30, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# 11. 수출 기업 vs 수입 기업 맞춤형 액션 플랜
# -----------------------------------------------------------------------------
st.subheader("🧭 기업별 맞춤형 무역 의사결정 가이드")
st.caption("환율 흐름 및 거시 체력에 따라 수출 지향 기업과 수입 지향 기업이 취해야 할 구체적 실행 지침입니다.")

tab_export, tab_import = st.tabs(["🚀 [수출 기업 관점] 진출 및 결제 전략", "📦 [수입 기업 관점] 원자재 소싱 및 환헤지 전략"])

with tab_export:
    c_ex1, c_ex2 = st.columns([1, 1], gap="medium")
    with c_ex1:
        with st.container(border=True):
            st.markdown("#### 💡 **현지 가격 경쟁력 및 결제 통화 지침**")
            if target_currency == "USD" or rate_volatility < 5.0:
                st.success("✔️ **달러화 결제(USD) 강력 추천**: 기축통화 결제를 통해 환전 수수료를 최소화하고 안정적인 영업 마진 확보가 가능합니다.")
            else:
                st.warning("⚠️ **선물환 매도 헷징 필수**: 현지 통화 변동성이 감지되므로 대금 수령 주기를 단축하거나 단가 연동 조항을 삽입하세요.")
            st.markdown(f"- **추천 공략 품목**: {', '.join(trade_info['top_exports'])}")
    with c_ex2:
        with st.container(border=True):
            st.markdown("#### 📈 **현지 시장 소비 구매력 진단**")
            if latest_gni > 35000:
                st.info("💎 **고부가가치 프리미엄 제품 진입 적합**: 1인당 GNI가 높아 브랜드 가치 기반의 고단가 제품 수출이 유망합니다.")
            else:
                st.info("⚖️ **가성비 및 볼륨 중심 판매 전략 권장**: 소득 수준에 맞춘 현지화 패키징과 가격 탄력성 중심의 마케팅이 유리합니다.")

with tab_import:
    c_im1, c_im2 = st.columns([1, 1], gap="medium")
    with c_im1:
        with st.container(border=True):
            st.markdown("#### 🏭 **원자재 및 부품 소싱 단가 관리**")
            st.markdown(f"""
            - **핵심 수입 부문**: `{', '.join(trade_info['top_imports'])}`
            - **현지 통화 약세 시**: 부품 수입 단가가 원화 기준 하락하므로 장기 공급 계약 체결의 최적기입니다.
            - **현지 통화 강세 시**: 수입 원가 상승 압력이 발생하므로 제3국 대체 공급선 다변화를 검토하세요.
            """)
    with c_im2:
        with st.container(border=True):
            st.markdown("#### 🛡️ **결제 리스크 방어 솔루션**")
            st.markdown(f"""
            - **환리스크 신호등**: **{'🟢 안정' if rate_volatility < 5 else '🟡 변동 주의' if rate_volatility < 10 else '🔴 고위험'}**
            - **외환 개방도**: `{openness_score}/100` (외환 결제 건전성 우수)
            - **행동 요령**: 환율 상한선(Cap)을 설정하는 통화옵션 또는 선물환 매수 계약 체결 권장.
            """)