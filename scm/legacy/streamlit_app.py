from datetime import datetime, timedelta
import io
import os
import urllib.request
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# PPTX 생성 라이브러리
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# PDF 생성 라이브러리 (ReportLab)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image as RLImage, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==============================================================================
# [1. Page Configuration]
# ==============================================================================
st.set_page_config(
    page_title="Executive SCM Control Tower & Digital Twin",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# [2. Design System & Responsive CSS]
# ==============================================================================
st.markdown(
    """
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        :root {
            --bg-main: #F5F5F7;
            --bg-card: #FFFFFF;
            --border-color: #E5E5EA;
            --text-main: #1D1D1F;
            --text-sub: #86868B;
            --color-green: #34C759;
            --color-yellow: #FF9500;
            --color-red: #FF3B30;
            --color-blue: #0066CC;
            --card-radius: 12px;
            --shadow-subtle: 0 2px 8px rgba(0, 0, 0, 0.03);
        }

        html, body, .stApp, [data-testid="stAppViewContainer"], section.main {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
            background-color: var(--bg-main) !important;
            color: var(--text-main) !important;
        }

        header[data-testid="stHeader"] {
            background-color: transparent !important;
            background: transparent !important;
            z-index: 100 !important;
        }

        .block-container {
            padding-top: 3.6rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: clamp(1rem, 2vw, 2.5rem) !important;
            padding-right: clamp(1rem, 2vw, 2.5rem) !important;
            max-width: 100% !important;
        }

        div[data-testid="stElementContainer"]:has(style) {
            display: none !important;
        }

        section[data-testid="stSidebar"] {
            min-width: 250px !important;
            max-width: 320px !important;
            background-color: rgba(251, 251, 253, 0.98) !important;
            border-right: 1px solid rgba(210, 210, 215, 0.6) !important;
        }

        div[data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
        }

        .control-tower-header {
            background: var(--bg-card);
            padding: clamp(0.8rem, 1.2vw, 1.2rem) clamp(1rem, 1.5vw, 1.6rem);
            border-radius: var(--card-radius);
            box-shadow: var(--shadow-subtle);
            border: 1px solid var(--border-color);
            margin-bottom: 0.8rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.8rem;
        }

        .traffic-lights {
            display: flex;
            gap: 6px;
            margin-bottom: 5px;
        }
        .dot { width: 9px; height: 9px; border-radius: 50%; }
        .dot-red { background-color: var(--color-red); }
        .dot-yellow { background-color: var(--color-yellow); }
        .dot-green { background-color: var(--color-green); }

        .custom-h1 { font-size: clamp(1.25rem, 1.6vw, 1.55rem); font-weight: 800; color: var(--text-main); margin: 0; line-height: 1.25; }
        .custom-h2 { font-size: clamp(1.05rem, 1.3vw, 1.25rem); font-weight: 700; color: var(--text-main); margin-top: 1rem; margin-bottom: 0.6rem; line-height: 1.3; }
        .custom-h3 { font-size: clamp(0.92rem, 1.1vw, 1.05rem); font-weight: 700; color: #3A3A3C; margin-top: 0.4rem; margin-bottom: 0.4rem; }

        div[data-testid="stMetric"] {
            box-sizing: border-box !important;
            background: var(--bg-card) !important;
            padding: clamp(0.65rem, 0.9vw, 0.95rem) !important;
            border-radius: var(--card-radius) !important;
            box-shadow: var(--shadow-subtle) !important;
            border: 1px solid var(--border-color) !important;
            text-align: center !important;
            min-height: 94px !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            overflow: hidden !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: clamp(0.72rem, 0.78vw, 0.82rem) !important;
            font-weight: 600 !important;
            color: var(--text-sub) !important;
            line-height: 1.25 !important;
            word-break: keep-all !important;
            overflow-wrap: anywhere !important;
            margin-bottom: 3px !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: clamp(1.15rem, 1.45vw, 1.52rem) !important;
            font-weight: 800 !important;
            color: var(--text-main) !important;
            letter-spacing: -0.5px !important;
            line-height: 1.2 !important;
            word-break: normal !important;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 0.73rem !important;
            line-height: 1.1 !important;
        }

        .custom-card {
            box-sizing: border-box;
            width: 100%;
            height: 100%;
            min-height: 195px;
            padding: clamp(0.9rem, 1.1vw, 1.2rem);
            border-radius: var(--card-radius);
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            box-shadow: var(--shadow-subtle);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
            word-break: keep-all;
            overflow-wrap: anywhere;
        }

        .card-header-title {
            font-weight: 800;
            font-size: clamp(0.95rem, 1.05vw, 1.1rem);
            color: var(--text-main);
            margin-bottom: 0.4rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: clamp(0.82rem, 0.9vw, 0.88rem);
            margin: 3px 0;
            color: #3A3A3C;
        }
        .card-data-row b {
            color: var(--text-main);
            font-weight: 700;
        }

        .intelligent-alert-box {
            background: var(--bg-card);
            padding: 0.8rem 1.2rem;
            border-radius: var(--card-radius);
            border-left: 5px solid var(--color-red);
            border-top: 1px solid var(--border-color);
            border-right: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            box-shadow: var(--shadow-subtle);
            margin-bottom: 1rem;
            word-break: keep-all;
        }
        .intelligent-alert-box ul {
            margin: 0 !important;
            padding-left: 1.2rem !important;
        }
        .intelligent-alert-box li {
            line-height: 1.45 !important;
            font-size: clamp(0.82rem, 0.9vw, 0.88rem) !important;
            font-weight: 600 !important;
            margin-bottom: 3px;
        }

        .exec-summary-box {
            background: var(--bg-card);
            padding: 1.2rem 1.5rem;
            border-radius: var(--card-radius);
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-subtle);
            margin-top: 1rem;
            word-break: keep-all;
        }

        .badge-green { background-color: var(--color-green); color: white; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.72rem; }
        .badge-yellow { background-color: var(--color-yellow); color: white; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.72rem; }
        .badge-red { background-color: var(--color-red); color: white; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.72rem; }

        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# [3. API / Data Interface Layer] (향후 ERP/WMS/TMS 연동 준비)
# ==============================================================================
def get_orders(): return None
def get_inventory(): return None
def get_shipments(): return None
def get_suppliers(): return None
def get_purchase_orders(): return None

def format_currency(val):
    if pd.isna(val) or val == 0: return "₩0"
    if abs(val) >= 1_000_000_000_000: return f"₩{val / 1_000_000_000_000:.1f}T"
    elif abs(val) >= 100_000_000: return f"₩{val / 100_000_000:.1f}억"
    elif abs(val) >= 1_000_000: return f"₩{val / 1_000_000:.1f}M"
    else: return f"₩{val:,.0f}"

# ==============================================================================
# [4. Synthetic Data Layer] (2026-08-31 완결 포함 데이터셋 생성)
# ==============================================================================
@st.cache_data
def generate_control_tower_data():
    np.random.seed(42)
    n_rows = 7500

    suppliers = ["Supplier_A", "Supplier_B", "Supplier_C", "Supplier_D", "Overseas_Supplier"]
    warehouses = ["ICN_DC", "BUSAN_DC", "DAEJEON_DC", "GWANGJU_DC"]
    channels = ["B2C", "DC", "B2B"]
    products = [f"SKU_Item_{i:02d}" for i in range(1, 21)]

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2026, 8, 31)
    total_days = (end_date - start_date).days

    # total_days + 1을 통해 2026-08-31 데이터가 반드시 생성되도록 보정
    random_days = np.random.randint(0, total_days + 1, size=n_rows)
    date_range = [start_date + timedelta(days=int(d)) for d in random_days]

    data_list = []
    for i in range(n_rows):
        dt = date_range[i]
        year, month = dt.year, dt.month
        ch = np.random.choice(channels, p=[0.55, 0.30, 0.15])
        wh = np.random.choice(warehouses, p=[0.40, 0.30, 0.20, 0.10])
        sup = np.random.choice(suppliers, p=[0.25, 0.25, 0.20, 0.15, 0.15])
        sku = np.random.choice(products)

        is_year_end = month in [11, 12]
        is_black_friday = month == 11
        is_chuseok = month == 9
        is_b2b_proj = np.random.rand() < 0.15
        is_disruption = np.random.rand() < 0.08

        multiplier = 1.0
        spike_label = "Normal"
        if is_black_friday:
            multiplier = 3.8
            spike_label = "Black Friday (+280%)"
        elif is_year_end:
            multiplier = 3.2
            spike_label = "Year-End Peak"
        elif is_chuseok:
            multiplier = 2.0
            spike_label = "Chuseok Special (+100%)"
        elif month in [1, 2]:
            multiplier = 1.8
            spike_label = "Lunar New Year"
        if ch == "B2B" and is_b2b_proj:
            multiplier *= 2.2
            spike_label = "B2B Project (+120%)"

        if ch == "B2C":
            base_q = np.random.randint(1, 6)
            order_q = int(base_q * multiplier)
            unfulfilled = np.random.choice([0, 1], p=[0.92, 0.08]) if not is_disruption else np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            sales_q = max(0, order_q - unfulfilled)
        elif ch == "DC":
            base_q = np.random.randint(30, 120)
            order_q = int(base_q * multiplier)
            unfulfilled = np.random.randint(0, 10) if is_disruption else np.random.randint(0, 4)
            sales_q = max(0, order_q - unfulfilled)
        else:
            base_q = np.random.randint(200, 600)
            order_q = int(base_q * (multiplier * 1.3 if is_b2b_proj else 1.0))
            unfulfilled = np.random.randint(5, 30) if is_disruption else np.random.randint(0, 10)
            sales_q = max(0, order_q - unfulfilled)

        forecast_q = int(sales_q * np.random.uniform(0.88, 1.14))
        unit_price = np.random.randint(20000, 120000)
        revenue = sales_q * unit_price

        daily_cap = 12000 if wh == "ICN_DC" else (18000 if wh == "BUSAN_DC" else (15000 if wh == "DAEJEON_DC" else 8000))
        util_rate = min(round((sales_q / (daily_cap / 30)) * 100, 2), 108.0)

        base_lt = np.random.randint(3, 7) if sup != "Overseas_Supplier" else np.random.randint(14, 28)
        lead_time = base_lt + (np.random.randint(4, 12) if is_disruption else 0)

        surge_factor = 1.25 if util_rate > 90 else 1.0
        transport_c = sales_q * np.random.randint(1800, 3500) * surge_factor
        handling_c = sales_q * np.random.randint(500, 1100)
        labor_c = sales_q * np.random.randint(800, 2000) * surge_factor
        storage_c = np.random.randint(500000, 2000000) / 30
        packaging_c = sales_q * np.random.randint(150, 400)
        total_logistics_c = transport_c + handling_c + labor_c + storage_c + packaging_c
        cost_per_unit = round(total_logistics_c / max(1, sales_q), 2)

        stock_q = np.random.randint(20, 700)
        inbound_expected = np.random.randint(0, 250)

        data_list.append({
            "order_date": dt,
            "year": dt.year,
            "month": dt.month,
            "year_month": dt.strftime("%Y-%m"),
            "date_str": dt.strftime("%Y-%m-%d"),
            "supplier": sup,
            "purchase_order": f"PO{dt.year}{i:05d}",
            "forecast_quantity": forecast_q,
            "order_quantity": order_q,
            "sales_quantity": sales_q,
            "warehouse": wh,
            "daily_capacity": daily_cap,
            "utilization_rate": util_rate,
            "transport_cost": transport_c,
            "handling_cost": handling_c,
            "labor_cost": labor_c,
            "storage_cost": storage_c,
            "packaging_cost": packaging_c,
            "total_logistics_cost": total_logistics_c,
            "cost_per_unit": cost_per_unit,
            "stock_quantity": stock_q,
            "expected_inbound": inbound_expected,
            "lead_time_days": lead_time,
            "channel": ch,
            "product_name": sku,
            "revenue": revenue,
            "spike_event": spike_label
        })

    df = pd.DataFrame(data_list)
    df["is_otd"] = np.where(df["supplier"].str.contains("Overseas"), df["lead_time_days"] <= 20, df["lead_time_days"] <= 5)
    df["is_otif"] = df["is_otd"] & (df["sales_quantity"] >= df["order_quantity"])

    df["daily_demand"] = df["sales_quantity"] / 30.0
    df["lead_time_demand"] = df["lead_time_days"] * df["daily_demand"]
    df["projected_stock"] = (df["stock_quantity"] + df["expected_inbound"] - df["lead_time_demand"]).round(1)

    def classify_risk(p_stock):
        if p_stock <= 0: return "CRITICAL"
        elif p_stock <= 35: return "WARNING"
        elif p_stock <= 80: return "WATCH"
        else: return "NORMAL"

    df["risk_level"] = df["projected_stock"].apply(classify_risk)
    df["is_stockout_risk"] = df["risk_level"].isin(["CRITICAL", "WARNING"])
    df["daily_avg_sales"] = np.random.randint(15, 120, size=len(df))
    df["days_on_hand"] = (df["stock_quantity"] / df["daily_avg_sales"].replace(0, 1)).round(1)

    return df

raw_df = generate_control_tower_data()

# ==============================================================================
# [5. Global Filter & Sidebar Setup]
# ==============================================================================
st.sidebar.markdown("<h3 style='margin-bottom:0px;'>🎛️ Control Tower 관제</h3>", unsafe_allow_html=True)
selected_menu = st.sidebar.selectbox("화면 선택", [
    "1. Executive Dashboard",
    "2. Daily Operation Dashboard",
    "3. Warehouse Dashboard",
    "4. Logistics Cost Dashboard",
    "5. Inventory Dashboard",
    "6. Demand Forecast Dashboard",
    "7. ABC Analysis",
    "8. ABC-XYZ Matrix",
    "9. Supplier Dashboard",
    "10. 🎯 Digital Twin & What-if Planning (2027)"
])

st.sidebar.markdown("---")
with st.sidebar.expander("🎯 경영진 KPI 목표 설정", expanded=False):
    target_rev_growth = st.number_input("매출 성장률 목표 (%)", value=15.0, step=1.0) / 100.0
    target_vol_growth = st.number_input("물동량 증가율 목표 (%)", value=10.0, step=1.0) / 100.0
    target_cost_reduction = st.number_input("물류비 절감률 목표 (%)", value=8.0, step=1.0) / 100.0
    target_otd = st.number_input("OTD 목표 (%)", value=98.0, step=0.5)

with st.sidebar.expander("⚡ What-if 시뮬레이션 설정", expanded=False):
    sim_rev_growth = st.slider("시뮬레이션 매출 성장률 (%)", 0.0, 30.0, 15.0, 0.5) / 100.0
    sim_cost_reduction = st.slider("시뮬레이션 물류비 절감률 (%)", 0.0, 20.0, 7.5, 0.5) / 100.0
    sim_otd_boost = st.slider("시뮬레이션 OTD 개선치 (%p)", -5.0, 5.0, 1.2, 0.1) / 100.0

with st.sidebar.expander("🔍 전역 데이터 필터", expanded=True):
    max_data_date = raw_df["order_date"].max()
    min_data_date = raw_df["order_date"].min()

    date_filter_option = st.selectbox(
        "기간 선택",
        ["전체 기간 (5개년)", "데이터 기준 최신일", "최근 7일", "최근 30일", "최근 90일", "사용자 지정"]
    )

    if date_filter_option == "데이터 기준 최신일":
        date_filtered_df = raw_df[raw_df["order_date"] == max_data_date]
    elif date_filter_option == "최근 7일":
        date_filtered_df = raw_df[raw_df["order_date"] >= (max_data_date - timedelta(days=7))]
    elif date_filter_option == "최근 30일":
        date_filtered_df = raw_df[raw_df["order_date"] >= (max_data_date - timedelta(days=30))]
    elif date_filter_option == "최근 90일":
        date_filtered_df = raw_df[raw_df["order_date"] >= (max_data_date - timedelta(days=90))]
    elif date_filter_option == "사용자 지정":
        date_val = st.date_input("기간 지정", [min_data_date, max_data_date])
        if isinstance(date_val, (list, tuple)):
            if len(date_val) == 2: s_date, e_date = date_val
            elif len(date_val) == 1: s_date = e_date = date_val[0]
            else: s_date, e_date = min_data_date, max_data_date
        else:
            s_date = e_date = date_val
        date_filtered_df = raw_df[(raw_df["order_date"] >= pd.to_datetime(s_date)) & (raw_df["order_date"] <= pd.to_datetime(e_date))]
    else:
        date_filtered_df = raw_df.copy()

    selected_channels = st.multiselect("조회 채널", options=["B2C", "DC", "B2B"], default=["B2C", "DC", "B2B"])
    selected_wh = st.multiselect("물류센터(DC)", options=raw_df["warehouse"].unique(), default=raw_df["warehouse"].unique())

filtered_df = date_filtered_df[
    date_filtered_df["channel"].isin(selected_channels) &
    date_filtered_df["warehouse"].isin(selected_wh)
]

if filtered_df.empty:
    st.warning("⚠️ 선택하신 필터 조건에 부합하는 SCM 운영 데이터가 존재하지 않습니다. 사이드바 필터 조건을 확인해주세요.")
    st.stop()

# ==============================================================================
# [6. Global Pre-calculations & Strict Dependency Alignment]
# ==============================================================================
# 6-1. 2026년 전사 베이스라인
df_2026_all = raw_df[raw_df["year"] == 2026]
base_rev_2026 = df_2026_all["revenue"].sum() if not df_2026_all.empty else 0.0
base_vol_2026 = df_2026_all["sales_quantity"].sum() if not df_2026_all.empty else 0.0
base_cost_2026 = df_2026_all["total_logistics_cost"].sum() if not df_2026_all.empty else 0.0
base_otd_2026 = (df_2026_all["is_otd"].sum() / max(1, len(df_2026_all))) * 100.0 if not df_2026_all.empty else 0.0

# 6-2. 2027년 목표치 (Target) & 예측치 (Forecast)
target_rev_2027 = base_rev_2026 * (1.0 + target_rev_growth)
target_vol_2027 = base_vol_2026 * (1.0 + target_vol_growth)
target_cost_2027 = base_cost_2026 * (1.0 + target_vol_growth) * (1.0 - target_cost_reduction)

forecast_rev_2027 = base_rev_2026 * (1.0 + sim_rev_growth)
forecast_vol_2027 = base_vol_2026 * (1.0 + target_vol_growth)
forecast_cost_2027 = base_cost_2026 * (1.0 + target_vol_growth) * (1.0 - sim_cost_reduction)
forecast_otd_2027 = min(100.0, max(0.0, base_otd_2026 + (sim_otd_boost * 100.0)))

# 6-3. 필터링된 현재 데이터 기반 핵심 KPI 계산
tot_records = len(filtered_df)
tot_order_qty = filtered_df["order_quantity"].sum()
tot_sales_qty = filtered_df["sales_quantity"].sum()
tot_log_cost = filtered_df["total_logistics_cost"].sum()

real_fill_rate = min(100.0, round((tot_sales_qty / max(1.0, tot_order_qty) * 100.0), 1)) if tot_order_qty > 0 else 100.0
real_otd = round((filtered_df["is_otd"].sum() / max(1, tot_records) * 100.0), 1)
real_otif = round((filtered_df["is_otif"].sum() / max(1, tot_records) * 100.0), 1)

avg_stock = filtered_df["stock_quantity"].mean()
real_turnover = round((tot_sales_qty / max(1.0, avg_stock) * 0.25), 1)

avg_warehouse_util = filtered_df["utilization_rate"].mean() if tot_records > 0 else 0.0
critical_risk_count = int(filtered_df["is_stockout_risk"].sum())

score_service = real_fill_rate * 0.25
score_otd = real_otd * 0.20
score_capacity = max(0.0, min(100.0, (100.0 - max(0.0, avg_warehouse_util - 80.0) * 4.0))) * 0.20
score_inventory = max(0.0, (100.0 - (critical_risk_count / max(1, tot_records) * 300.0))) * 0.20
score_supplier = (filtered_df.groupby("supplier")["is_otd"].mean().mean() * 100.0 if tot_records > 0 else 85.0) * 0.15
scm_health_score = int(np.clip(score_service + score_otd + score_capacity + score_inventory + score_supplier, 0, 100))

wh_summary = filtered_df.groupby("warehouse").agg({
    "sales_quantity": "sum",
    "utilization_rate": "mean",
    "total_logistics_cost": "sum",
    "is_otd": lambda x: f"{(x.sum() / max(1, len(x))) * 100.0:.1f}%"
}).reset_index()

busan_df = filtered_df[filtered_df["warehouse"] == "BUSAN_DC"]
busan_util = busan_df["utilization_rate"].mean() if not busan_df.empty else 0.0

if busan_util >= 90.0:
    busan_comment = f"BUSAN_DC 가동률이 <b>{busan_util:.1f}%</b>로 임계치 초과, 성수기 대비 권역 분산 필요"
else:
    busan_comment = f"전국 물류센터 가동률 안정 범위(BUSAN_DC: <b>{busan_util:.1f}%</b>)"

if sim_cost_reduction >= target_cost_reduction:
    cost_comment = f"물류비 절감 시나리오(<b>{sim_cost_reduction*100:.1f}%</b>) 목표치 달성"
else:
    cost_comment = f"물류비 절감 시나리오(<b>{sim_cost_reduction*100:.1f}%</b>) 목표 대비 소폭 미달"

cost_breakdown = pd.DataFrame({
    "비용항목": ["운송비", "인건비", "보관비", "하역비", "포장비"],
    "금액": [
        filtered_df["transport_cost"].sum(),
        filtered_df["labor_cost"].sum(),
        filtered_df["storage_cost"].sum(),
        filtered_df["handling_cost"].sum(),
        filtered_df["packaging_cost"].sum(),
    ]
})

inv_df = filtered_df.groupby("product_name").agg({
    "stock_quantity": "sum",
    "expected_inbound": "sum",
    "projected_stock": "mean",
    "days_on_hand": "mean",
    "risk_level": lambda x: x.mode()[0] if not x.empty else "NORMAL"
}).reset_index()

fc_agg = filtered_df.groupby("year_month")[["forecast_quantity", "sales_quantity"]].sum().reset_index()
fc_agg["절대오차"] = abs(fc_agg["forecast_quantity"] - fc_agg["sales_quantity"])
fc_agg["편향(Bias)"] = fc_agg["forecast_quantity"] - fc_agg["sales_quantity"]
wmape_val = (fc_agg["절대오차"].sum() / max(1.0, fc_agg["sales_quantity"].sum())) * 100.0

sup_perf = filtered_df.groupby("supplier").agg({
    "lead_time_days": ["mean", "std"],
    "is_otd": lambda x: (x.sum() / max(1, len(x))) * 100.0,
    "purchase_order": "count"
})
sup_perf.columns = ["평균리드타임", "리드타임표준편차", "OTD(%)", "발주건수"]
sup_perf = sup_perf.reset_index()
sup_perf["리드타임표준편차"] = sup_perf["리드타임표준편차"].fillna(0.0)
sup_perf["변동계수(CV)"] = (sup_perf["리드타임표준편차"] / sup_perf["평균리드타임"].replace(0, 1.0)).round(2)

def evaluate_sup_risk(row):
    if row["OTD(%)"] < 88.0 or row["변동계수(CV)"] > 0.40: return "High Risk"
    elif row["OTD(%)"] < 94.0 or row["변동계수(CV)"] > 0.25: return "Medium Risk"
    else: return "Low Risk"

sup_perf["리스크등급"] = sup_perf.apply(evaluate_sup_risk, axis=1)

# 고변동성 공급사 추출
high_variance_suppliers = []
if not sup_perf.empty and "변동계수(CV)" in sup_perf.columns and "supplier" in sup_perf.columns:
    high_variance_suppliers = (
        sup_perf.loc[sup_perf["변동계수(CV)"] > 0.35, "supplier"]
        .astype(str)
        .tolist()
    )

# Today's Operation 기준: 필터 조건 내 실제 최신일로 정합성 일원화
target_latest_date = filtered_df["order_date"].max() if not filtered_df.empty else max_data_date
latest_day_df = filtered_df[filtered_df["order_date"] == target_latest_date]
t_outbound = latest_day_df["sales_quantity"].sum() if not latest_day_df.empty else 0
t_inbound = latest_day_df["expected_inbound"].sum() if not latest_day_df.empty else 0
t_orders = latest_day_df["order_quantity"].sum() if not latest_day_df.empty else 0
t_cost = latest_day_df["total_logistics_cost"].sum() if not latest_day_df.empty else 0
t_stock = latest_day_df["stock_quantity"].sum() if not latest_day_df.empty else 0
t_risk_skus = int(latest_day_df["is_stockout_risk"].sum()) if not latest_day_df.empty else 0

# 단일 소스 캡슐화 데이터 패키지 (Report Data)
report_data = {
    "max_data_date": target_latest_date,
    "system_max_date": max_data_date,
    "scm_health_score": scm_health_score,
    "real_fill_rate": real_fill_rate,
    "real_otd": real_otd,
    "real_otif": real_otif,
    "real_turnover": real_turnover,
    "critical_risk_count": critical_risk_count,
    "tot_log_cost": tot_log_cost,
    "t_inbound": t_inbound,
    "t_outbound": t_outbound,
    "t_orders": t_orders,
    "t_cost": t_cost,
    "t_stock": t_stock,
    "t_risk_skus": t_risk_skus,
    "wh_summary": wh_summary,
    "cost_breakdown": cost_breakdown,
    "inv_df": inv_df,
    "fc_agg": fc_agg,
    "wmape_val": wmape_val,
    "sup_perf": sup_perf,
    "high_variance_suppliers": high_variance_suppliers,
    "base_rev_2026": base_rev_2026,
    "base_vol_2026": base_vol_2026,
    "base_cost_2026": base_cost_2026,
    "base_otd_2026": base_otd_2026,
    "target_rev_growth": target_rev_growth,
    "target_vol_growth": target_vol_growth,
    "target_cost_reduction": target_cost_reduction,
    "target_otd": target_otd,
    "target_rev_2027": target_rev_2027,
    "target_vol_2027": target_vol_2027,
    "target_cost_2027": target_cost_2027,
    "sim_rev_growth": sim_rev_growth,
    "sim_cost_reduction": sim_cost_reduction,
    "sim_otd_boost": sim_otd_boost,
    "forecast_rev_2027": forecast_rev_2027,
    "forecast_vol_2027": forecast_vol_2027,
    "forecast_cost_2027": forecast_cost_2027,
    "forecast_otd_2027": forecast_otd_2027,
    "busan_comment": busan_comment,
    "cost_comment": cost_comment,
    "filtered_df": filtered_df,
    "selected_channels": selected_channels,
    "selected_wh": selected_wh,
    "date_filter_option": date_filter_option
}

# ==============================================================================
# [7. Design Constants for PPTX & Visual Engine] (전역 디자인 상수 통합)
# ==============================================================================
COLOR_PRIMARY_NAVY = RGBColor(15, 23, 42)    # #0F172A
COLOR_ACCENT_BLUE   = RGBColor(0, 102, 204)   # #0066CC
COLOR_TEXT_MAIN     = RGBColor(30, 30, 30)    # #1E1E1E
COLOR_TEXT_SUB      = RGBColor(100, 116, 139) # #64748B
COLOR_TEXT_LIGHT    = RGBColor(148, 163, 184) # #94A3B8
COLOR_BG_MAIN       = RGBColor(255, 255, 255) # #FFFFFF
COLOR_BG_SUB        = RGBColor(241, 245, 249) # #F1F5F9 (LIGHT_GRAY)
COLOR_BORDER        = RGBColor(226, 232, 240) # #E2E8F0
COLOR_SUCCESS       = RGBColor(52, 199, 89)   # #34C759
COLOR_WARNING       = RGBColor(255, 149, 0)   # #FF9500
COLOR_DANGER        = RGBColor(255, 59, 48)   # #FF3B30
COLOR_WHITE         = RGBColor(255, 255, 255)
COLOR_BLACK         = RGBColor(0, 0, 0)

# 호환성을 위한 완전한 별칭(Aliases) 체계
TEXT_MAIN  = COLOR_TEXT_MAIN
TEXT_SUB   = COLOR_TEXT_SUB
TEXT_LIGHT = COLOR_TEXT_LIGHT
BG_MAIN    = COLOR_BG_MAIN
BG_SUB     = COLOR_BG_SUB
NAVY       = COLOR_PRIMARY_NAVY
PRIMARY    = COLOR_PRIMARY_NAVY
BLUE       = COLOR_ACCENT_BLUE
ACCENT     = COLOR_ACCENT_BLUE
WHITE      = COLOR_WHITE
BLACK      = COLOR_BLACK
GRAY       = COLOR_TEXT_SUB
LIGHT_GRAY = COLOR_BG_SUB
BORDER     = COLOR_BORDER
GREEN      = COLOR_SUCCESS
SUCCESS    = COLOR_SUCCESS
AMBER      = COLOR_WARNING
WARNING    = COLOR_WARNING
RED        = COLOR_DANGER
DANGER     = COLOR_DANGER

# ==============================================================================
# [8. Professional PPTX & PDF Report Engines]
# ==============================================================================

def get_korean_font_name():
    """PDF 한글 폰트 자동 등록 및 fallback 처리"""
    candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/nanum/NanumGothic.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "./NanumGothic.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("KFont", path))
                return "KFont"
            except Exception:
                pass
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        local_path = "./NanumGothic.ttf"
        if not os.path.exists(local_path):
            urllib.request.urlretrieve(url, local_path)
        if os.path.exists(local_path):
            pdfmetrics.registerFont(TTFont("KFont", local_path))
            return "KFont"
    except Exception:
        pass
    return "Helvetica"

def create_chart_image(chart_type, r_data):
    """보고서 삽입용 클린 Matplotlib 차트 생성 (데이터 누락 예외 방어)"""
    fig, ax = plt.subplots(figsize=(5.5, 3.0), dpi=150)
    plt.tight_layout()
    wh_sum = r_data.get("wh_summary", pd.DataFrame())
    c_break = r_data.get("cost_breakdown", pd.DataFrame())
    f_df = r_data.get("filtered_df", pd.DataFrame())

    if chart_type == "warehouse":
        if not wh_sum.empty:
            whs = wh_sum["warehouse"].tolist()
            utils = wh_sum["utilization_rate"].tolist()
            colors_list = ['#FF3B30' if u >= 90 else '#0F172A' for u in utils]
            ax.bar(whs, utils, color=colors_list, width=0.45)
            ax.axhline(90, color='#FF3B30', linestyle='--', linewidth=1.2)
            ax.set_ylim(0, 115)
            for i, v in enumerate(utils):
                ax.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=9, color='#1D1D1F')
        else:
            ax.text(0.5, 0.5, "No Warehouse Data Available", ha='center', va='center')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.yaxis.set_visible(False)
    elif chart_type == "cost":
        if not c_break.empty:
            costs = c_break["금액"].tolist()
            labels = c_break["비용항목"].tolist()
            colors_list = ['#0F172A', '#34C759', '#FF9500', '#64748B', '#0066CC']
            wedges, _, autotexts = ax.pie(
                costs, labels=labels, autopct='%1.1f%%', colors=colors_list, 
                startangle=140, pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2)
            )
            for at in autotexts:
                at.set_fontsize(8)
                at.set_weight('bold')
                at.set_color('white')
        else:
            ax.text(0.5, 0.5, "No Cost Breakdown Data", ha='center', va='center')
    elif chart_type == "trend":
        if not f_df.empty:
            trend_data = f_df.groupby("year_month")["sales_quantity"].sum().tail(12).reset_index()
            ax.plot(trend_data["year_month"], trend_data["sales_quantity"], marker='o', color='#0F172A', linewidth=2.5, markersize=5)
            ax.set_xticklabels(trend_data["year_month"], rotation=45, fontsize=8)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
        else:
            ax.text(0.5, 0.5, "No Trend Data", ha='center', va='center')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png", bbox_inches="tight", transparent=False)
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

def generate_pptx_report(r_data):
    """
    McKinsey/Canva 스타일의 11-Slide 의사결정용 Executive PPTX 생성 엔진
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    dt_str = r_data.get('max_data_date', datetime.now()).strftime('%Y-%m-%d')
    chs = ", ".join(r_data.get('selected_channels', ['All']))
    whs = ", ".join(r_data.get('selected_wh', ['All']))

    # Component: Page Header & Footer
    def add_page_header(slide, title, lead_message, slide_num):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
        shape.fill.solid()
        shape.fill.fore_color.rgb = NAVY
        shape.line.fill.background()
        
        hdr = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(12.0), Inches(1.0))
        tf = hdr.text_frame
        p1 = tf.paragraphs[0]
        p1.text = title.upper()
        p1.font.name = "Malgun Gothic"
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = GRAY
        
        p2 = tf.add_paragraph()
        p2.text = lead_message
        p2.font.name = "Malgun Gothic"
        p2.font.size = Pt(20)
        p2.font.bold = True
        p2.font.color.rgb = NAVY

        ftr = slide.shapes.add_textbox(Inches(0.6), Inches(6.9), Inches(12.0), Inches(0.4))
        ftf = ftr.text_frame
        fp = ftf.paragraphs[0]
        fp.text = f"SCM Executive Report | Date: {dt_str} | Channels: {chs} | DCs: {whs} | Page {slide_num}"
        fp.font.name = "Malgun Gothic"
        fp.font.size = Pt(9)
        fp.font.color.rgb = GRAY

    # Component: KPI Block
    def add_kpi_block(slide, left, top, width, height, value, label, sub_text, val_color=NAVY):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = LIGHT_GRAY
        tf = box.text_frame
        
        p1 = tf.paragraphs[0]
        p1.text = str(value)
        p1.font.name = "Malgun Gothic"
        p1.font.size = Pt(32)
        p1.font.bold = True
        p1.font.color.rgb = val_color
        p1.alignment = PP_ALIGN.LEFT
        
        p2 = tf.add_paragraph()
        p2.text = str(label)
        p2.font.name = "Malgun Gothic"
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = NAVY
        
        p3 = tf.add_paragraph()
        p3.text = str(sub_text)
        p3.font.name = "Malgun Gothic"
        p3.font.size = Pt(9)
        p3.font.color.rgb = GRAY

    # -------------------------------------------------------------
    # Slide 1: Cover
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    s1.background.fill.solid()
    s1.background.fill.fore_color.rgb = NAVY

    shape = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(2.0), Inches(0.1), Inches(3.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLUE
    shape.line.fill.background()

    c_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.0), Inches(3.0))
    ctf = c_box.text_frame
    p1 = ctf.paragraphs[0]
    p1.text = "SCM EXECUTIVE\nCONTROL TOWER"
    p1.font.name = "Malgun Gothic"
    p1.font.size = Pt(48)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p2 = ctf.add_paragraph()
    p2.text = "\nEnterprise Management Report"
    p2.font.name = "Malgun Gothic"
    p2.font.size = Pt(18)
    p2.font.color.rgb = GRAY

    f_box = s1.shapes.add_textbox(Inches(1.3), Inches(5.8), Inches(10.0), Inches(1.0))
    ftf = f_box.text_frame
    fp1 = ftf.paragraphs[0]
    fp1.text = f"Date: {dt_str}\nChannels: {chs} | Warehouses: {whs}"
    fp1.font.name = "Malgun Gothic"
    fp1.font.size = Pt(12)
    fp1.font.color.rgb = WHITE

    # -------------------------------------------------------------
    # Slide 2: Contents
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_page_header(s2, "Table of Contents", "Executive Agenda", "2 / 11")
    
    agenda = [
        ("01", "Executive Summary", "전사 SCM 상태 진단 및 핵심 메시지"),
        ("02", "Today's Operation", "실시간 물동량 및 현장 재고/출고 현황"),
        ("03", "Warehouse Performance", "거점 DC별 가동률 병목 및 처리량"),
        ("04", "Logistics Cost Analysis", "물류비 구조 분석 및 절감 기회"),
        ("05", "Inventory Risk", "안전재고 미달 품목 및 결품 리스크"),
        ("06", "Demand Forecast", "수요예측 정확도(WMAPE) 및 트렌드"),
        ("07", "Supplier Performance", "공급사 OTD 및 리드타임 변동성(CV) 평가"),
        ("08", "Digital Twin 2027", "2026 실적 vs 2027 목표 vs 시뮬레이션 비교"),
        ("09", "Management Action", "우선 순위별 경영진 조치 권고안")
    ]
    for i, (num, title, desc) in enumerate(agenda):
        col = i // 5
        row = i % 5
        x = Inches(0.8 + col * 6.0)
        y = Inches(1.8 + row * 0.9)
        
        num_box = s2.shapes.add_textbox(x, y, Inches(0.6), Inches(0.6))
        num_tf = num_box.text_frame
        np1 = num_tf.paragraphs[0]
        np1.text = num
        np1.font.name = "Malgun Gothic"
        np1.font.size = Pt(20)
        np1.font.bold = True
        np1.font.color.rgb = BLUE
        
        txt_box = s2.shapes.add_textbox(x + Inches(0.6), y - Inches(0.1), Inches(5.0), Inches(0.8))
        txt_tf = txt_box.text_frame
        tp1 = txt_tf.paragraphs[0]
        tp1.text = title
        tp1.font.name = "Malgun Gothic"
        tp1.font.size = Pt(14)
        tp1.font.bold = True
        tp1.font.color.rgb = NAVY
        tp2 = txt_tf.add_paragraph()
        tp2.text = desc
        tp2.font.name = "Malgun Gothic"
        tp2.font.size = Pt(10)
        tp2.font.color.rgb = GRAY

    # -------------------------------------------------------------
    # Slide 3: Executive Summary
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    h_score = r_data.get('scm_health_score', 0)
    lead_msg = f"SCM Health {h_score}pt 유지 중이나, 거점 과부하 및 결품 선제 대응 필요" if h_score >= 80 else "SCM Health 경고 수준, 즉각적 비상 조치 필요"
    add_page_header(s3, "Executive Summary", lead_msg, "3 / 11")

    kpi_w = 2.8
    add_kpi_block(s3, Inches(0.8), Inches(1.8), Inches(kpi_w), Inches(1.6), f"{r_data.get('real_fill_rate', 0.0)}%", "Order Fill Rate", f"OTIF {r_data.get('real_otif', 0.0):.1f}% 달성")
    add_kpi_block(s3, Inches(0.8 + kpi_w + 0.2), Inches(1.8), Inches(kpi_w), Inches(1.6), f"{r_data.get('real_otd', 0.0):.1f}%", "On-Time Delivery", f"Target {r_data.get('target_otd', 98.0):.1f}%")
    add_kpi_block(s3, Inches(0.8 + (kpi_w + 0.2)*2), Inches(1.8), Inches(kpi_w), Inches(1.6), f"{r_data.get('critical_risk_count', 0)}", "Critical Risk SKUs", "Projected Stock 기준", val_color=RED if r_data.get('critical_risk_count',0) > 0 else GREEN)
    add_kpi_block(s3, Inches(0.8 + (kpi_w + 0.2)*3), Inches(1.8), Inches(kpi_w), Inches(1.6), format_currency(r_data.get("tot_log_cost", 0)), "Total Logistics Cost", "선택 기간 누적")

    box_l = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.6), Inches(5.8), Inches(3.0))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = WHITE
    box_l.line.color.rgb = LIGHT_GRAY
    ltf = box_l.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "Key Findings & Risk Areas"
    lp1.font.name = "Malgun Gothic"
    lp1.font.size = Pt(14)
    lp1.font.bold = True
    lp1.font.color.rgb = NAVY
    for iss in ["• 거점 병목: BUSAN_DC 가동률 90% 초과 (피크시즌 병목 예상)", f"• 결품 위험: 재고 고갈 예상 품목 {r_data.get('critical_risk_count',0)}건 발생", f"• 납기 변동: 고위험 공급사 {len(r_data.get('high_variance_suppliers',[]))}곳 리드타임 지연 확대"]:
        p = ltf.add_paragraph()
        p.text = iss
        p.font.name = "Malgun Gothic"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN

    box_r = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.6), Inches(5.7), Inches(3.0))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = WHITE
    box_r.line.color.rgb = LIGHT_GRAY
    rtf = box_r.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "Management Message"
    rp1.font.name = "Malgun Gothic"
    rp1.font.size = Pt(14)
    rp1.font.bold = True
    rp1.font.color.rgb = NAVY
    rp2 = rtf.add_paragraph()
    rp2.text = f"디지털 트윈 시뮬레이션 결과, 목표 성장률(+{r_data.get('target_rev_growth',0.15)*100:.1f}%) 달성 시 물동량 증가로 인한 거점 병목이 즉각 발생할 것으로 예상됩니다. FTL 적재율 개선을 통한 운송비 효율화와 핵심 SKU 안전재고 재조정이 선행되어야 합니다."
    rp2.font.name = "Malgun Gothic"
    rp2.font.size = Pt(12)
    rp2.font.color.rgb = TEXT_SUB

    # -------------------------------------------------------------
    # Slide 4: Today's Operation
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_page_header(s4, "Today's Operation", "실시간 물동량 및 현장 재고/출고 모니터링", "4 / 11")
    
    op_kpis = [
        (f"{r_data.get('t_inbound', 0):,} EA", "Inbound (입고예정)", "정시 입고율 관리 대상"),
        (f"{r_data.get('t_outbound', 0):,} EA", "Outbound (실제출고)", "일일 목표 달성도 반영"),
        (f"{r_data.get('t_orders', 0):,} EA", "Orders (주문접수)", "OMS 접수 확정 기준"),
        (format_currency(r_data.get('t_cost', 0)), "Daily Cost (발생물류비)", "운송/하역/인건 집계")
    ]
    for i, (val, label, sub) in enumerate(op_kpis):
        add_kpi_block(s4, Inches(0.8), Inches(1.8 + i*1.2), Inches(3.5), Inches(1.05), val, label, sub)
    
    op_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.5), Inches(1.8), Inches(8.0), Inches(4.7))
    op_box.fill.solid()
    op_box.fill.fore_color.rgb = WHITE
    op_box.line.color.rgb = LIGHT_GRAY
    otf = op_box.text_frame
    op1 = otf.paragraphs[0]
    op1.text = "Operational Status & Insights"
    op1.font.name = "Malgun Gothic"
    op1.font.size = Pt(16)
    op1.font.bold = True
    op1.font.color.rgb = NAVY
    
    op2 = otf.add_paragraph()
    op2.text = f"\n• 현재 전사 총 재고량은 {r_data.get('t_stock', 0):,} EA 유지 중"
    op2.font.name = "Malgun Gothic"
    op2.font.size = Pt(13)
    op2.font.color.rgb = TEXT_MAIN
    
    op3 = otf.add_paragraph()
    op3.text = f"• {r_data.get('busan_comment','').replace('<b>','').replace('</b>','')}"
    op3.font.name = "Malgun Gothic"
    op3.font.size = Pt(13)
    op3.font.color.rgb = TEXT_MAIN

    op4 = otf.add_paragraph()
    op4.text = f"• 일일 출고 마감 전 잔여 품절위험 품목 {r_data.get('t_risk_skus', 0)}개 특별 관제 중"
    op4.font.name = "Malgun Gothic"
    op4.font.size = Pt(13)
    op4.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------
    # Slide 5: Warehouse
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_page_header(s5, "Warehouse Performance", "전국 거점 가동률 편차 심화 및 라우팅 분산 필요", "5 / 11")
    
    wh_sum = r_data.get("wh_summary", pd.DataFrame())
    if not wh_sum.empty:
        rows, cols_cnt = len(wh_sum) + 1, 4
        table_shape = s5.shapes.add_table(rows, cols_cnt, Inches(0.8), Inches(1.8), Inches(6.0), Inches(2.6))
        table = table_shape.table
        col_names = ["Warehouse", "Volume (EA)", "Utilization", "OTD"]
        for j, cn in enumerate(col_names):
            cell = table.cell(0, j)
            cell.text = cn
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            cell.text_frame.paragraphs[0].font.name = "Malgun Gothic"
            cell.text_frame.paragraphs[0].font.size = Pt(10)
            cell.text_frame.paragraphs[0].font.bold = True
            cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        for i, r in wh_sum.iterrows():
            row_data = [str(r["warehouse"]), f"{r['sales_quantity']:,}", f"{r['utilization_rate']:.1f}%", str(r["is_otd"])]
            for j, val in enumerate(row_data):
                cell = table.cell(i+1, j)
                cell.text = val
                cell.text_frame.paragraphs[0].font.name = "Malgun Gothic"
                cell.text_frame.paragraphs[0].font.size = Pt(11)
                cell.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN
                if j == 2 and r['utilization_rate'] >= 90:
                    cell.text_frame.paragraphs[0].font.bold = True
                    cell.text_frame.paragraphs[0].font.color.rgb = RED

    wh_chart_buf = create_chart_image("warehouse", r_data)
    s5.shapes.add_picture(wh_chart_buf, Inches(7.1), Inches(1.8), width=Inches(5.4))

    # -------------------------------------------------------------
    # Slide 6: Cost
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_page_header(s6, "Logistics Cost", "간선 운송비 중심의 원가 구조 개선 및 FTL 표준화 필요", "6 / 11")
    
    add_kpi_block(s6, Inches(0.8), Inches(1.8), Inches(3.5), Inches(1.2), format_currency(r_data.get("tot_log_cost", 0)), "Total Logistics Cost", "기간 누적", val_color=NAVY)
    avg_cpu = r_data.get("filtered_df", pd.DataFrame())["cost_per_unit"].mean() if not r_data.get("filtered_df", pd.DataFrame()).empty else 0
    add_kpi_block(s6, Inches(0.8), Inches(3.2), Inches(3.5), Inches(1.2), f"₩{avg_cpu:,.1f}", "Cost per EA", "단위당 처리 원가", val_color=GRAY)

    cost_chart_buf = create_chart_image("cost", r_data)
    s6.shapes.add_picture(cost_chart_buf, Inches(4.5), Inches(1.8), width=Inches(4.5))

    c_break = r_data.get("cost_breakdown", pd.DataFrame())
    if not c_break.empty:
        c_table = s6.shapes.add_table(6, 2, Inches(9.2), Inches(1.8), Inches(3.3), Inches(2.6)).table
        c_table.cell(0, 0).text = "Cost Driver"
        c_table.cell(0, 1).text = "Amount"
        c_table.cell(0, 0).fill.solid()
        c_table.cell(0, 0).fill.fore_color.rgb = NAVY
        c_table.cell(0, 1).fill.solid()
        c_table.cell(0, 1).fill.fore_color.rgb = NAVY
        c_table.cell(0, 0).text_frame.paragraphs[0].font.color.rgb = WHITE
        c_table.cell(0, 1).text_frame.paragraphs[0].font.color.rgb = WHITE
        for i, r in c_break.iterrows():
            c_table.cell(i+1, 0).text = str(r["비용항목"])
            c_table.cell(i+1, 1).text = format_currency(r["금액"])
            c_table.cell(i+1, 0).text_frame.paragraphs[0].font.name = "Malgun Gothic"
            c_table.cell(i+1, 1).text_frame.paragraphs[0].font.name = "Malgun Gothic"
            c_table.cell(i+1, 0).text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN
            c_table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN
            c_table.cell(i+1, 1).text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT

    # -------------------------------------------------------------
    # Slide 7: Inventory
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_page_header(s7, "Inventory & Stock Risk", "Projected Stock 기반 안전재고 미달 품목 긴급 버퍼링 요망", "7 / 11")
    
    inv_df_sub = r_data.get("inv_df", pd.DataFrame())
    if not inv_df_sub.empty:
        i_rows = min(8, len(inv_df_sub)) + 1
        i_table = s7.shapes.add_table(i_rows, 5, Inches(0.8), Inches(1.8), Inches(8.0), Inches(4.5)).table
        i_cols = ["SKU명", "현재고량", "입고예정", "가용예측(Proj.)", "Risk"]
        for j, cn in enumerate(i_cols):
            cell = i_table.cell(0, j)
            cell.text = cn
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            cell.text_frame.paragraphs[0].font.name = "Malgun Gothic"
            cell.text_frame.paragraphs[0].font.bold = True
            cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        for i, r in inv_df_sub.head(8).iterrows():
            row_vals = [str(r["product_name"]), f"{r['stock_quantity']:,}", f"{r['expected_inbound']:,}", f"{r['projected_stock']:.1f}", str(r["risk_level"])]
            for j, v in enumerate(row_vals):
                cell = i_table.cell(i+1, j)
                cell.text = v
                cell.text_frame.paragraphs[0].font.name = "Malgun Gothic"
                cell.text_frame.paragraphs[0].font.size = Pt(10)
                cell.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN
                if j == 4 and v in ["CRITICAL", "WARNING"]:
                    cell.text_frame.paragraphs[0].font.bold = True
                    cell.text_frame.paragraphs[0].font.color.rgb = RED

    add_kpi_block(s7, Inches(9.2), Inches(1.8), Inches(3.3), Inches(1.2), f"{r_data.get('critical_risk_count',0)}", "Critical SKUs", "즉시 발주 필요", val_color=RED)

    # -------------------------------------------------------------
    # Slide 8: Forecast
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_page_header(s8, "Demand Forecast Accuracy", "WMAPE 오차율 관리 및 피크시즌 예측 편향 보정", "8 / 11")
    
    w_val = r_data.get('wmape_val', 0.0)
    add_kpi_block(s8, Inches(0.8), Inches(1.8), Inches(4.0), Inches(1.8), f"{w_val:.1f}%", "WMAPE", "수요예측오차율 (낮을수록 우수)")
    add_kpi_block(s8, Inches(0.8), Inches(3.8), Inches(4.0), Inches(1.8), f"{100-w_val:.1f}%", "Forecast Accuracy", "전사 예측 정확도")

    trend_chart_buf = create_chart_image("trend", r_data)
    s8.shapes.add_picture(trend_chart_buf, Inches(5.2), Inches(1.8), width=Inches(7.3))

    # -------------------------------------------------------------
    # Slide 9: Supplier
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_page_header(s9, "Supplier Performance", "리드타임 변동계수(CV) 고위험 공급선 대상 듀얼 소싱 추진", "9 / 11")
    
    s_perf = r_data.get("sup_perf", pd.DataFrame())
    if not s_perf.empty:
        s_table = s9.shapes.add_table(len(s_perf) + 1, 5, Inches(0.8), Inches(1.8), Inches(7.5), Inches(3.4)).table
        s_cols = ["Supplier", "Avg LT", "OTD(%)", "CV", "Risk Level"]
        for j, cn in enumerate(s_cols):
            cell = s_table.cell(0, j)
            cell.text = cn
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        for i, r in s_perf.iterrows():
            row_data = [str(r.get("supplier", "")), f"{r.get('평균리드타임', 0):.1f}", f"{r.get('OTD(%)', 0):.1f}%", f"{r.get('변동계수(CV)', 0):.2f}", str(r.get("리스크등급", ""))]
            for j, val in enumerate(row_data):
                cell = s_table.cell(i+1, j)
                cell.text = val
                cell.text_frame.paragraphs[0].font.name = "Malgun Gothic"
                cell.text_frame.paragraphs[0].font.size = Pt(10)
                cell.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN
                if j == 4 and "High" in val:
                    cell.text_frame.paragraphs[0].font.bold = True
                    cell.text_frame.paragraphs[0].font.color.rgb = RED

    h_list = ", ".join(r_data.get('high_variance_suppliers', [])) or "없음"
    add_kpi_block(s9, Inches(8.7), Inches(1.8), Inches(3.8), Inches(1.5), str(len(r_data.get('high_variance_suppliers', []))), "High Variance Suppliers", f"CV 0.35 초과: {h_list}", val_color=RED)

    # -------------------------------------------------------------
    # Slide 10: Digital Twin
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_page_header(s10, "2027 Digital Twin Strategy", "전사 목표 달성 시뮬레이션 및 비용/서비스 상충관계 분석", "10 / 11")
    
    dt_cards = [
        ("2026 ACTUAL", format_currency(r_data.get('base_rev_2026',0)), f"{int(r_data.get('base_vol_2026',0)):,}", format_currency(r_data.get('base_cost_2026',0)), f"{r_data.get('base_otd_2026',0.0):.1f}%", NAVY),
        (f"2027 TARGET (+{r_data.get('target_rev_growth',0.15)*100:.0f}%)", format_currency(r_data.get('target_rev_2027',0)), f"{int(r_data.get('target_vol_2027',0)):,}", format_currency(r_data.get('target_cost_2027',0)), f"{r_data.get('target_otd',98.0):.1f}%", BLUE),
        (f"2027 WHAT-IF (+{r_data.get('sim_rev_growth',0.15)*100:.0f}%)", format_currency(r_data.get('forecast_rev_2027',0)), f"{int(r_data.get('forecast_vol_2027',0)):,}", format_currency(r_data.get('forecast_cost_2027',0)), f"{r_data.get('forecast_otd_2027',0.0):.1f}%", GREEN)
    ]
    
    for i, (title, rev, vol, cost, otd_v, color) in enumerate(dt_cards):
        x = Inches(0.8 + i * 4.0)
        box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(3.8), Inches(4.2))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = LIGHT_GRAY
        tf = box.text_frame
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Malgun Gothic"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        
        tf.add_paragraph().text = ""
        
        items = [("Revenue", rev), ("Volume", vol), ("Logistics Cost", cost), ("OTD", otd_v)]
        for label, val in items:
            p2 = tf.add_paragraph()
            p2.text = f"{label}\n{val}\n"
            p2.font.name = "Malgun Gothic"
            p2.font.size = Pt(12)
            p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------
    # Slide 11: Action Plan
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_page_header(s11, "Management Action Plan", "이슈 해결 및 전략 달성을 위한 우선 순위 실행 로드맵", "11 / 11")
    
    actions = [
        ("01 Immediate (1-2 Weeks)", "BUSAN_DC 가동률 90% 초과 병목", "야간조 인력 +10% 탄력 증원 및 대전/수도권 우회 배차", "CSO"),
        ("02 Short-term (1-3 Months)", "해외 공급사 리드타임 CV 확대", "국내 서브 공급사와의 듀얼 소싱(Dual Sourcing) 계약 체결", "CPO"),
        ("03 Mid-term (3-6 Months)", "Projected Stock 마이너스 품목 발생", "A/B 등급 핵심 SKU 안전재고 버퍼 +15% 상향 조정", "Supply Planners"),
        ("04 Strategic (2027)", "간선 운송비 과다 및 차량 적재율 저하", "라인홀(Line-haul) FTL 표준화 및 공동 배차 알고리즘 도입", "Logistics VP")
    ]
    
    for i, (period, issue, action, owner) in enumerate(actions):
        y = Inches(1.8 + i * 1.2)
        box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(1.0))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = LIGHT_GRAY
        tf = box.text_frame
        
        p = tf.paragraphs[0]
        p.text = period
        p.font.name = "Malgun Gothic"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = BLUE
        
        p2 = tf.add_paragraph()
        p2.text = f"• Issue: {issue}   |   • Action: {action}   |   • Owner: {owner}"
        p2.font.name = "Malgun Gothic"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MAIN

    ppt_buf = io.BytesIO()
    prs.save(ppt_buf)
    ppt_buf.seek(0)
    return ppt_buf

def generate_pdf_report(r_data):
    """독립적인 6페이지 A4 가로형 Executive Management PDF Report 생성"""
    pdf_buf = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buf, pagesize=landscape(A4),
        leftMargin=30, rightMargin=30, topMargin=25, bottomMargin=25
    )

    font_name = get_korean_font_name()
    font_bold = font_name

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("RepTitle", parent=styles["Normal"], fontName=font_bold, fontSize=20, leading=24, textColor=colors.HexColor("#0F172A"))
    sub_style = ParagraphStyle("RepSub", parent=styles["Normal"], fontName=font_name, fontSize=10, leading=14, textColor=colors.HexColor("#64748B"))
    h2_style = ParagraphStyle("RepH2", parent=styles["Normal"], fontName=font_bold, fontSize=14, leading=18, textColor=colors.HexColor("#0066CC"), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("RepBody", parent=styles["Normal"], fontName=font_name, fontSize=9.5, leading=14, textColor=colors.HexColor("#1D1D1F"))

    story = []
    dt_str = r_data.get('max_data_date', datetime.now()).strftime('%Y-%m-%d')

    # Page 1: Cover & Executive Summary
    story.append(Paragraph("SCM EXECUTIVE CONTROL TOWER REPORT", title_style))
    chs = ", ".join(r_data.get('selected_channels', ['All']))
    whs = ", ".join(r_data.get('selected_wh', ['All']))
    story.append(Paragraph(f"Data Updated: {dt_str} | Channels: {chs} | DCs: {whs}", sub_style))
    story.append(Spacer(1, 15))

    kpi_data = [
        ["SCM Health Score", "Order Fill Rate", "OTD", "OTIF", "Est. Turnover", "Total Logistics Cost"],
        [
            f"{r_data.get('scm_health_score', 0)} pt", 
            f"{r_data.get('real_fill_rate', 0.0)}%", 
            f"{r_data.get('real_otd', 0.0):.1f}%", 
            f"{r_data.get('real_otif', 0.0):.1f}%", 
            f"{r_data.get('real_turnover', 0.0)}x", 
            format_currency(r_data.get("tot_log_cost", 0))
        ]
    ]
    table_kpi = Table(kpi_data, colWidths=[130]*6)
    table_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#FFFFFF")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5EA"))
    ]))
    story.append(table_kpi)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Executive Action Required", h2_style))
    b_comm = r_data.get('busan_comment','').replace('<b>','').replace('</b>','')
    c_comm = r_data.get('cost_comment','').replace('<b>','').replace('</b>','')
    story.append(Paragraph(f"• 물류센터 상태: {b_comm}", body_style))
    story.append(Paragraph(f"• 물류비 절감 상태: {c_comm}", body_style))
    story.append(Paragraph(f"• 품절 위험 리스크: 현재고 및 Projected Stock 기준 안전재고 미달 품목은 총 {r_data.get('critical_risk_count',0)}건입니다.", body_style))
    story.append(PageBreak())

    # Page 2: Warehouse Performance
    story.append(Paragraph("Warehouse Capacity & DC Performance", title_style))
    story.append(Spacer(1, 10))
    wh_sum = r_data.get("wh_summary", pd.DataFrame())
    wh_tbl_data = [["물류센터", "출고량 (EA)", "가동률 (%)", "총 물류비", "정시도착률 (OTD)"]]
    if not wh_sum.empty:
        for _, r in wh_sum.iterrows():
            wh_tbl_data.append([str(r["warehouse"]), f"{r['sales_quantity']:,}", f"{r['utilization_rate']:.1f}%", format_currency(r["total_logistics_cost"]), str(r["is_otd"])])
    table_wh = Table(wh_tbl_data, colWidths=[150]*5)
    table_wh.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#FFFFFF")),
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5EA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table_wh)
    story.append(PageBreak())

    # Page 3: Logistics Cost Structure
    story.append(Paragraph("Logistics Cost Structure & Efficiency", title_style))
    story.append(Spacer(1, 10))
    c_break = r_data.get("cost_breakdown", pd.DataFrame())
    cost_tbl_data = [["비용 항목", "발생 금액 (원)"]]
    if not c_break.empty:
        for _, r in c_break.iterrows():
            cost_tbl_data.append([str(r["비용항목"]), format_currency(r["금액"])])
    table_cost = Table(cost_tbl_data, colWidths=[200, 200])
    table_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#FFFFFF")),
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5EA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table_cost)
    story.append(PageBreak())

    # Page 4: Inventory & Demand Forecast
    story.append(Paragraph("Inventory Health & Forecast Accuracy", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"• 전사 누적 WMAPE: {r_data.get('wmape_val', 0.0):.1f}% | 예측 정확도: {100 - r_data.get('wmape_val', 0.0):.1f}%", body_style))
    story.append(Spacer(1, 8))
    inv_df_sub = r_data.get("inv_df", pd.DataFrame())
    inv_tbl = [["SKU명", "현재고량", "입고예정", "가용재고(Proj.)", "DOH(일)", "리스크등급"]]
    if not inv_df_sub.empty:
        for _, r in inv_df_sub.head(8).iterrows():
            inv_tbl.append([str(r["product_name"]), f"{r['stock_quantity']:,}", f"{r['expected_inbound']:,}", f"{r['projected_stock']:.1f}", f"{r['days_on_hand']:.1f}", str(r["risk_level"])])
    table_inv = Table(inv_tbl, colWidths=[130]*6)
    table_inv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#FFFFFF")),
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5EA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(table_inv)
    story.append(PageBreak())

    # Page 5: Supplier Performance
    story.append(Paragraph("Supplier Reliability & Risk", title_style))
    story.append(Spacer(1, 10))
    s_perf = r_data.get("sup_perf", pd.DataFrame())
    sup_tbl = [["공급사명", "평균리드타임", "정시도착률(OTD)", "변동계수(CV)", "리스크등급"]]
    if not s_perf.empty:
        for _, r in s_perf.iterrows():
            sup_tbl.append([str(r.get("supplier", "")), f"{r.get('평균리드타임', 0):.1f}일", f"{r.get('OTD(%)', 0):.1f}%", f"{r.get('변동계수(CV)', 0):.2f}", str(r.get("리스크등급", ""))])
    table_sup = Table(sup_tbl, colWidths=[150]*5)
    table_sup.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#FFFFFF")),
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5EA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table_sup)
    story.append(PageBreak())

    # Page 6: 2027 Digital Twin
    story.append(Paragraph("2027 Digital Twin Strategy & Execution", title_style))
    story.append(Spacer(1, 10))
    dt_data = [
        ["구분", "2026 Actual (전사 실적)", f"2027 Target (+{r_data.get('target_rev_growth',0.15)*100:.1f}%)", f"2027 Forecast ({r_data.get('sim_rev_growth',0.15)*100:.1f}%)"],
        ["총 매출액", format_currency(r_data.get('base_rev_2026',0)), format_currency(r_data.get('target_rev_2027',0)), format_currency(r_data.get('forecast_rev_2027',0))],
        ["총 물동량", f"{int(r_data.get('base_vol_2026',0)):,} EA", f"{int(r_data.get('target_vol_2027',0)):,} EA", f"{int(r_data.get('forecast_vol_2027',0)):,} EA"],
        ["총 물류비", format_currency(r_data.get('base_cost_2026',0)), format_currency(r_data.get('target_cost_2027',0)), format_currency(r_data.get('forecast_cost_2027',0))],
        ["정시도착률(OTD)", f"{r_data.get('base_otd_2026',0.0):.1f}%", f"{r_data.get('target_otd',98.0):.1f}%", f"{r_data.get('forecast_otd_2027',0.0):.1f}%"]
    ]
    table_dt = Table(dt_data, colWidths=[180]*4)
    table_dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#FFFFFF")),
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5EA")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table_dt)
    story.append(Spacer(1, 15))
    story.append(Paragraph("Strategic Action Plan", h2_style))
    story.append(Paragraph("1. 거점 인터모달 분산: BUSAN_DC 과부하 방지를 위한 내륙 거점(대전/수도권) 분산 배차", body_style))
    story.append(Paragraph("2. 공급사 듀얼 소싱: 리드타임 변동성이 높은 고위험 공급사 대상 대체 공급선 확보", body_style))
    story.append(Paragraph("3. 안전재고 전략: Projected Stock 마이너스 SKU 긴급 발주 및 버퍼 상향", body_style))
    story.append(Paragraph("4. 간선 운임 최적화: FTL 적재율 표준화를 통한 단위당 물류비 절감 달성", body_style))

    doc.build(story)
    pdf_buf.seek(0)
    return pdf_buf

# ==============================================================================
# [9. Header & Management Report Download Bar]
# ==============================================================================
st.markdown(
    f"""
    <div class="control-tower-header">
        <div>
            <div class="traffic-lights">
                <div class="dot dot-red"></div>
                <div class="dot dot-yellow"></div>
                <div class="dot dot-green"></div>
            </div>
            <div class="custom-h1">🏢 SCM Executive Control Tower & Digital Twin</div>
            <p style="margin: 3px 0 0 0; color: #86868B; font-size: 0.85rem;">
                Enterprise Supply Chain Intelligence | <b>System:</b> <span style="color: #34C759; font-weight:700;">● Operational</span>
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-size: 0.85rem; color: #86868B;"><b>Data Updated:</b> {max_data_date.strftime('%Y-%m-%d')}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #86868B;"><b>Data Source:</b> Simulation Dataset (ERP API Ready)</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

rep_col_left, rep_col_mid, rep_col_right = st.columns([2.5, 1, 1])
with rep_col_left:
    st.markdown(
        """
        <div style="padding: 4px 0;">
            <b style="font-size: 0.95rem; color: #1D1D1F;">📑 Management Report</b>
            <span style="font-size: 0.82rem; color: #86868B; margin-left: 6px;">실시간 KPI & 2027 시뮬레이션 기반 자동 생성 보고서</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with rep_col_mid:
    st.download_button(
        label="📊 PPT 보고서 다운로드",
        data=generate_pptx_report(report_data),
        file_name=f"SCM_Executive_Report_{max_data_date.strftime('%Y-%m-%d')}.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True
    )
with rep_col_right:
    st.download_button(
        label="📄 PDF 보고서 다운로드",
        data=generate_pdf_report(report_data),
        file_name=f"SCM_Executive_Report_{max_data_date.strftime('%Y-%m-%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("<div style='margin-bottom: 0.4rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# [10. Intelligent Alert Center (동적 룰 엔진)]
# ==============================================================================
alert_items = []
if busan_util >= 90.0:
    alert_items.append(f"<li><span style='color: #FF3B30;'>[Critical]</span> BUSAN_DC 가동률 과부하 경보 <span class='badge-red'>{busan_util:.1f}%</span> (도크 분산 및 추가 인력 배치 필요)</li>")
elif busan_util >= 80.0:
    alert_items.append(f"<li><span style='color: #FF9500;'>[Watch]</span> BUSAN_DC 가동률 관찰 단계 <span class='badge-yellow'>{busan_util:.1f}%</span></li>")
else:
    alert_items.append(f"<li><span style='color: #34C759;'>[Normal]</span> 전국 물류센터 가동률 정상 범위 유지 중 (BUSAN_DC: {busan_util:.1f}%)</li>")

if critical_risk_count > 0:
    alert_items.append(f"<li><span style='color: #FF3B30;'>[Critical]</span> 안전재고 미달 품절 위험 SKU 발생 <span class='badge-red'>{critical_risk_count}건</span> (Projected Stock 기준 발주 요망)</li>")
else:
    alert_items.append("<li><span style='color: #34C759;'>[Normal]</span> 현재 안전재고 미달 품목 없음</li>")

if high_variance_suppliers:
    alert_items.append(f"<li><span style='color: #FF9500;'>[Warning]</span> 공급사 리드타임 변동성 확대 ({', '.join(high_variance_suppliers)}) <span class='badge-yellow'>납기 지연 리스크</span></li>")
else:
    alert_items.append("<li><span style='color: #34C759;'>[Normal]</span> 주요 공급사 리드타임 변동성 안정 범위</li>")

if sim_cost_reduction >= target_cost_reduction:
    alert_items.append(f"<li><span style='color: #34C759;'>[Achieved]</span> 2027 물류비 절감 시뮬레이션({sim_cost_reduction*100:.1f}%)이 경영진 목표치({target_cost_reduction*100:.1f}%)를 충족합니다.</li>")
else:
    alert_items.append(f"<li><span style='color: #FF9500;'>[Notice]</span> 2027 물류비 절감 시뮬레이션({sim_cost_reduction*100:.1f}%)이 목표치({target_cost_reduction*100:.1f}%)에 소폭 미달합니다.</li>")

alert_html = "".join(alert_items)
st.markdown(
    f"""
    <div class="intelligent-alert-box">
        <div style="font-weight:700; color:#FF3B30; font-size:0.92rem; margin-bottom:4px;">🚨 Intelligent Alert Center (동적 관제 경보)</div>
        <ul>{alert_html}</ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# [11. Today's Operation Summary (KPI 6개)]
# ==============================================================================
st.markdown("<div class='custom-h2'>📋 Today's Operation Summary (데이터 기준 최신일 현황)</div>", unsafe_allow_html=True)
tc1, tc2, tc3, tc4, tc5, tc6 = st.columns(6)
with tc1: st.metric("오늘 입고예정량", f"{t_inbound:,} EA")
with tc2: st.metric("오늘 실제출고량", f"{t_outbound:,} EA")
with tc3: st.metric("오늘 주문접수량", f"{t_orders:,} EA")
with tc4: st.metric("오늘 발생물류비", format_currency(t_cost))
with tc5: st.metric("현재고 총합계", f"{t_stock:,} EA")
with tc6: st.metric("품절위험 품목수", f"{t_risk_skus} 개", delta="주의" if t_risk_skus > 0 else "양호", delta_color="inverse")

st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# [12. Individual Menu Dashboards Rendering]
# ==============================================================================

if selected_menu == "1. Executive Dashboard":
    st.markdown("<div class='custom-h2'>📊 Executive Dashboard (경영진 핵심 관제 지표)</div>", unsafe_allow_html=True)
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1: st.metric("SCM Health Score", f"{scm_health_score}점", delta="정상" if scm_health_score >= 80 else "주의")
    with m2: st.metric("Order Fill Rate", f"{real_fill_rate}%", delta=f"OTIF {real_otif:.1f}%")
    with m3: st.metric("OTD (정시도착률)", f"{real_otd:.1f}%", delta=f"목표 {target_otd:.1f}% 대비")
    with m4: st.metric("Est. Inventory Turnover", f"{real_turnover} 회", delta="COGS 프록시")
    with m5: st.metric("Stockout Risk", f"{critical_risk_count} 건", delta="위험" if critical_risk_count > 0 else "안정", delta_color="inverse")
    with m6: st.metric("Total Logistics Cost", format_currency(tot_log_cost))

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='custom-h3'>채널별 총 매출 점유율</div>", unsafe_allow_html=True)
        ch_grp = filtered_df.groupby("channel")[["revenue"]].sum().reset_index()
        fig_ch = px.bar(ch_grp, x="channel", y="revenue", color="channel", text_auto=".2s")
        fig_ch.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False, height=330, margin=dict(l=15, r=15, t=15, b=15),
            font=dict(size=12, color="#1D1D1F")
        )
        st.plotly_chart(fig_ch, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with c2:
        st.markdown("<div class='custom-h3'>월별 출고량 추이 및 피크 구간</div>", unsafe_allow_html=True)
        trend_exec = filtered_df.groupby("year_month")["sales_quantity"].sum().reset_index()
        fig_trend = px.line(trend_exec, x="year_month", y="sales_quantity")
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickangle=-45), height=330, margin=dict(l=15, r=15, t=15, b=15),
            font=dict(size=12, color="#1D1D1F")
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False, "responsive": True})

elif selected_menu == "2. Daily Operation Dashboard":
    st.markdown("<div class='custom-h2'>📅 Daily Operation Dashboard (일자별 운영 현황)</div>", unsafe_allow_html=True)
    daily_agg = filtered_df.groupby("date_str").agg({
        "order_quantity": "sum",
        "sales_quantity": "sum",
        "total_logistics_cost": "sum",
        "stock_quantity": "sum",
        "utilization_rate": "mean"
    }).reset_index().sort_values(by="date_str", ascending=False)

    daily_agg.columns = ["일자", "주문량(EA)", "출고량(EA)", "총물류비", "재고량(EA)", "평균가동률(%)"]
    daily_agg["총물류비"] = daily_agg["총물류비"].apply(format_currency)
    daily_agg["평균가동률(%)"] = daily_agg["평균가동률(%)"].round(1)
    st.dataframe(daily_agg, use_container_width=True, height=400)

elif selected_menu == "3. Warehouse Dashboard":
    st.markdown("<div class='custom-h2'>🏭 Warehouse Dashboard (물류센터 가동률 및 Capacity)</div>", unsafe_allow_html=True)
    cols = st.columns(len(wh_summary) if len(wh_summary) > 0 else 1)
    for idx, row in wh_summary.iterrows():
        wh_name = row["warehouse"]
        u_val = row["utilization_rate"]
        ship_q = f"{row['sales_quantity']:,} EA"
        c_val = format_currency(row["total_logistics_cost"])
        o_val = row["is_otd"]

        status = "Critical" if u_val >= 95 else ("Warning" if u_val >= 85 else "Normal")
        b_color = "#FF3B30" if status == "Critical" else ("#FF9500" if status == "Warning" else "#34C759")
        badge = f"<span class='badge-red'>{status}</span>" if status == "Critical" else (f"<span class='badge-yellow'>{status}</span>" if status == "Warning" else f"<span class='badge-green'>{status}</span>")

        with cols[idx]:
            st.markdown(
                f"""
                <div class="custom-card" style="border: 2px solid {b_color};">
                    <div>
                        <div class="card-header-title">
                            <span>{wh_name}</span>
                            <span>{badge}</span>
                        </div>
                        <div class="card-data-row"><span>총 출고량</span><b>{ship_q}</b></div>
                        <div class="card-data-row"><span>평균 가동률</span><b>{u_val:.1f}%</b></div>
                        <div class="card-data-row"><span>총 물류비</span><b>{c_val}</b></div>
                    </div>
                    <div class="card-data-row" style="border-top: 1px dashed var(--border-color); padding-top: 6px; margin-top: 6px;">
                        <span>정시도착률(OTD)</span><b>{o_val}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
    wh_disp = wh_summary.copy()
    wh_disp.columns = ["물류센터", "출고량(EA)", "평균가동률(%)", "총물류비", "OTD"]
    wh_disp["총물류비"] = wh_disp["총물류비"].apply(format_currency)
    wh_disp["평균가동률(%)"] = wh_disp["평균가동률(%)"].round(1)
    st.dataframe(wh_disp, use_container_width=True, height=220)

elif selected_menu == "4. Logistics Cost Dashboard":
    st.markdown("<div class='custom-h2'>💰 Logistics Cost Dashboard (실집계 물류비 분석)</div>", unsafe_allow_html=True)
    avg_cpu = filtered_df["cost_per_unit"].mean()

    lc1, lc2 = st.columns(2)
    with lc1: st.metric("총 발생 물류비", format_currency(tot_log_cost))
    with lc2: st.metric("단위당 물류비 (Cost per EA)", f"₩{avg_cpu:,.1f}")

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
    fig_pie = px.pie(cost_breakdown, names="비용항목", values="금액", hole=0.45)
    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(size=12), height=340, margin=dict(l=15, r=15, t=15, b=15))
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False, "responsive": True})

elif selected_menu == "5. Inventory Dashboard":
    st.markdown("<div class='custom-h2'>📦 Inventory Dashboard (Projected Stock & DOH 관제)</div>", unsafe_allow_html=True)
    inv_disp = inv_df.copy()
    inv_disp.columns = ["SKU 품목명", "현재고량(EA)", "입고예정량(EA)", "가용재고예측(Projected)", "재고일수(DOH)", "리스크레벨"]
    inv_disp["가용재고예측(Projected)"] = inv_disp["가용재고예측(Projected)"].round(1)
    inv_disp["재고일수(DOH)"] = inv_disp["재고일수(DOH)"].round(1)
    st.dataframe(inv_disp, use_container_width=True, height=400)

elif selected_menu == "6. Demand Forecast Dashboard":
    st.markdown("<div class='custom-h2'>📈 Demand Forecast Dashboard (예측 오차 및 WMAPE 분석)</div>", unsafe_allow_html=True)
    st.markdown(f"**전사 누적 WMAPE (수요예측오차율):** <b>{wmape_val:.1f}%</b> | **정확도(Accuracy):** <b>{100 - wmape_val:.1f}%</b>", unsafe_allow_html=True)
    fc_display = fc_agg.rename(columns={"year_month": "연도-월", "forecast_quantity": "수요예측수량(EA)", "sales_quantity": "실제판매수량(EA)"})
    st.dataframe(fc_display, use_container_width=True, height=360)

elif selected_menu == "7. ABC Analysis":
    st.markdown("<div class='custom-h2'>📊 ABC Analysis (누적 매출 비중 기준 자동 분류)</div>", unsafe_allow_html=True)
    sku_rev = filtered_df.groupby("product_name")["revenue"].sum().reset_index()
    sku_rev = sku_rev.sort_values(by="revenue", ascending=False)
    tot_rev = max(1.0, sku_rev["revenue"].sum())
    sku_rev["cum_pct"] = (sku_rev["revenue"].cumsum() / tot_rev) * 100.0

    def assign_abc(p):
        if p <= 80.0: return "A등급 (핵심 80%)"
        elif p <= 95.0: return "B등급 (중간 15%)"
        else: return "C등급 (일반 5%)"

    sku_rev["ABC등급"] = sku_rev["cum_pct"].apply(assign_abc)

    col1, col2 = st.columns([1, 1])
    with col1:
        abc_summary = sku_rev.groupby("ABC등급")["revenue"].sum().reset_index()
        fig_abc = px.pie(abc_summary, names="ABC등급", values="revenue", hole=0.45)
        fig_abc.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(l=15, r=15, t=15, b=15))
        st.plotly_chart(fig_abc, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    with col2:
        sku_rev_disp = sku_rev[["product_name", "revenue", "cum_pct", "ABC등급"]].copy()
        sku_rev_disp.columns = ["SKU 품목명", "총매출액", "누적비중(%)", "ABC등급"]
        sku_rev_disp["총매출액"] = sku_rev_disp["총매출액"].apply(format_currency)
        sku_rev_disp["누적비중(%)"] = sku_rev_disp["누적비중(%)"].round(1)
        st.dataframe(sku_rev_disp, use_container_width=True, height=320)

elif selected_menu == "8. ABC-XYZ Matrix":
    st.markdown("<div class='custom-h2'>🔲 ABC-XYZ Matrix (수요 변동성 기반 실제 SKU 매핑)</div>", unsafe_allow_html=True)
    sku_stats = filtered_df.groupby("product_name").agg({
        "revenue": "sum",
        "sales_quantity": ["mean", "std"]
    })
    sku_stats.columns = ["total_rev", "qty_mean", "qty_std"]
    sku_stats = sku_stats.reset_index()
    sku_stats["qty_std"] = sku_stats["qty_std"].fillna(0)
    sku_stats["cv"] = sku_stats["qty_std"] / sku_stats["qty_mean"].replace(0, 1)

    sku_stats = sku_stats.sort_values(by="total_rev", ascending=False)
    sku_stats["cum_pct"] = (sku_stats["total_rev"].cumsum() / max(1.0, sku_stats["total_rev"].sum())) * 100.0
    sku_stats["A_Class"] = sku_stats["cum_pct"].apply(lambda p: "A" if p <= 80 else ("B" if p <= 95 else "C"))
    sku_stats["X_Class"] = sku_stats["cv"].apply(lambda c: "X" if c <= 0.3 else ("Y" if c <= 0.6 else "Z"))
    sku_stats["Matrix_Zone"] = sku_stats["A_Class"] + sku_stats["X_Class"]

    zone_counts = sku_stats["Matrix_Zone"].value_counts().to_dict()
    matrix_info = [
        {"Zone": "AX", "의미": "고수익 / 안정수요", "전략": "자동보충 및 서비스수준 극대화", "품목수": zone_counts.get("AX", 0)},
        {"Zone": "AY", "의미": "고수익 / 중변동", "전략": "정기발주 및 안전재고 버퍼링", "품목수": zone_counts.get("AY", 0)},
        {"Zone": "AZ", "의미": "고수익 / 불규칙수요", "전략": "안전재고 대폭 강화 및 긴급발주 라인 확보", "품목수": zone_counts.get("AZ", 0)},
        {"Zone": "BX", "의미": "중수익 / 안정수요", "전략": "경제적 주문량(EOQ) 관리", "품목수": zone_counts.get("BX", 0)},
        {"Zone": "BY", "의미": "중수익 / 중변동", "전략": "공급사 연계 VMI 및 탄력 발주", "품목수": zone_counts.get("BY", 0)},
        {"Zone": "BZ", "의미": "중수익 / 불규칙수요", "전략": "수주 후 출고(MTO) 검토", "품목수": zone_counts.get("BZ", 0)},
        {"Zone": "CX", "의미": "저수익 / 안정수요", "전략": "일괄 대량발주 및 재고 최소화", "품목수": zone_counts.get("CX", 0)},
        {"Zone": "CY", "의미": "저수익 / 중변동", "전략": "재고 감축 및 표준화", "품목수": zone_counts.get("CY", 0)},
        {"Zone": "CZ", "의미": "저수익 / 불규칙수요", "전략": "단종 검토 및 재고 소진 정책", "품목수": zone_counts.get("CZ", 0)},
    ]
    st.dataframe(pd.DataFrame(matrix_info), use_container_width=True, height=360)

elif selected_menu == "9. Supplier Dashboard":
    st.markdown("<div class='custom-h2'>🌐 Supplier Dashboard (공급사 성과 및 리스크 평가)</div>", unsafe_allow_html=True)
    sup_disp = sup_perf.copy()
    sup_disp["평균리드타임"] = sup_disp["평균리드타임"].round(1)
    sup_disp["OTD(%)"] = sup_disp["OTD(%)"].round(1)
    sup_disp.columns = ["공급사명", "평균리드타임(일)", "표준편차", "OTD(%)", "발주건수", "변동계수(CV)", "리스크등급"]
    st.dataframe(sup_disp[["공급사명", "평균리드타임(일)", "OTD(%)", "변동계수(CV)", "발주건수", "리스크등급"]], use_container_width=True, height=360)

elif selected_menu == "10. 🎯 Digital Twin & What-if Planning (2027)":
    st.markdown("<div class='custom-h2'>🎯 Executive Digital Twin : Actual vs Target vs Forecast (2027)</div>", unsafe_allow_html=True)
    st.markdown("경영진 사업계획 목표(Target)와 What-if 시뮬레이션(Forecast) 간의 상충관계(Trade-off)를 정렬된 카드로 검토합니다.")

    gap_rev = ((forecast_rev_2027 - target_rev_2027) / max(1.0, target_rev_2027)) * 100.0

    dt1, dt2, dt3 = st.columns(3)
    with dt1:
        st.markdown(
            f"""
            <div class="custom-card">
                <div>
                    <div class="card-header-title">📌 2026 Actual (실적)</div>
                    <div class="card-data-row"><span>총 매출액</span><b>{format_currency(base_rev_2026)}</b></div>
                    <div class="card-data-row"><span>총 물동량</span><b>{int(base_vol_2026):,} EA</b></div>
                    <div class="card-data-row"><span>총 물류비</span><b>{format_currency(base_cost_2026)}</b></div>
                </div>
                <div class="card-data-row" style="border-top: 1px dashed var(--border-color); padding-top: 6px; margin-top: 6px;">
                    <span>정시배송률(OTD)</span><b>{base_otd_2026:.1f}%</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with dt2:
        st.markdown(
            f"""
            <div class="custom-card" style="border: 2px solid var(--color-blue);">
                <div>
                    <div class="card-header-title" style="color: var(--color-blue);">🎯 2027 Target (목표)</div>
                    <div class="card-data-row"><span>목표 매출액</span><b>{format_currency(target_rev_2027)} (+{target_rev_growth*100:.1f}%)</b></div>
                    <div class="card-data-row"><span>목표 물동량</span><b>{int(target_vol_2027):,} EA</b></div>
                    <div class="card-data-row"><span>목표 물류비</span><b>{format_currency(target_cost_2027)} (-{target_cost_reduction*100:.1f}%)</b></div>
                </div>
                <div class="card-data-row" style="border-top: 1px dashed var(--border-color); padding-top: 6px; margin-top: 6px;">
                    <span>목표 OTD</span><b>{target_otd:.1f}%</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with dt3:
        st.markdown(
            f"""
            <div class="custom-card" style="border: 2px solid var(--color-green);">
                <div>
                    <div class="card-header-title" style="color: var(--color-green);">🔮 2027 Forecast (시뮬레이션)</div>
                    <div class="card-data-row"><span>예상 매출액</span><b>{format_currency(forecast_rev_2027)} ({gap_rev:+.1f}%)</b></div>
                    <div class="card-data-row"><span>예상 물동량</span><b>{int(forecast_vol_2027):,} EA</b></div>
                    <div class="card-data-row"><span>예상 물류비</span><b>{format_currency(forecast_cost_2027)}</b></div>
                </div>
                <div class="card-data-row" style="border-top: 1px dashed var(--border-color); padding-top: 6px; margin-top: 6px;">
                    <span>예상 OTD</span><b>{forecast_otd_2027:.1f}%</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='custom-h3'>전사 월별 출고량 추이 및 2027년 시뮬레이션 연결</div>", unsafe_allow_html=True)

    monthly_hist = raw_df.groupby("year_month")["sales_quantity"].sum().reset_index()
    monthly_hist["구분"] = "Actual (실적)"

    months_2027 = [f"2027-{m:02d}" for m in range(1, 13)]
    weights = [0.08, 0.07, 0.09, 0.08, 0.08, 0.09, 0.08, 0.07, 0.10, 0.09, 0.09, 0.08]
    vals_2027 = [forecast_vol_2027 * w for w in weights]
    monthly_sim = pd.DataFrame({"year_month": months_2027, "sales_quantity": vals_2027, "구분": "Forecast (2027 예측)"})

    comb_trend = pd.concat([monthly_hist, monthly_sim])
    fig_twin = px.line(comb_trend, x="year_month", y="sales_quantity", color="구분", line_dash="구분")
    fig_twin.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=-45), height=340, margin=dict(l=15, r=15, t=15, b=15),
        font=dict(size=12, color="#1D1D1F")
    )
    st.plotly_chart(fig_twin, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# ==============================================================================
# [13. AI Executive Summary & Action Required]
# ==============================================================================
st.markdown(
    f"""
    <div class="exec-summary-box">
        <div style="font-weight: 800; font-size: 1.05rem; color: #1D1D1F; margin-bottom: 6px;">📝 AI Executive Summary & Action Required</div>
        <p style="margin: 0 0 8px 0; color: #3A3A3C; font-size: 0.9rem; line-height: 1.55;">
            • <b>운영 상태 진단:</b> {busan_comment} 품절 위험군 SKU는 총 <b>{critical_risk_count}건</b>으로 조기 안전재고 버퍼링이 요구됩니다.<br>
            • <b>2027 디지털 트윈 시뮬레이션:</b> 경영진 목표 매출(성장률 +{target_rev_growth*100:.1f}%) 대비 시뮬레이션 예상 매출은 <b>{format_currency(forecast_rev_2027)}</b>이며, {cost_comment}
        </p>
        <hr style="margin: 6px 0; border: none; border-top: 1px solid var(--border-color);">
        <div style="font-weight: 700; color: #1D1D1F; font-size: 0.92rem; margin-bottom: 4px;">🛠️ 경영진 우선 조치 권고 (Action Required):</div>
        <ul style="margin: 0; padding-left: 18px; color: #3A3A3C; font-size: 0.88rem; line-height: 1.5;">
            <li><b>물류센터 Capacity:</b> 성수기 물동량 집중에 대비한 거점 간 인터모달 분산 배치 검토</li>
            <li><b>공급망 리스크:</b> 변동계수(CV)가 0.35를 초과하는 공급사 대상 듀얼 소싱(Dual Sourcing) 계약 추진</li>
            <li><b>재고 정책:</b> Projected Stock 기준 마이너스(-) 예상 SKU 대상 긴급 발주 파이프라인 가동</li>
            <li><b>원가 최적화:</b> 운송비 비중 절감을 위한 주요 간선 노선 적재율 및 FTL(Full Truck Load) 운영 표준화</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)