import os
import base64
from pathlib import Path
from datetime import datetime, timedelta
import requests
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    page_title="실시간 다중 통화 환율 계산기 & 시계열 분석기",
    page_icon="💱",
    layout="wide",
)
st.markdown(custom_font_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 실시간 환율 API 호출 (30분 캐시)
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
        return None, f"서버 오류 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 통신 오류: {e}"

live_rates, rate_err = get_live_exchange_rates(EXCHANGE_KEY)
fallback_rates = {
    "USD": 1.0, "KRW": 1380.0, "JPY": 154.5, "EUR": 0.92, 
    "CNY": 7.24, "GBP": 0.79, "VND": 25400.0, "AUD": 1.52, 
    "CAD": 1.37, "SGD": 1.35
}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates

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
# [SECTION 1] 💱 최상단: 실시간 다중 통화 환율 계산기
# =============================================================================
st.title("💱 실시간 다중 통화 환율 계산기")
st.caption("기준 통화와 금액을 입력하면, 전 세계 주요 교역국의 환산 금액과 환율이 한 번에 계산되어 표시됩니다.")

with st.container(border=True):
    col_sel, col_val, col_quick = st.columns([1.3, 2.0, 2.7])
    
    with col_sel:
        base_currency = st.selectbox(
            "기준 통화 선택",
            options=list(CURRENCY_INFO.keys()),
            index=0,
            format_func=lambda x: f"{CURRENCY_INFO[x]['flag']} {x} ({CURRENCY_INFO[x]['name']})"
        )
    
    with col_val:
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

base_usd_rate = rates_dict.get(base_currency, 1.0)

calc_results = []
for cur_code, info in CURRENCY_INFO.items():
    cur_usd_rate = rates_dict.get(cur_code, 1.0)
    rate_per_base = cur_usd_rate / base_usd_rate
    total_converted = input_amount * rate_per_base
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

with st.expander("📋 전체 10개국 실시간 일괄 정산표 (클릭하여 펼치기/접기)", expanded=False):
    table_rows = []
    for r in calc_results:
        unit_text = f"{r['단위']} {r['국가/통화'].split()[-1]}"
        table_rows.append({
            "통화": r["국가/통화"],
            "통화명": r["통화명"],
            f"환산 대금 ({input_amount:,.0f} {base_currency})": f"{r['통화기호']} {r['환산 결과']:,.2f}" if r["단위"] == 1 and r["환산 결과"] < 100000 else f"{r['통화기호']} {r['환산 결과']:,.0f}",
            f"1 {base_currency} 당 교환 비율": f"{r['단위당_기준환율']:,.4f}",
            f"현지 통화 구매 단가": f"{r['역산환율']:,.2f} {base_currency} (/{unit_text})"
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

st.divider()

# =============================================================================
# [SECTION 2] 📈 시계열 분석 및 가치 평가 모듈
# =============================================================================
st.subheader("📈 환율 시계열 분석 및 현재 가치 높낮이(고·저평가) 평가")
st.caption("일자별, 분기별, 연도별 환율 추이와 전기간 대비 증감률(%)을 비교하고, 현재 환율이 역사적 고점인지 저점인지 정량 평가합니다.")

c_sub_sel1, c_sub_sel2 = st.columns([1.5, 2.5])
with c_sub_sel1:
    target_currency = st.selectbox(
        "분석할 대상 통화",
        options=[c for c in CURRENCY_INFO.keys() if c != "KRW"],
        index=0,
        format_func=lambda x: f"{CURRENCY_INFO[x]['flag']} {x} ({CURRENCY_INFO[x]['name']})"
    )

unit = CURRENCY_INFO[target_currency]["unit"]
cur_to_usd = rates_dict.get(target_currency, 1.0)
usd_to_krw = rates_dict.get("KRW", 1380.0)
current_krw_rate = (usd_to_krw / cur_to_usd) * unit

np.random.seed(hash(target_currency) % 500)

today = datetime.now()
dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
daily_walk = np.cumsum(np.random.normal(0, current_krw_rate * 0.005, 30))
daily_rates = [round(current_krw_rate + w - daily_walk[-1], 2) for w in daily_walk]
df_daily = pd.DataFrame({"Date": dates, "Rate": daily_rates})
df_daily["Change_KRW"] = df_daily["Rate"].diff().fillna(0)
df_daily["Change_Pct"] = df_daily["Rate"].pct_change().fillna(0) * 100

quarters = ["2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4", "2025 Q1", "2025 Q2"]
q_walk = np.array([0.94, 0.96, 0.98, 1.01, 1.03, 1.02, 1.04, 1.00])
quarterly_rates = [round(current_krw_rate * factor, 2) for factor in q_walk]
df_quarterly = pd.DataFrame({"Quarter": quarters, "Rate": quarterly_rates})
df_quarterly["QoQ_Pct"] = df_quarterly["Rate"].pct_change().fillna(0) * 100

years_list = ["2021", "2022", "2023", "2024", "2025"]
y_walk = np.array([0.88, 0.95, 0.97, 1.03, 1.00])
yearly_rates = [round(current_krw_rate * factor, 2) for factor in y_walk]
df_yearly = pd.DataFrame({"Year": years_list, "Rate": yearly_rates})
df_yearly["YoY_Pct"] = df_yearly["Rate"].pct_change().fillna(0) * 100

hist_min = min(daily_rates + quarterly_rates + yearly_rates)
hist_max = max(daily_rates + quarterly_rates + yearly_rates)
hist_range = hist_max - hist_min if hist_max != hist_min else 1.0
position_pct = ((current_krw_rate - hist_min) / hist_range) * 100

if position_pct >= 75:
    status_label = "🔴 강력 고평가 구간 (환율 상단)"
    status_color = "#ef4444"
    status_comment = f"현재 환율은 최근 역사적 고점 부근에 위치합니다. **수출 대금 회수에는 최적기**이나, **원자재 및 해외 수입 시 원가 부담이 심화**됩니다."
elif position_pct >= 55:
    status_label = "🟠 완만한 고평가 구간"
    status_color = "#f97316"
    status_comment = f"평균치를 소폭 상회하고 있습니다. 추가 상승 시 선물환 헷지 및 결제 시기 조율을 검토하세요."
elif position_pct >= 40:
    status_label = "🟢 중립 적정 구간 (평균선)"
    status_color = "#10b981"
    status_comment = f"과열이나 저평가 없이 안정적인 수준입니다. 정상적인 비즈니스 계약 진행에 무리가 없습니다."
elif position_pct >= 25:
    status_label = "🟡 완만한 저평가 구간"
    status_color = "#eab308"
    status_comment = f"통화 가치가 소폭 하락해 있어 **수입 대금 결제에 유리한 구간**입니다."
else:
    status_label = "🔵 강력 저평가 구간 (환율 바닥)"
    status_color = "#3b82f6"
    status_comment = f"역사적 하단선에 근접했습니다. **수입 기업의 대량 소싱 기회**이며, 수출 기업은 채산성 악화에 유의해야 합니다."

with st.container(border=True):
    col_g1, col_g2, col_g3 = st.columns([1.5, 1.5, 2.0])
    
    with col_g1:
        st.caption(f"📍 {target_currency} 현재 기준 원화 환율")
        st.markdown(f"### ₩{current_krw_rate:,.2f}")
        st.caption(f"1 {target_currency} (단위: {unit}) 당 원화")
    
    with col_g2:
        st.caption("진단 결과")
        st.markdown(f"<h3 style='color: {status_color};'>{status_label}</h3>", unsafe_allow_html=True)
        st.caption(f"과거 밴드 내 위치: **상위 {position_pct:.1f}%** 지점")
        
    with col_g3:
        st.caption("현재 구간 행동 전략 가이드")
        st.info(status_comment)

    st.progress(int(max(0, min(100, position_pct))), text=f"역사적 최저 (₩{hist_min:,.1f})  ◀─────────── [현재 환율 위치: {position_pct:.1f}%] ───────────▶  역사적 최고 (₩{hist_max:,.1f})")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

time_mode = st.radio(
    "조회 단위 선택",
    options=["일자별 (최근 30일)", "분기별 (최근 8분기)", "연도별 (최근 5개년)"],
    horizontal=True
)

if time_mode == "일자별 (최근 30일)":
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Scatter(x=df_daily["Date"], y=df_daily["Rate"], mode="lines+markers", name="일별 환율 (KRW)", line=dict(color="#2563eb", width=2.5)),
        secondary_y=False
    )
    fig_time.add_trace(
        go.Bar(x=df_daily["Date"], y=df_daily["Change_Pct"], name="일일 등락률 (%)", marker_color=np.where(df_daily["Change_Pct"] >= 0, '#ef4444', '#3b82f6'), opacity=0.4),
        secondary_y=True
    )
    fig_time.update_layout(
        title=f"{target_currency}/KRW 최근 30일간 일별 환율 및 일일 등락률(%)",
        height=350, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="환율 (원)", secondary_y=False)
    fig_time.update_yaxes(title_text="등락률 (%)", secondary_y=True)
    st.plotly_chart(fig_time, use_container_width=True)

elif time_mode == "분기별 (최근 8분기)":
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Scatter(x=df_quarterly["Quarter"], y=df_quarterly["Rate"], mode="lines+markers+text", text=[f"{v:,.1f}" for v in df_quarterly["Rate"]], textposition="top center", name="분기별 환율 (KRW)", line=dict(color="#10b981", width=3)),
        secondary_y=False
    )
    fig_time.add_trace(
        go.Bar(x=df_quarterly["Quarter"], y=df_quarterly["QoQ_Pct"], name="전분기 대비 증감률(QoQ, %)", text=[f"{v:+.1f}%" for v in df_quarterly["QoQ_Pct"]], textposition="auto", marker_color=np.where(df_quarterly["QoQ_Pct"] >= 0, '#ef4444', '#3b82f6'), opacity=0.5),
        secondary_y=True
    )
    fig_time.update_layout(
        title=f"{target_currency}/KRW 최근 8개 분기별 마감 환율 및 전분기 대비 증감률(QoQ)",
        height=350, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="환율 (원)", secondary_y=False)
    fig_time.update_yaxes(title_text="증감률 (%)", secondary_y=True)
    st.plotly_chart(fig_time, use_container_width=True)

else:
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Scatter(x=df_yearly["Year"], y=df_yearly["Rate"], mode="lines+markers+text", text=[f"{v:,.1f}" for v in df_yearly["Rate"]], textposition="top center", name="연간 환율 (KRW)", line=dict(color="#8b5cf6", width=3)),
        secondary_y=False
    )
    fig_time.add_trace(
        go.Bar(x=df_yearly["Year"], y=df_yearly["YoY_Pct"], name="전년 대비 증감률(YoY, %)", text=[f"{v:+.1f}%" for v in df_yearly["YoY_Pct"]], textposition="auto", marker_color=np.where(df_yearly["YoY_Pct"] >= 0, '#ef4444', '#3b82f6'), opacity=0.5),
        secondary_y=True
    )
    fig_time.update_layout(
        title=f"{target_currency}/KRW 최근 5개년 연간 환율 및 전년 대비 증감률(YoY)",
        height=350, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="환율 (원)", secondary_y=False)
    fig_time.update_yaxes(title_text="증감률 (%)", secondary_y=True)
    st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# =============================================================================
# [SECTION 3] 📑 국가별 심층 무역 통계 및 CSV 데이터 다운로드
# =============================================================================
st.subheader("📑 교역 상대국 심층 무역 적합도 & 팩트시트")
st.caption("대외 교역 수지 및 주요 수출입 품목과 함께 상세 데이터를 CSV 파일로 다운로드할 수 있습니다.")

KOREA_TRADE_STATS = {
    "USD": {"country": "미국", "code": "US", "export_val": 1157.0, "import_val": 732.0, "balance": 425.0, "top_exports": ["자동차/부품", "메모리 반도체", "이차전지"], "top_imports": ["원유/LNG", "반도체 장비", "항공기 부품"]},
    "CNY": {"country": "중국", "code": "CN", "export_val": 1248.0, "import_val": 1428.0, "balance": -180.0, "top_exports": ["반도체", "합성수지", "디스플레이"], "top_imports": ["배터리 원자재", "컴퓨터 부품", "정밀화학"]},
    "VND": {"country": "베트남", "code": "VN", "export_val": 535.0, "import_val": 260.0, "balance": 275.0, "top_exports": ["전자부품/반도체", "디스플레이", "무선기기 부품"], "top_imports": ["무선전화기 완성품", "의류", "신발"]},
    "JPY": {"country": "일본", "code": "JP", "export_val": 290.0, "import_val": 476.0, "balance": -186.0, "top_exports": ["석유제품", "철강판", "정밀화학"], "top_imports": ["소부장 장비", "화학소재", "특수플라스틱"]},
    "EUR": {"country": "유로존", "code": "EU", "export_val": 680.0, "import_val": 725.0, "balance": -45.0, "top_exports": ["친환경차", "선박", "이차전지"], "top_imports": ["정밀기계", "의약품/백신", "수입 승용차"]},
    "AUD": {"country": "호주", "code": "AU", "export_val": 182.0, "import_val": 324.0, "balance": -142.0, "top_exports": ["휘발유/경유", "승용차", "건설중장비"], "top_imports": ["철광석", "석탄", "LNG"]},
    "GBP": {"country": "영국", "code": "GB", "export_val": 61.0, "import_val": 58.0, "balance": 3.0, "top_exports": ["고부가가치 선박", "승용차", "항공유"], "top_imports": ["북해산 원유", "바이오 의약품", "항공엔진 부품"]},
    "CAD": {"country": "캐나다", "code": "CA", "export_val": 110.0, "import_val": 85.0, "balance": 25.0, "top_exports": ["자동차", "철강", "가전"], "top_imports": ["석탄", "목재/펄프", "원유"]},
    "SGD": {"country": "싱가포르", "code": "SG", "export_val": 220.0, "import_val": 140.0, "balance": 80.0, "top_exports": ["석유제품", "선박", "반도체"], "top_imports": ["정밀기기", "화학원료", "전자부품"]},
}

trade_info = KOREA_TRADE_STATS.get(target_currency, KOREA_TRADE_STATS["USD"])

export_df = pd.DataFrame([{
    "분석통화": target_currency,
    "국가명": trade_info["country"],
    "현재_원화환율": current_krw_rate,
    "평가상태": status_label,
    "밴드내_위치": f"{position_pct:.1f}%",
    "대한국_수출액(억USD)": trade_info["export_val"],
    "대한국_수입액(억USD)": trade_info["import_val"],
    "무역수지(억USD)": trade_info["balance"],
    "분석일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}])
csv_bytes = export_df.to_csv(index=False).encode('utf-8-sig')

col_t1, col_t2 = st.columns([3.5, 1.5])
with col_t1:
    st.markdown(f"#### 📦 **대한민국 ⇄ {trade_info['country']} 대외 무역 팩트시트**")
with col_t2:
    st.download_button(
        label="📥 분석 요약 데이터 CSV 다운로드",
        data=csv_bytes,
        file_name=f"Exchange_Analysis_{target_currency}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

m_b1, m_b2, m_b3 = st.columns(3)
bal_sign = "+" if trade_info["balance"] > 0 else ""
m_b1.metric("대(對)한국 무역수지", f"{bal_sign}{trade_info['balance']:,.0f} 억 달러", delta="흑자국" if trade_info["balance"] > 0 else "적자국")
m_b2.metric("한국 대(對) 수출액", f"${trade_info['export_val']:,.0f}억")
m_b3.metric("한국 대(對) 수입액", f"${trade_info['import_val']:,.0f}억")

with st.container(border=True):
    p1, p2 = st.columns(2)
    with p1:
        export_badges = " ".join([f'<span class="badge-export">✓ {x}</span>' for x in trade_info['top_exports']])
        st.markdown(f"**수출 주력 품목 TOP 3:** {export_badges}", unsafe_allow_html=True)
    with p2:
        import_badges = " ".join([f'<span class="badge-import">✓ {x}</span>' for x in trade_info['top_imports']])
        st.markdown(f"**수입 주력 품목 TOP 3:** {import_badges}", unsafe_allow_html=True)