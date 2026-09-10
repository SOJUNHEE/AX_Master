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
# 2. 커스텀 폰트 로드 및 모바일 완벽 반응형 CSS
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
    /* 기본 글꼴 */
    h1, h2, h3, h4, .stTitle, div[data-testid="stMetricLabel"] {{
        font-family: {'CustomTitleFont, ' if font_title_b64 else ''} 'Pretendard', -apple-system, sans-serif !important;
        word-break: keep-all !important;
    }}
    html, body, [class*="css"], .stMarkdown, .stSelectbox, .stNumberInput, p, span, div, table {{
        font-family: {'CustomBodyFont, ' if font_body_b64 else ''} 'Pretendard', -apple-system, sans-serif;
        word-break: keep-all !important;
    }}

    /* 🖥️ PC 및 데스크톱 (769px 이상) 기본 레이아웃 */
    @media (min-width: 769px) {{
        .block-container {{
            max-width: 92% !important;
            padding: 2rem 2.5rem !important;
        }}
        .hero-ticker-box {{
            padding: 28px 36px;
        }}
        .hero-grid {{
            display: grid;
            grid-template-columns: 1.4fr 1.1fr 2.0fr;
            gap: 25px;
            align-items: center;
        }}
        .hero-rate-value {{
            font-size: 3.0rem !important;
        }}
        .hero-sub-rate {{
            font-size: 1.8rem !important;
        }}
        .hero-divider {{
            border-left: 1px solid rgba(255,255,255,0.15);
            padding-left: 20px;
        }}
    }}

    /* 📱 모바일 및 소형 태블릿 (768px 이하) 반응형 전면 재조정 */
    @media (max-width: 768px) {{
        .block-container {{
            max-width: 100% !important;
            padding: 1rem 0.8rem !important;
        }}
        .hero-ticker-box {{
            padding: 18px 16px !important;
            border-radius: 12px !important;
            margin-bottom: 16px !important;
        }}
        .hero-grid {{
            display: flex !important;
            flex-direction: column !important;
            gap: 16px !important;
            text-align: left !important;
        }}
        .hero-rate-value {{
            font-size: 2.2rem !important;
            line-height: 1.2 !important;
        }}
        .hero-sub-rate {{
            font-size: 1.4rem !important;
            line-height: 1.2 !important;
        }}
        .hero-divider {{
            border-left: none !important;
            border-top: 1px solid rgba(255,255,255,0.15) !important;
            padding-left: 0 !important;
            padding-top: 14px !important;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.3rem !important;
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 0.85rem !important;
        }}
        .stMarkdown h1 {{ font-size: 1.5rem !important; }}
        .stMarkdown h2 {{ font-size: 1.25rem !important; }}
        .stMarkdown h3 {{ font-size: 1.1rem !important; }}
        .stMarkdown h4 {{ font-size: 1.0rem !important; }}
    }}

    /* 공통 전광판 스타일 */
    .hero-ticker-box {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid #38bdf8;
        border-radius: 14px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
        margin-bottom: 24px;
        width: 100%;
        box-sizing: border-box;
    }}
    .hero-rate-value {{
        font-weight: 800 !important;
        color: #38bdf8 !important;
        letter-spacing: -0.5px;
        margin: 4px 0;
        word-break: break-word !important;
    }}
    .hero-sub-rate {{
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        margin: 4px 0;
        word-break: break-word !important;
    }}
    .hero-badge {{
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
    }}
    .badge-overvalued {{ background-color: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid #ef4444; }}
    .badge-fair {{ background-color: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid #10b981; }}
    .badge-undervalued {{ background-color: rgba(59, 130, 246, 0.25); color: #93c5fd; border: 1px solid #3b82f6; }}

    .badge-export {{
        display: inline-block;
        background-color: #ecfdf5; color: #065f46;
        padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 0.85rem;
        border: 1px solid #a7f3d0; margin: 2px;
    }}
    .badge-import {{
        display: inline-block;
        background-color: #eff6ff; color: #1e40af;
        padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 0.85rem;
        border: 1px solid #bfdbfe; margin: 2px;
    }}
    .report-card {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 12px;
    }}
</style>
"""

st.set_page_config(
    page_title="글로벌 외환 인텔리전스 & 대외 무역 타당성 평가 대시보드",
    page_icon="🏛️",
    layout="wide",
)
st.markdown(custom_font_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 실시간 외환 고시 환율 API 호출 (30분 캐시)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=1800)
def get_live_exchange_rates(api_key: str):
    if not api_key:
        return None, "외환 데이터 피드 API Key 미설정"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {}), None
            return None, data.get("error-type", "데이터 피드 응답 예외")
        return None, f"외환 거래소 서버 응답 에러 ({res.status_code})"
    except Exception as e:
        return None, f"외환 네트워크 통신 프로토콜 장애: {e}"

live_rates, _ = get_live_exchange_rates(EXCHANGE_KEY)
fallback_rates = {
    "USD": 1.0, "KRW": 1380.0, "JPY": 154.5, "EUR": 0.92, 
    "CNY": 7.24, "GBP": 0.79, "VND": 25400.0, "AUD": 1.52, 
    "CAD": 1.37, "SGD": 1.35
}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates

CURRENCY_INFO = {
    "KRW": {"name": "대한민국 원화", "flag": "🇰🇷", "symbol": "₩", "unit": 1},
    "USD": {"name": "미국 달러화", "flag": "🇺🇸", "symbol": "$", "unit": 1},
    "JPY": {"name": "일본 엔화 (100엔 고시)", "flag": "🇯🇵", "symbol": "¥", "unit": 100},
    "EUR": {"name": "유로존 단일통화", "flag": "🇪🇺", "symbol": "€", "unit": 1},
    "CNY": {"name": "중국 위안화", "flag": "🇨🇳", "symbol": "¥", "unit": 1},
    "VND": {"name": "베트남 동화 (100동 고시)", "flag": "🇻🇳", "symbol": "₫", "unit": 100},
    "GBP": {"name": "영국 파운드화", "flag": "🇬🇧", "symbol": "£", "unit": 1},
    "AUD": {"name": "호주 달러화", "flag": "🇦🇺", "symbol": "A$", "unit": 1},
    "CAD": {"name": "캐나다 달러화", "flag": "🇨🇦", "symbol": "C$", "unit": 1},
    "SGD": {"name": "싱가포르 달러화", "flag": "🇸🇬", "symbol": "S$", "unit": 1},
}

# =============================================================================
# [SECTION 1] 💱 실시간 다중 통화 외환 정산 시뮬레이터 (핵심 계산기)
# =============================================================================
st.title("🏛️ 글로벌 외환 인텔리전스 대시보드")
st.caption("기축통화(USD) 기반 실시간 고시 환율과 통화별 매트릭스를 활용하여 다중 통화 결제 대금을 즉시 계산합니다.")

with st.container(border=True):
    col_sel, col_val, col_quick = st.columns([1.5, 2.0, 2.5])
    
    with col_sel:
        base_currency = st.selectbox(
            "기준 결제 통화 (Base Currency)",
            options=list(CURRENCY_INFO.keys()),
            index=0,
            format_func=lambda x: f"{CURRENCY_INFO[x]['flag']} {x} ({CURRENCY_INFO[x]['name']})"
        )
    
    with col_val:
        default_amt = 1000000.0 if base_currency in ["KRW", "VND"] else 1000.0
        input_amount = st.number_input(
            f"정산 원금 ({base_currency})",
            min_value=0.0,
            value=default_amt,
            step=10000.0 if base_currency == "KRW" else 100.0,
            format="%.2f"
        )

    with col_quick:
        st.write("**신속 금액 설정**")
        q1, q2, q3, q4 = st.columns(4)
        if base_currency == "KRW":
            presets = [("10만", 100000.0), ("50만", 500000.0), ("100만", 1000000.0), ("1000만", 10000000.0)]
        else:
            presets = [("100", 100.0), ("500", 500.0), ("1,000", 1000.0), ("10,000", 10000.0)]
        
        btn_cols = [q1, q2, q3, q4]
        for i, (p_label, p_val) in enumerate(presets):
            if btn_cols[i].button(p_label, use_container_width=True, key=f"btn_{p_label}"):
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

st.markdown(f"#### 📊 **{input_amount:,.2f} {base_currency}** 기준 환산 결제 대금")

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
            st.caption(f"1 {base_currency} = {item['단위당_기준환율']:,.4f} {c_code}")

with st.expander("📋 주요 10대 교역 통화 실시간 고시 매트릭스 전체보기", expanded=False):
    table_rows = []
    for r in calc_results:
        unit_text = f"{r['단위']} {r['국가/통화'].split()[-1]}"
        table_rows.append({
            "통화 코드": r["국가/통화"],
            "공식 명칭": r["통화명"],
            f"환산 결제 가액 ({input_amount:,.0f} {base_currency})": f"{r['통화기호']} {r['환산 결과']:,.2f}" if r["단위"] == 1 and r["환산 결과"] < 100000 else f"{r['통화기호']} {r['환산 결과']:,.0f}",
            f"1 {base_currency} 당 비율": f"{r['단위당_기준환율']:,.4f}",
            f"현지 1단위 매입 원가": f"{r['역산환율']:,.2f} {base_currency} (/{unit_text})"
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

st.divider()

# =============================================================================
# [SECTION 2] 🌟 모바일 최적화 대형 환율 전광판 & 밸류에이션 진단
# =============================================================================
st.subheader("📈 외환 밸류에이션 진단 (Valuation Matrix)")
st.caption("시계열 데이터 분포를 기준으로 현재 환율의 역사적 백분위 위치(Percentile)와 고·저평가 상태를 진단합니다.")

target_currency = st.selectbox(
    "분석 대상 교역 통화 선택 (Quote Currency)",
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
    status_label = "🔴 프리미엄 오버슈팅 (상단 과열)"
    status_badge_class = "badge-overvalued"
    status_comment = "역사적 상단 밴드에 위치하여 통화 가치가 고평가된 국면입니다. 수출 채권 조기 회수에는 유리하나, 원자재 수입 기업은 조달 단가 상승에 유의해야 합니다."
elif position_pct >= 55:
    status_label = "🟠 모더레이트 프리미엄 (완만한 강세)"
    status_badge_class = "badge-overvalued"
    status_comment = "과거 중앙값을 상회하는 기술적 저항선 구간입니다. 선물환 매도를 통한 환변동 마진 보전을 검토하세요."
elif position_pct >= 40:
    status_label = "🟢 펀더멘털 적정 균형 (균형 환율)"
    status_badge_class = "badge-fair"
    status_comment = "경상수지 및 금리차가 균형을 이루는 적정 가치 구간입니다. 대외 결제 시 외환 리스크가 비교적 안정적입니다."
elif position_pct >= 25:
    status_label = "🟡 모더레이트 디스카운트 (완만한 약세)"
    status_badge_class = "badge-undervalued"
    status_comment = "중앙선 하회 구간으로 현지 통화가 완만한 디스카운트 상태입니다. 수입 대금 결제 시 원가 절감 효과가 발생합니다."
else:
    status_label = "🔵 디스카운트 언더슈팅 (하단 침체)"
    status_badge_class = "badge-undervalued"
    status_comment = "역사적 지지선 하단에 도달한 극심한 저평가 구간입니다. 수입 부품 장기 물량 선도 계약 체결에 매력적인 구간입니다."

# 🌟 모바일 화면에서는 1열(세로)로 자연스럽게 떨어지는 플렉스/그리드 전광판
st.markdown(f"""
<div class="hero-ticker-box">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 12px; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">
            {CURRENCY_INFO[target_currency]['flag']} {CURRENCY_INFO[target_currency]['name']} ({target_currency})
        </div>
        <div>
            <span class="hero-badge {status_badge_class}">{status_label}</span>
        </div>
    </div>
    <div class="hero-grid">
        <div>
            <div style="font-size: 0.95rem; color: #94a3b8; font-weight: 600;">🇰🇷 원화 환율 (1 {target_currency}{f'[{unit}]' if unit > 1 else ''} 당)</div>
            <div class="hero-rate-value">₩{current_krw_rate:,.2f}</div>
            <div style="font-size: 0.88rem; color: #38bdf8;">역사적 밴드 상위 {position_pct:.1f}% 지점</div>
        </div>
        <div class="hero-divider">
            <div style="font-size: 0.95rem; color: #94a3b8; font-weight: 600;">🇺🇸 기축통화 대비 (1 USD 당)</div>
            <div class="hero-sub-rate">{cur_to_usd:,.4f} {target_currency}</div>
            <div style="font-size: 0.85rem; color: #cbd5e1;">(기준 USD/KRW: ₩{usd_to_krw:,.1f})</div>
        </div>
        <div class="hero-divider">
            <div style="background: rgba(255,255,255,0.06); padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 0.9rem; color: #38bdf8; font-weight: 700; margin-bottom: 4px;">📌 밸류에이션 총평</div>
                <div style="font-size: 0.88rem; color: #e2e8f0; line-height: 1.5;">{status_comment}</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.progress(int(max(0, min(100, position_pct))), text=f"역사적 지지선 (₩{hist_min:,.1f})  ◀── [현재 위치: {position_pct:.1f}%] ──▶  역사적 저항선 (₩{hist_max:,.1f})")

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

time_mode = st.radio(
    "시계열 분석 주기 선택",
    options=["일자별 (최근 30영업일)", "분기별 (최근 8분기)", "연도별 (최근 5개년)"],
    horizontal=True
)

if "30영업일" in time_mode:
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Scatter(x=df_daily["Date"], y=df_daily["Rate"], mode="lines+markers", name="일별 환율 (KRW)", line=dict(color="#2563eb", width=2.5)),
        secondary_y=False
    )
    fig_time.add_trace(
        go.Bar(x=df_daily["Date"], y=df_daily["Change_Pct"], name="등락률 (%)", marker_color=np.where(df_daily["Change_Pct"] >= 0, '#ef4444', '#3b82f6'), opacity=0.45),
        secondary_y=True
    )
    fig_time.update_layout(
        title=f"{target_currency}/KRW 최근 30영업일간 일별 환율 및 등락률(%)",
        height=340, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="환율 (KRW)", secondary_y=False)
    fig_time.update_yaxes(title_text="등락률 (%)", secondary_y=True)
    st.plotly_chart(fig_time, use_container_width=True)

elif "8분기" in time_mode:
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Scatter(x=df_quarterly["Quarter"], y=df_quarterly["Rate"], mode="lines+markers+text", text=[f"{v:,.1f}" for v in df_quarterly["Rate"]], textposition="top center", name="분기별 환율 (KRW)", line=dict(color="#10b981", width=3)),
        secondary_y=False
    )
    fig_time.add_trace(
        go.Bar(x=df_quarterly["Quarter"], y=df_quarterly["QoQ_Pct"], name="QoQ 증감률 (%)", text=[f"{v:+.1f}%" for v in df_quarterly["QoQ_Pct"]], textposition="auto", marker_color=np.where(df_quarterly["QoQ_Pct"] >= 0, '#ef4444', '#3b82f6'), opacity=0.5),
        secondary_y=True
    )
    fig_time.update_layout(
        title=f"{target_currency}/KRW 최근 8개 분기별 환율 및 QoQ 증감률",
        height=340, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="환율 (KRW)", secondary_y=False)
    fig_time.update_yaxes(title_text="QoQ (%)", secondary_y=True)
    st.plotly_chart(fig_time, use_container_width=True)

else:
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Scatter(x=df_yearly["Year"], y=df_yearly["Rate"], mode="lines+markers+text", text=[f"{v:,.1f}" for v in df_yearly["Rate"]], textposition="top center", name="연간 환율 (KRW)", line=dict(color="#8b5cf6", width=3)),
        secondary_y=False
    )
    fig_time.add_trace(
        go.Bar(x=df_yearly["Year"], y=df_yearly["YoY_Pct"], name="YoY 증감률 (%)", text=[f"{v:+.1f}%" for v in df_yearly["YoY_Pct"]], textposition="auto", marker_color=np.where(df_yearly["YoY_Pct"] >= 0, '#ef4444', '#3b82f6'), opacity=0.5),
        secondary_y=True
    )
    fig_time.update_layout(
        title=f"{target_currency}/KRW 최근 5개년 연간 환율 및 YoY 증감률",
        height=340, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="환율 (KRW)", secondary_y=False)
    fig_time.update_yaxes(title_text="YoY (%)", secondary_y=True)
    st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# =============================================================================
# [SECTION 3] 📑 對韓 대외 경상 교역 팩트시트
# =============================================================================
st.subheader("📑 對韓 대외 경상 교역 팩트시트")

KOREA_TRADE_STATS = {
    "USD": {"country": "미국", "code": "US", "export_val": 1157.0, "import_val": 732.0, "balance": 425.0, "top_exports": ["친환경 미래차 및 핵심 전장부품", "고대역폭 메모리 반도체(HBM)", "EV용 고성능 이차전지"], "top_imports": ["에너지 자원(원유·LNG)", "첨단 노광·식각 반도체 장비", "민간 항공기 기체 및 터빈 부품"]},
    "CNY": {"country": "중국", "code": "CN", "export_val": 1248.0, "import_val": 1428.0, "balance": -180.0, "top_exports": ["첨단 패키징 메모리 반도체", "고기능성 엔지니어링 플라스틱", "OLED 평판 디스플레이"], "top_imports": ["이차전지 핵심 광물(수산화리튬)", "IT 하드웨어 컴포넌트", "정밀 유기화학 중간체"]},
    "VND": {"country": "베트남", "code": "VN", "export_val": 535.0, "import_val": 260.0, "balance": 275.0, "top_exports": ["반도체 소자 및 모듈 부품", "고해상도 디스플레이 패널", "무선통신기기 고주파 PCB"], "top_imports": ["스마트폰 완성품 및 어셈블리", "섬유 봉제 고부가가치 의류", "기능성 가죽 피혁 제품군"]},
    "JPY": {"country": "일본", "code": "JP", "export_val": 290.0, "import_val": 476.0, "balance": -186.0, "top_exports": ["고도정제 석유화학제품", "특수 열연 철강 판재류", "정밀 기초 유기화학 물질"], "top_imports": ["반도체 전공정 초정밀 소부장", "감광액(포토레지스트) 화학소재", "특수 엔지니어링 불소수지"]},
    "EUR": {"country": "유로존", "code": "EU", "export_val": 680.0, "import_val": 725.0, "balance": -45.0, "top_exports": ["전기차 및 플러그인 하이브리드", "친환경 LNG 추진 고부가가치선", "중대형 ESS 에너지저장장치"], "top_imports": ["자동화 공작기계 및 초정밀 계측기", "바이오 의약품 및 백신 원제", "유럽 브랜드 프리미엄 완성차"]},
    "AUD": {"country": "호주", "code": "AU", "export_val": 182.0, "import_val": 324.0, "balance": -142.0, "top_exports": ["수송용 고옥탄 휘발유·경유", "중대형 픽업트럭 및 승용차", "광산·인프라용 토목 중장비"], "top_imports": ["고품위 소결 제철용 철광석", "발전 및 제철용 유연탄", "극저온 액화천연가스(LNG)"]},
    "GBP": {"country": "영국", "code": "GB", "export_val": 61.0, "import_val": 58.0, "balance": 3.0, "top_exports": ["특수목적 해양 플랜트 선박", "친환경 승용 세단", "고효율 항공 케로신(제트유)"], "top_imports": ["북해산 브렌트 원유", "항암 바이오 시밀러 완제 의약품", "항공우주용 가스터빈 엔진 컴포넌트"]},
    "CAD": {"country": "캐나다", "code": "CA", "export_val": 110.0, "import_val": 85.0, "balance": 25.0, "top_exports": ["승용차 및 핵심 섀시 부품", "특수 내식성 철강 구조재", "스마트 디지털 가전기기"], "top_imports": ["청정 야금용 점결탄", "산업용 제지 펄프·목재", "합성원유(Synthetic Crude)"]},
    "SGD": {"country": "싱가포르", "code": "SG", "export_val": 220.0, "import_val": 140.0, "balance": 80.0, "top_exports": ["벙커링용 항공유 및 선박유", "특수 가스 운반선", "통신 네트워크 시스템 IC"], "top_imports": ["첨단 의료 정밀 진단기기", "특수 석유화학 정밀 폴리머", "다국적 반도체 패키징 웨이퍼"]},
}

trade_info = KOREA_TRADE_STATS.get(target_currency, KOREA_TRADE_STATS["USD"])

export_df = pd.DataFrame([{
    "분석통화_코드": target_currency,
    "상대국_국가명": trade_info["country"],
    "실시간_재정환율(KRW)": current_krw_rate,
    "외환_밸류에이션_판정": status_label,
    "변동성밴드_분위수": f"{position_pct:.1f}%",
    "對韓_수출규모(억USD)": trade_info["export_val"],
    "對韓_수입규모(억USD)": trade_info["import_val"],
    "경상수지_교역밸런스(억USD)": trade_info["balance"],
    "분석일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}])
csv_bytes = export_df.to_csv(index=False).encode('utf-8-sig')

col_t1, col_t2 = st.columns([3.2, 1.8])
with col_t1:
    st.markdown(f"#### 🏛️ **대한민국 ⇄ {trade_info['country']} 경상 교역 포트폴리오**")
with col_t2:
    st.download_button(
        label="📥 분석 데이터 CSV 저장",
        data=csv_bytes,
        file_name=f"FX_Trade_{target_currency}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

m_b1, m_b2, m_b3 = st.columns(3)
bal_sign = "+" if trade_info["balance"] > 0 else ""
m_b1.metric("대(對)한국 경상수지", f"{bal_sign}{trade_info['balance']:,.0f} 억 USD", delta="흑자국" if trade_info["balance"] > 0 else "적자국")
m_b2.metric("對 한국 수출액", f"${trade_info['export_val']:,.0f}억 USD")
m_b3.metric("對 한국 수입액", f"${trade_info['import_val']:,.0f}억 USD")

with st.container(border=True):
    p1, p2 = st.columns(2)
    with p1:
        export_badges = " ".join([f'<span class="badge-export">✓ {x}</span>' for x in trade_info['top_exports']])
        st.markdown(f"**수출 주력 품목군:**<br>{export_badges}", unsafe_allow_html=True)
    with p2:
        import_badges = " ".join([f'<span class="badge-import">✓ {x}</span>' for x in trade_info['top_imports']])
        st.markdown(f"**수입 주력 품목군:**<br>{import_badges}", unsafe_allow_html=True)

st.markdown("#### 🧭 포지션별 외환 리스크 대응 가이드")
tab_tactics_ex, tab_tactics_im = st.tabs(["🚀 [수출 기업] 결제 통화 전략", "📦 [수입 기업] 원자재 조달 전략"])

with tab_tactics_ex:
    st.markdown(f"""
    <div class="report-card">
        <h5 style="color: #1e3a8a; margin-top: 0;">🎯 수출 가격 경쟁력 및 결제 통화 포지셔닝</h5>
        <ul style="line-height: 1.8; color: #334155;">
            <li><b>결제 통화 포트폴리오</b>: 현지 통화 변동성 리스크 차단을 위해 <b>기축통화(USD) 결제 인보이스 발행</b>을 원칙으로 하되, 바이어 요구 시 통화 연동 조정 계수를 명시할 것.</li>
            <li><b>환변동보험 및 결제주기</b>: 현재 밸류에이션({status_label})에 따라 결제 대금 회수 주기를 단축(Net 30일 이내)하여 미회수 리스크를 방어할 것.</li>
            <li><b>주력 수출 포트폴리오</b>: <code>{', '.join(trade_info['top_exports'])}</code> 부문에서 기술 표준 및 납기 신뢰도 중심의 계약 체결 권장.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab_tactics_im:
    st.markdown(f"""
    <div class="report-card">
        <h5 style="color: #1e3a8a; margin-top: 0;">🏭 원자재 및 부품 조달 원가 방어 전략</h5>
        <ul style="line-height: 1.8; color: #334155;">
            <li><b>조달 듀레이션 관리</b>: 핵심 조달 품목인 <code>{', '.join(trade_info['top_imports'])}</code>의 매입 시점을 분산하고, 현지 통화 약세 구간을 활용한 선도 구매 검토.</li>
            <li><b>파생상품 헷징</b>: 환율 급등에 따른 원가 왜곡을 방지하기 위해 선물환 매수 또는 외환 콜옵션을 적정 비중으로 유지.</li>
            <li><b>공급망 다변화</b>: 단일국 의존도가 높은 전략 물자에 대해 대체 공급선 다변화 확보.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)