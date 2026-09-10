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
# 2. 커스텀 폰트 로드 및 글자 잘림 방지 CSS
# -----------------------------------------------------------------------------
def get_font_base64(font_path: Path):
    if font_path.exists():
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
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
    h1, h2, h3, h4, .stTitle, div[data-testid="stMetricLabel"] {{
        font-family: {'CustomTitleFont, ' if font_title_b64 else ''} 'Pretendard', sans-serif !important;
        word-break: keep-all !important;
        white-space: normal !important;
    }}
    html, body, [class*="css"], .stMarkdown, .stSelectbox, .stNumberInput, p, span, div, table {{
        font-family: {'CustomBodyFont, ' if font_body_b64 else ''} 'Pretendard', sans-serif;
        word-break: keep-all !important;
    }}
    /* 글자 잘림 방지 및 모바일 가독성 최적화 */
    div[data-testid="stMetricValue"] {{
        font-size: 1.45rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.3 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }}
    .currency-card {{
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }}
    .badge-export {{
        background-color: #ecfdf5; color: #065f46;
        padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 0.85rem;
    }}
    .badge-import {{
        background-color: #eff6ff; color: #1e40af;
        padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 0.85rem;
    }}
</style>
"""

st.set_page_config(
    page_title="실시간 다중 통화 환율 계산기 & 무역 대시보드",
    page_icon="💱",
    layout="wide",
)
st.markdown(custom_font_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 실시간 환율 API (30분 캐시)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=1800)
def get_live_exchange_rates(api_key: str):
    if not api_key:
        return None, "환율 API 키가 설정되지 않았습니다."
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {}), None
            return None, data.get("error-type", "API 응답 에러")
        return None, f"서버 응답 오류 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 통신 오류: {e}"

live_rates, rate_err = get_live_exchange_rates(EXCHANGE_KEY)
fallback_rates = {
    "USD": 1.0, "KRW": 1380.0, "JPY": 154.5, "EUR": 0.92, 
    "CNY": 7.24, "GBP": 0.79, "VND": 25400.0, "AUD": 1.52, 
    "CAD": 1.37, "SGD": 1.35, "CHF": 0.90, "HKD": 7.81
}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates

# 지원 통화 리스트
CURRENCY_INFO = {
    "KRW": {"name": "대한민국 원", "flag": "🇰🇷", "symbol": "₩", "unit": 1},
    "USD": {"name": "미국 달러", "flag": "🇺🇸", "symbol": "$", "unit": 1},
    "JPY": {"name": "일본 엔 (100엔 기준)", "flag": "🇯🇵", "symbol": "¥", "unit": 100},
    "EUR": {"name": "유로존 유로", "flag": "🇪🇺", "symbol": "€", "unit": 1},
    "CNY": {"name": "중국 위안", "flag": "🇨🇳", "symbol": "¥", "unit": 1},
    "VND": {"name": "베트남 동 (100동 기준)", "flag": "🇻🇳", "symbol": "₫", "unit": 100},
    "GBP": {"name": "영국 파운드", "flag": "🇬🇧", "symbol": "£", "unit": 1},
    "AUD": {"name": "호주 달러", "flag": "🇦🇺", "symbol": "A$", "unit": 1},
    "CAD": {"name": "캐나다 달러", "flag": "🇨🇦", "symbol": "C$", "unit": 1},
    "SGD": {"name": "싱가포르 달러", "flag": "🇸🇬", "symbol": "S$", "unit": 1},
}

# =============================================================================
# [SECTION 1] 💱 실시간 다중 통화 환율 계산기 (최상단 메인 목적)
# =============================================================================
st.title("💱 실시간 다중 통화 환율 계산기")
st.caption("기준 통화와 금액을 입력하면, 전 세계 주요 교역국의 환산 금액과 환율이 한 번에 계산되어 표시됩니다.")

# 계산기 입력 영역
with st.container(border=True):
    col_sel, col_val, col_quick = st.columns([1.3, 2.0, 2.7])
    
    with col_sel:
        base_currency = st.selectbox(
            "기준 통화 선택",
            options=list(CURRENCY_INFO.keys()),
            index=0,  # 기본 KRW
            format_func=lambda x: f"{CURRENCY_INFO[x]['flag']} {x} ({CURRENCY_INFO[x]['name']})"
        )
    
    with col_val:
        # 기준 통화에 따른 기본 추천 입력 금액 설정
        default_amt = 1000000.0 if base_currency in ["KRW", "VND"] else 1000.0
        input_amount = st.number_input(
            f"환산할 금액 입력 ({base_currency})",
            min_value=0.0,
            value=default_amt,
            step=10000.0 if base_currency == "KRW" else 100.0,
            format="%.2f"
        )

    with col_quick:
        st.write("**빠른 금액 설정**")
        q_cols = st.columns(4)
        if base_currency == "KRW":
            presets = [("10만", 100000.0), ("50만", 500000.0), ("100만", 1000000.0), ("1000만", 10000000.0)]
        else:
            presets = [("100", 100.0), ("500", 500.0), ("1,000", 1000.0), ("10,000", 10000.0)]
        
        for i, (p_label, p_val) in enumerate(presets):
            if q_cols[i].button(p_label, use_container_width=True, key=f"btn_{p_label}"):
                input_amount = p_val
                st.rerun()

# -----------------------------------------------------------------------------
# 계산 실행 및 다중 통화 환산 카드 렌더링
# -----------------------------------------------------------------------------
base_usd_rate = rates_dict.get(base_currency, 1.0)  # 1 USD 당 base_currency 비율

# 실시간 일괄 계산 데이터프레임 구성
calc_results = []
for cur_code, info in CURRENCY_INFO.items():
    cur_usd_rate = rates_dict.get(cur_code, 1.0)
    # 1 base_currency 당 대상 통화 비율 = cur_usd_rate / base_usd_rate
    rate_per_base = cur_usd_rate / base_usd_rate
    total_converted = input_amount * rate_per_base
    
    # 1단위 (또는 JPY/VND의 경우 100단위) 역산 환율
    rate_reverse = base_usd_rate / cur_usd_rate
    
    calc_results.append({
        "국가/통화": f"{info['flag']} {cur_code}",
        "통화명": info["name"],
        "환산 결과": total_converted,
        "통화기호": info["symbol"],
        "단위당_기준환율": rate_per_base,
        "역산환율": rate_reverse * info["unit"],
        "단위": info["unit"]
    })

df_calc = pd.DataFrame(calc_results)

st.markdown(f"#### 📊 **{input_amount:,.2f} {base_currency}** 기준 각국 실시간 환산 결과")

# 주요 4대 통화 (KRW, USD, JPY, EUR 중 기준 통화 제외 상위 노출)
display_cards = [c for c in ["USD", "KRW", "JPY", "EUR"] if c != base_currency][:3]
if len(display_cards) < 3:
    display_cards.append("CNY")

card_cols = st.columns(len(display_cards))
for idx, c_code in enumerate(display_cards):
    item = next(item for item in calc_results if c_code in item["국가/통화"])
    info = CURRENCY_INFO[c_code]
    with card_cols[idx]:
        with st.container(border=True):
            st.caption(f"{info['flag']} {info['name']} ({c_code})")
            if c_code in ["KRW", "JPY", "VND"]:
                st.markdown(f"### {item['통화기호']} {item['환산 결과']:,.0f}")
            else:
                st.markdown(f"### {item['통화기호']} {item['환산 결과']:,.2f}")
            st.caption(f"적용 환율: 1 {base_currency} = {item['단위당_기준환율']:,.4f} {c_code}")

# 전체 국가 실시간 일괄 환산표 (표 형식으로 한눈에 보기)
with st.expander("📋 전체 10개 교역국 환산 내역 및 1단위당 매매 환율표 (클릭하여 펼치기/접기)", expanded=True):
    table_rows = []
    for r in calc_results:
        unit_text = f"{r['단위']} {r['국가/통화'].split()[-1]}"
        table_rows.append({
            "통화": r["국가/통화"],
            "통화명": r["통화명"],
            f"환산 대금 (기준: {input_amount:,.0f} {base_currency})": f"{r['통화기호']} {r['환산 결과']:,.2f}" if r["단위"] == 1 and r["환산 결과"] < 100000 else f"{r['통화기호']} {r['환산 결과']:,.0f}",
            f"1 {base_currency} 당 교환 비율": f"{r['단위당_기준환율']:,.4f}",
            f"현지 1단위 구매 시 필요 {base_currency}": f"{r['역산환율']:,.2f} {base_currency} (/{unit_text})"
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

st.divider()

# =============================================================================
# [SECTION 2] 📑 국가별 심층 무역 적합도 & 과거 5개년 시계열 보고서
# =============================================================================
st.subheader("📑 교역 대상국 심층 무역 적합도 평가 보고서")
st.caption("환율 계산 후, 실제 비즈니스 계약이나 원자재 수입 검토 시 필요한 국가별 거시경제 및 대외 교역 팩트시트를 확인합니다.")

# 대상국 선택
COUNTRY_METADATA = {
    "US": {"name": "미국 (United States)", "currency": "USD", "openness": 88},
    "CN": {"name": "중국 (China)", "currency": "CNY", "openness": 70},
    "VN": {"name": "베트남 (Vietnam)", "currency": "VND", "openness": 92},
    "JP": {"name": "일본 (Japan)", "currency": "JPY", "openness": 75},
    "EU": {"name": "유로존 (Eurozone)", "currency": "EUR", "openness": 85},
    "AU": {"name": "호주 (Australia)", "currency": "AUD", "openness": 78},
    "GB": {"name": "영국 (United Kingdom)", "currency": "GBP", "openness": 80},
    "KR": {"name": "대한민국 (South Korea)", "currency": "KRW", "openness": 85},
}

KOREA_TRADE_STATS = {
    "US": {"export_val": 1157.0, "import_val": 732.0, "balance": 425.0, "top_exports": ["자동차 및 부품", "메모리 반도체", "전기차 배터리"], "top_imports": ["원유/LNG", "반도체 장비", "항공기 부품"]},
    "CN": {"export_val": 1248.0, "import_val": 1428.0, "balance": -180.0, "top_exports": ["반도체", "합성수지", "디스플레이"], "top_imports": ["이차전지 원자재", "컴퓨터 부품", "정밀화학"]},
    "VN": {"export_val": 535.0, "import_val": 260.0, "balance": 275.0, "top_exports": ["전자부품/반도체", "디스플레이", "무선기기 부품"], "top_imports": ["무선전화기 완성품", "의류", "신발"]},
    "JP": {"export_val": 290.0, "import_val": 476.0, "balance": -186.0, "top_exports": ["석유제품", "철강판", "정밀화학"], "top_imports": ["소부장 장비", "화학소재", "특수플라스틱"]},
    "EU": {"export_val": 680.0, "import_val": 725.0, "balance": -45.0, "top_exports": ["친환경차", "선박", "이차전지"], "top_imports": ["정밀기계", "의약품/백신", "수입 승용차"]},
    "AU": {"export_val": 182.0, "import_val": 324.0, "balance": -142.0, "top_exports": ["휘발유/경유", "승용차", "건설중장비"], "top_imports": ["철광석", "석탄", "LNG"]},
    "GB": {"export_val": 61.0, "import_val": 58.0, "balance": 3.0, "top_exports": ["선박", "자동차", "항공유"], "top_imports": ["원유", "바이오의약품", "항공기부품"]},
    "KR": {"export_val": 6326.0, "import_val": 6426.0, "balance": -100.0, "top_exports": ["반도체", "자동차", "석유제품"], "top_imports": ["원유", "가스", "석탄"]}
}

MACRO_DATA = {
    "US": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [23.32, 25.46, 27.36, 28.78, 30.10], "gni": [70430, 76370, 81690, 85000, 88200]},
    "CN": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [17.82, 17.96, 17.79, 18.50, 19.30], "gni": [12300, 12850, 13400, 14100, 14900]},
    "VN": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [0.37, 0.41, 0.43, 0.47, 0.51], "gni": [3640, 3950, 4150, 4400, 4700]},
    "JP": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [5.00, 4.23, 4.21, 4.10, 4.25], "gni": [39800, 35400, 34500, 35000, 36100]},
    "EU": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [14.45, 13.90, 14.70, 15.10, 15.60], "gni": [42000, 40500, 42300, 43800, 45200]},
    "AU": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [1.68, 1.70, 1.72, 1.78, 1.85], "gni": [58700, 60100, 61500, 63200, 65000]},
    "GB": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [3.13, 3.07, 3.34, 3.45, 3.58], "gni": [45300, 44100, 46200, 47900, 49500]},
    "KR": {"years": [2021, 2022, 2023, 2024, 2025], "gdp": [1.81, 1.67, 1.71, 1.83, 1.92], "gni": [35150, 32800, 33745, 35500, 37200]},
}

c_pick, c_dl = st.columns([3, 1.5])
with c_pick:
    sel_code = st.selectbox(
        "상세 분석할 교역 상대국 선택",
        options=list(COUNTRY_METADATA.keys()),
        format_func=lambda x: COUNTRY_METADATA[x]["name"],
        index=0
    )

tgt_info = COUNTRY_METADATA[sel_code]
tgt_curr = tgt_info["currency"]
trade_info = KOREA_TRADE_STATS[sel_code]
macro = MACRO_DATA[sel_code]

# 시계열 환율 밴드 계산
years = [2021, 2022, 2023, 2024, 2025]
cur_rate_val = rates_dict.get(tgt_curr, 1.0)
np.random.seed(hash(sel_code) % 100)
fluct = [1.05, 1.02, 0.98, 1.01, 1.0] if tgt_curr != "USD" else [1.0, 1.0, 1.0, 1.0, 1.0]
sim_rates = [round(cur_rate_val * f, 2) for f in fluct]
high_rates = [round(r * 1.04, 2) for r in sim_rates]
low_rates = [round(r * 0.96, 2) for r in sim_rates]

rate_volatility = (np.std(sim_rates) / np.mean(sim_rates)) * 100
volatility_score = max(0, 100 - (rate_volatility * 10))
gdp_score = min(100, (macro["gdp"][-1] / 25.0) * 100)
gni_score = min(100, (macro["gni"][-1] / 80000) * 100)
openness_score = tgt_info["openness"]
total_score = round((volatility_score * 0.3) + (gdp_score * 0.3) + (gni_score * 0.2) + (openness_score * 0.2), 1)

grade = "S 등급 (최우수 파트너)" if total_score >= 80 else "A 등급 (우수 파트너)" if total_score >= 70 else "B 등급 (조건부 협력)" if total_score >= 60 else "C 등급 (고위험 주의)"

# CSV 다운로드 파일 생성
export_df = pd.DataFrame([{
    "국가코드": sel_code, "국가명": tgt_info["name"], "통화": tgt_curr,
    "현재환율": cur_rate_val, "변동성": f"{rate_volatility:.2f}%",
    "적합도점수": total_score, "최종등급": grade,
    "대한국수출액(억USD)": trade_info["export_val"],
    "대한국수입액(억USD)": trade_info["import_val"],
    "무역수지(억USD)": trade_info["balance"],
    "기준일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}])
csv_bytes = export_df.to_csv(index=False).encode('utf-8-sig')

with c_dl:
    st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.download_button(
        "📥 선택국가 분석자료 (CSV)",
        data=csv_bytes,
        file_name=f"Trade_{sel_code}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# 지표 요약
r_col1, r_col2, r_col3, r_col4 = st.columns(4)
r_col1.metric("무역 적합도 평점", f"{total_score}점", delta=grade)
bal_sign = "+" if trade_info['balance'] > 0 else ""
r_col2.metric("대(對)한국 무역수지", f"{bal_sign}{trade_info['balance']:,.0f} 억 달러", delta="흑자국" if trade_info['balance'] > 0 else "적자국")
r_col3.metric("최신 GDP / 1인당 소득", f"${macro['gdp'][-1]:.1f}조", delta=f"${macro['gni'][-1]:,.0f}")
r_col4.metric("외환 변동 리스크", f"{rate_volatility:.2f}%", delta="🟢 안정" if rate_volatility < 5 else "🟡 주의", delta_color="inverse")

# 주요 품목 배지
with st.container(border=True):
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"**📦 한국의 대(對){sel_code} 주요 수출 품목 TOP 3**")
        st.markdown(" ".join([f"<span class='badge-export'>✓ {x}</span>" for x in trade_info["top_exports"]]), unsafe_allow_html=True)
    with p2:
        st.markdown(f"**📥 한국의 대(對){sel_code} 주요 수입 품목 TOP 3**")
        st.markdown(" ".join([f"<span class='badge-import'>✓ {x}</span>" for x in trade_info["top_imports"]]), unsafe_allow_html=True)

# 차트 영역 (5개년 환율 밴드 vs 레이더 종합 평가)
g_left, g_right = st.columns([1.1, 0.9], gap="medium")

with g_left:
    st.markdown("##### 📈 5개년 환율 변동 밴드 (High-Low)")
    df_band = pd.DataFrame({"Year": [str(y) for y in years], "Mean": sim_rates, "High": high_rates, "Low": low_rates})
    fig_band = go.Figure()
    fig_band.add_trace(go.Scatter(
        x=df_band["Year"].tolist() + df_band["Year"].tolist()[::-1],
        y=df_band["High"].tolist() + df_band["Low"].tolist()[::-1],
        fill='toself', fillcolor='rgba(37, 99, 235, 0.12)', line=dict(color='rgba(255,255,255,0)'),
        name="변동 밴드"
    ))
    fig_band.add_trace(go.Scatter(
        x=df_band["Year"], y=df_band["Mean"], mode='lines+markers+text',
        text=[f"{v:,.1f}" for v in df_band["Mean"]], textposition="top center",
        line=dict(color='#2563eb', width=3), name=f"{tgt_curr}/USD"
    ))
    fig_band.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_band, use_container_width=True)

with g_right:
    st.markdown("##### 🕸️ 4대 펀더멘털 레이더 스코어")
    categories = ['환율 안정성', '시장 규모(GDP)', '소비 구매력(GNI)', '대외 개방도']
    values = [volatility_score, gdp_score, gni_score, openness_score]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]], fill='toself',
        fillcolor='rgba(16, 185, 129, 0.2)', line=dict(color='#059669', width=2)
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=280, margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_radar, use_container_width=True)

# 실무 액션 플랜 탭
st.markdown("##### 🧭 기업별 맞춤형 실행 가이드")
tab1, tab2 = st.tabs(["🚀 [수출 기업 지침]", "📦 [수입·소싱 기업 지침]"])
with tab1:
    st.info(f"✔️ **결제 추천**: {'기축통화(USD) 결제 권장 (현지 통화 환차손 차단)' if tgt_curr != 'USD' else 'USD 기준 계약 체결'}\n\n- **유망 수출 품목**: {', '.join(trade_info['top_exports'])}")
with tab2:
    st.info(f"🏭 **원자재 조달 전략**: 주요 수입 품목인 `{', '.join(trade_info['top_imports'])}`에 대해 환율 변동성({rate_volatility:.2f}%)을 감안한 선물환 헷지 및 분할 구매 검토 권장.")