from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. 페이지 설정 (wide 레이아웃 및 일관된 여백 확보)
st.set_page_config(
    page_title="Executive SCM Control Tower & Digital Twin",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Apple + Bloomberg + McKinsey 통합 디자인 시스템 및 스페이싱/카드 높이 정렬 CSS 주입
st.markdown(
    """
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        html, body, [class*="css"] {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
            background-color: #F5F5F7;
            color: #1D1D1F;
        }

        /* 메인 컨테이너 좌우 여백 및 Spacing System 통일 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 100% !important;
        }

        section[data-testid="stSidebar"] {
            background-color: rgba(251, 251, 253, 0.98);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(210, 210, 215, 0.6);
        }

        /* 2단계: 상단 Apple Window Header 크기 및 패딩 축소 최적화 */
        .apple-window-bar {
            background: #FFFFFF;
            padding: 16px 22px;
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
            border: 1px solid #E5E5EA;
            margin-bottom: 24px;
        }

        .traffic-lights {
            display: flex;
            gap: 6px;
            margin-bottom: 8px;
        }
        .dot { width: 10px; height: 10px; border-radius: 50%; }
        .dot-red { background-color: #FF3B30; border: 1px solid #e0443e; }
        .dot-yellow { background-color: #FF9500; border: 1px solid #dea123; }
        .dot-green { background-color: #34C759; border: 1px solid #1aab29; }

        /* 타이포그래피 계층 구조 */
        h1 { font-size: 1.8rem !important; font-weight: 800 !important; color: #1D1D1F !important; letter-spacing: -0.5px; margin-bottom: 0px !important; }
        h2 { font-size: 1.35rem !important; font-weight: 700 !important; color: #1D1D1F !important; margin-top: 20px !important; margin-bottom: 12px !important; }
        h3 { font-size: 1.1rem !important; font-weight: 700 !important; color: #3A3A3C !important; margin-top: 10px !important; }
        p, span, label { color: #1D1D1F; }

        /* 5, 11단계: 모든 KPI 및 요약 카드의 높이/패딩 완벽 통일 (동일 Grid 시스템) */
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            padding: 18px 16px;
            border-radius: 14px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
            border: 1px solid #E5E5EA;
            text-align: center;
            height: 115px; /* 고정 높이 부여로 들쭉날쭉함 방지 */
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #86868B !important;
            margin-bottom: 2px !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.75rem !important;
            font-weight: 800 !important;
            color: #1D1D1F !important;
            letter-spacing: -1px;
        }

        /* 3단계: AI Insight & Alert Center 높이 최적화 */
        .ai-alert-box {
            background: #FFFFFF;
            padding: 16px 20px;
            border-radius: 14px;
            border-left: 6px solid #FF3B30;
            border: 1px solid #E5E5EA;
            box-shadow: 0 4px 15px rgba(255, 59, 48, 0.06);
            margin-bottom: 24px;
        }
        .ai-alert-box ul {
            margin: 0 !important;
            padding-left: 18px !important;
        }
        .ai-alert-box li {
            line-height: 1.5 !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            margin-bottom: 4px;
        }

        /* 커스텀 카드 컨테이너 (Warehouse, Digital Twin용 동일 규격) */
        .custom-card {
            background: #FFFFFF;
            padding: 20px;
            border-radius: 14px;
            border: 1px solid #E5E5EA;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
            height: 220px; /* 행 내부 카드 높이 통일 */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .exec-summary-box {
            background: #FFFFFF;
            padding: 22px;
            border-radius: 14px;
            border: 1px solid #E5E5EA;
            box-shadow: 0 2px 12px rgba(0,0,0,0.02);
            margin-top: 24px;
        }

        /* 9단계: 데이터 테이블 높이 및 가독성 최적화 */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #E5E5EA;
        }

        /* 상태 배지 */
        .badge-green { background-color: #34C759; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
        .badge-yellow { background-color: #FF9500; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
        .badge-red { background-color: #FF3B30; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    </style>
""",
    unsafe_allow_html=True,
)

# 2단계: 상단 Apple Window Header 구조
st.markdown(
    """
    <div class="apple-window-bar">
        <div class="traffic-lights">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
        </div>
        <h1>🏢 SCM Executive Control Tower & Digital Twin</h1>
        <p style="margin: 4px 0 0 0; color: #86868B; font-size: 0.95rem;">
            제조·유통·3PL 기업을 위한 실시간 공급망 통합 관제 및 2027 Digital Twin 의사결정 플랫폼
        </p>
    </div>
""",
    unsafe_allow_html=True,
)


# 4. 5개년치 시뮬레이션 데이터 생성 함수 (로직 변경 없음)
@st.cache_data
def generate_control_tower_data():
  np.random.seed(42)
  n_rows = 7500

  suppliers = [
      "Supplier_A",
      "Supplier_B",
      "Supplier_C",
      "Supplier_D",
      "Overseas_Supplier",
  ]
  warehouses = ["ICN_DC", "BUSAN_DC", "DAEJEON_DC", "GWANGJU_DC"]
  channels = ["B2C", "DC", "B2B"]
  products = [f"SKU_Item_{i:02d}" for i in range(1, 21)]

  start_date = datetime(2022, 1, 1)
  end_date = datetime(2026, 8, 31)
  total_days = (end_date - start_date).days

  random_days = np.random.randint(0, total_days, size=n_rows)
  date_range = [start_date + timedelta(days=int(d)) for d in random_days]

  data_list = []
  for i in range(n_rows):
    dt = date_range[i]
    year, month = dt.year, dt.month
    ch = np.random.choice(channels, p=[0.55, 0.30, 0.15])
    wh = np.random.choice(warehouses, p=[0.4, 0.3, 0.2, 0.1])
    sup = np.random.choice(suppliers)
    sku = np.random.choice(products)

    is_year_end = month in [11, 12]
    is_black_friday = month == 11
    is_chuseok = month == 9
    is_b2b_proj = np.random.rand() < 0.15
    is_disruption = np.random.rand() < 0.08

    multiplier = 1.0
    spike_label = "Normal"
    if is_black_friday:
      multiplier = 4.0
      spike_label = "Black Friday (+320%)"
    elif is_year_end:
      multiplier = 3.5
      spike_label = "Year-End Peak"
    elif is_chuseok:
      multiplier = 2.0
      spike_label = "Chuseok Special (+180%)"
    elif month in [1, 2]:
      multiplier = 2.0
      spike_label = "Lunar New Year"
    if ch == "B2B" and is_b2b_proj:
      multiplier *= 2.5
      spike_label = "B2B Large Project (+250%)"

    if ch == "B2C":
      base_q = np.random.randint(1, 6)
      sales_q = int(base_q * multiplier)
      req_q = sales_q + np.random.choice([0, 1], p=[0.8, 0.2])
    elif ch == "DC":
      base_q = np.random.randint(30, 120)
      sales_q = int(base_q * multiplier)
      req_q = sales_q + np.random.randint(0, 10)
    else:
      base_q = np.random.randint(200, 600)
      sales_q = int(base_q * (multiplier * 1.5 if is_b2b_proj else 1.0))
      req_q = sales_q + np.random.randint(10, 50)

    forecast_q = int(sales_q * np.random.uniform(0.85, 1.15))
    unit_price = np.random.randint(20000, 120000)
    revenue = sales_q * unit_price

    dock_cnt = (
        5
        if wh == "ICN_DC"
        else (8 if wh == "BUSAN_DC" else (6 if wh == "DAEJEON_DC" else 3))
    )
    worker_cnt = (
        15
        if wh == "ICN_DC"
        else (25 if wh == "BUSAN_DC" else (20 if wh == "DAEJEON_DC" else 10))
    )
    daily_cap = (
        12000
        if wh == "ICN_DC"
        else (18000 if wh == "BUSAN_DC" else (15000 if wh == "DAEJEON_DC" else 8000))
    )

    util_rate = min(round((sales_q / daily_cap) * 100, 2), 108.0)

    picking_t = np.random.randint(10, 45)
    packing_t = np.random.randint(5, 25)
    inspection_t = np.random.randint(5, 15)

    transport_c = sales_q * np.random.randint(1500, 3500)
    handling_c = sales_q * np.random.randint(500, 1200)
    labor_c = sales_q * np.random.randint(800, 2000)
    storage_c = np.random.randint(500000, 2000000)
    packaging_c = sales_q * np.random.randint(150, 400)
    total_logistics_c = (
        transport_c + handling_c + labor_c + storage_c + packaging_c
    )
    cost_per_unit = (
        round(total_logistics_c / sales_q, 2) if sales_q > 0 else 4010
    )

    inbound_fee = sales_q * np.random.randint(200, 500)
    outbound_fee = sales_q * np.random.randint(300, 700)
    storage_fee = np.random.randint(200000, 1000000)
    packaging_fee = sales_q * np.random.randint(150, 400)
    extra_fee = sales_q * np.random.randint(100, 300)
    total_settlement = (
        inbound_fee + outbound_fee + storage_fee + packaging_fee + extra_fee
    )

    stock_q = np.random.randint(10, 800)
    lead_time = (
        np.random.randint(3, 8)
        if not is_disruption
        else np.random.randint(15, 40)
    )

    data_list.append({
        "order_date": dt,
        "year": dt.year,
        "month": dt.month,
        "year_month": dt.strftime("%Y-%m"),
        "date_str": dt.strftime("%Y-%m-%d"),
        "supplier": sup,
        "purchase_order": f"PO{dt.year}{i:05d}",
        "forecast_quantity": forecast_q,
        "order_quantity": req_q,
        "sales_quantity": sales_q,
        "warehouse": wh,
        "dock_count": dock_cnt,
        "worker_count": worker_cnt,
        "daily_capacity": daily_cap,
        "utilization_rate": util_rate,
        "picking_time": picking_t,
        "packing_time": packing_t,
        "inspection_time": inspection_t,
        "transport_cost": transport_c,
        "handling_cost": handling_c,
        "labor_cost": labor_c,
        "storage_cost": storage_c,
        "packaging_cost": packaging_c,
        "total_logistics_cost": total_logistics_c,
        "cost_per_unit": cost_per_unit,
        "inbound_fee": inbound_fee,
        "outbound_fee": outbound_fee,
        "storage_fee": storage_fee,
        "packaging_fee": packaging_fee,
        "extra_fee": extra_fee,
        "total_settlement_cost": total_settlement,
        "stock_quantity": stock_q,
        "lead_time_days": lead_time,
        "channel": ch,
        "product_name": sku,
        "revenue": revenue,
        "spike_event": spike_label,
    })

  df = pd.DataFrame(data_list)
  df["is_otd"] = np.where(
      df["supplier"].str.contains("Overseas"),
      df["lead_time_days"] <= 10,
      df["lead_time_days"] <= 5,
  )
  df["safety_stock_line"] = 50
  df["is_stockout_risk"] = df["stock_quantity"] < df["safety_stock_line"]
  df["daily_avg_sales"] = np.random.randint(20, 150, size=len(df))
  df["days_on_hand"] = (
      df["stock_quantity"] / df["daily_avg_sales"]
  ).round(1)
  return df


df = generate_control_tower_data()

# 14단계: 사이드바 그룹화 및 스페이싱 최적화
st.sidebar.header("🎛️ Control Tower 관제 메뉴")
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
    "10. 🎯 Digital Twin & What-if Planning (2027)",
])

st.sidebar.markdown("---")
st.sidebar.header("🎯 경영진 KPI 목표 설정")
target_rev_growth = (
    st.sidebar.number_input("매출 성장률 목표 (%)", value=15.0, step=1.0) / 100.0
)
target_vol_growth = (
    st.sidebar.number_input("물동량 증가율 목표 (%)", value=10.0, step=1.0) / 100.0
)
target_cost_reduction = (
    st.sidebar.number_input("물류비 절감률 목표 (%)", value=8.0, step=1.0) / 100.0
)
target_otd = st.sidebar.number_input("OTD 목표 (%)", value=98.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("⚡ What-if 시뮬레이션 설정")
sim_rev_growth = (
    st.sidebar.slider("What-if 매출 성장률 조정 (%)", 0.0, 30.0, 15.0, 0.5) / 100.0
)
sim_cost_reduction = (
    st.sidebar.slider("What-if 물류비 절감률 조정 (%)", 0.0, 20.0, 8.0, 0.5)
    / 100.0
)
sim_otd_boost = (
    st.sidebar.slider("What-if OTD 개선 계수 조정 (%)", -5.0, 5.0, 1.5, 0.5)
    / 100.0
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 데이터 필터")
date_filter_option = st.sidebar.selectbox(
    "기간 선택",
    [
        "전체 기간 (5개년)",
        "오늘",
        "어제",
        "최근 7일",
        "최근 30일",
        "최근 90일",
        "사용자 지정",
    ],
)

max_date = df["order_date"].max()
if date_filter_option == "오늘":
  filtered_df = df[df["order_date"] == max_date]
elif date_filter_option == "어제":
  filtered_df = df[df["order_date"] == max_date - timedelta(days=1)]
elif date_filter_option == "최근 7일":
  filtered_df = df[df["order_date"] >= max_date - timedelta(days=7)]
elif date_filter_option == "최근 30일":
  filtered_df = df[df["order_date"] >= max_date - timedelta(days=30)]
elif date_filter_option == "최근 90일":
  filtered_df = df[df["order_date"] >= max_date - timedelta(days=90)]
elif date_filter_option == "사용자 지정":
  start_d, end_d = st.sidebar.date_input(
      "기간 지정", [df["order_date"].min(), max_date]
  )
  filtered_df = df[
      (df["order_date"] >= pd.to_datetime(start_d))
      & (df["order_date"] <= pd.to_datetime(end_d))
  ]
else:
  filtered_df = df.copy()

selected_channels = st.sidebar.multiselect(
    "조회 채널", options=["B2C", "DC", "B2B"], default=["B2C", "DC", "B2B"]
)
selected_wh = st.sidebar.multiselect(
    "물류센터(DC)", options=df["warehouse"].unique(), default=df["warehouse"].unique()
)

filtered_df = filtered_df[
    filtered_df["channel"].isin(selected_channels)
    & filtered_df["warehouse"].isin(selected_wh)
]

if filtered_df.empty:
  st.warning("선택된 조건에 부합하는 데이터가 없습니다.")
  st.stop()

# 2026년 실적 데이터 연동 및 What-if 계산
df_2026 = df[df["year"] == 2026]
base_rev_2026 = df_2026["revenue"].sum()
base_vol_2026 = df_2026["sales_quantity"].sum()
base_cost_2026 = df_2026["total_logistics_cost"].sum()
base_otd_2026 = (df_2026["is_otd"].sum() / len(df_2026)) * 100

forecast_rev_2027 = base_rev_2026 * (1 + sim_rev_growth)
forecast_vol_2027 = base_vol_2026 * (1 + target_vol_growth)
forecast_cost_2027 = base_cost_2026 * (1 + target_vol_growth) * (1 - sim_cost_reduction)
forecast_otd_2027 = min(100.0, base_otd_2026 + (sim_otd_boost * 100))

target_rev_2027 = base_rev_2026 * (1 + target_rev_growth)
target_cost_2027 = base_cost_2026 * (1 + target_vol_growth) * (1 - target_cost_reduction)

# KPI 계산 체계
real_otd = (
    (filtered_df["is_otd"].sum() / len(filtered_df)) * 100
    if len(filtered_df) > 0
    else 0
)
real_fill_rate = 98.2
real_turnover = round(
    filtered_df["sales_quantity"].sum()
    / max(1, filtered_df["stock_quantity"].sum())
    * 4.2,
    1,
)
real_health_score = int(
    min(
        100,
        max(
            60,
            80
            + (real_otd * 0.1)
            - (filtered_df["is_stockout_risk"].sum() * 0.5),
        ),
    )
)


# ==========================================
# 3단계: AI Insight & Alert Center (최상단 고정 관제 경보)
# ==========================================
busan_avg_util = (
    filtered_df[filtered_df["warehouse"] == "BUSAN_DC"]["utilization_rate"].mean()
)
busan_status_color = "#FF3B30" if busan_avg_util > 90 else "#34C759"

st.markdown(
    f"""
    <div class="ai-alert-box">
        <h3 style="margin: 0 0 8px 0; color: #FF3B30;">🚨 AI Insight & Alert Center (실시간 관제 경보)</h3>
        <ul>
            <li><span style="color: {busan_status_color};">[위험]</span> BUSAN_DC 센터 가동률 과부하 발생 <span class="badge-red">{busan_avg_util:.1f}%</span> (추가 인력 및 도크 분산 필수)</li>
            <li><span style="color: #FF3B30;">[위험]</span> SKU 품절 임박 <span class="badge-red">{filtered_df['is_stockout_risk'].sum()}개 SKU 위험</span> (긴급 선행 발주 요망)</li>
            <li><span style="color: #FF9500;">[주의]</span> Supplier_C 평균 리드타임 증가 추세 <span class="badge-yellow">납기 지연</span></li>
            <li><span style="color: #FF9500;">[주의]</span> 2027 물류비 절감 시뮬레이션 결과 <span class="badge-yellow">{sim_cost_reduction * 100:.1f}%</span> (목표치 {target_cost_reduction * 100:.1f}% 소폭 미달)</li>
            <li><span style="color: #34C759;">[정상]</span> 전사 정시배송률(OTD) <span class="badge-green">{real_otd:.1f}% 안정적 유지 중</span></li>
        </ul>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4단계: Today's Operation Summary (6개 KPI Grid 통일)
# ==========================================
st.subheader("📋 Today's Operation Summary (오늘의 운영 현황)")
today_df = df[df["order_date"] == max_date]
t_inbound = today_df["sales_quantity"].sum() + 1500
t_outbound = today_df["sales_quantity"].sum()
t_order = today_df["order_quantity"].sum()
t_cost = today_df["total_logistics_cost"].sum()
t_stock = today_df["stock_quantity"].sum()
t_risk_sku = today_df["is_stockout_risk"].sum()

t1, t2, t3, t4, t5, t6 = st.columns(6)
with t1:
  st.metric(label="오늘 입고량", value=f"{t_inbound:,} EA")
with t2:
  st.metric(label="오늘 출고량", value=f"{t_outbound:,} EA")
with t3:
  st.metric(label="오늘 주문량", value=f"{t_order:,} EA")
with t4:
  st.metric(label="오늘 물류비", value=f"₩{t_cost:,.0f}")
with t5:
  st.metric(label="현재 총 재고", value=f"{t_stock:,} EA")
with t6:
  st.metric(label="품절 위험 SKU", value=f"{t_risk_sku} 개", delta="🔴 위험")

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


# ==========================================
# 관제 메뉴별 화면 렌더링
# ==========================================
if selected_menu == "1. Executive Dashboard":
  st.subheader("📊 Executive Dashboard (경영진용 핵심 KPI 관제)")
  st.markdown("기업 공급망 상태를 한 화면에서 파악하고 전략적 의사결정을 수행합니다.")

  stockout_cnt = filtered_df["is_stockout_risk"].sum()
  tot_log_cost = filtered_df["total_logistics_cost"].sum()

  # 5단계: Executive KPI 카드 6개 동일 높이/폭 Grid 통일
  e1, e2, e3, e4, e5, e6 = st.columns(6)
  with e1:
    st.metric(
        label="SCM Health Score",
        value=f"{real_health_score}점",
        delta="▲ 4.2%",
        delta_color="normal",
    )
  with e2:
    st.metric(
        label="Fill Rate",
        value=f"{real_fill_rate}%",
        delta="목표 달성",
        delta_color="normal",
    )
  with e3:
    st.metric(label="OTD (정시배송률)", value=f"{real_otd:.1f}%")
  with e4:
    st.metric(label="Inventory Turnover", value=f"{real_turnover} 회")
  with e5:
    st.metric(
        label="Stockout Risk", value=f"{stockout_cnt} SKU", delta="🔴 위험"
    )
  with e6:
    st.metric(label="Total Logistics Cost", value=f"₩{tot_log_cost:,.0f}")

  st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

  # 6단계: 2열 차트 영역 높이 통일 (height=400px 동일 지정)
  ec1, ec2 = st.columns(2)
  with ec1:
    st.markdown("#### 채널별 매출 점유율 비교")
    ch_grp = (
        filtered_df.groupby("channel")[["sales_quantity", "revenue"]]
        .sum()
        .reset_index()
    )
    fig_ch = px.bar(
        ch_grp,
        x="channel",
        y="revenue",
        color="channel",
        title="채널별 매출 점유율",
        text_auto=".2s",
    )
    fig_ch.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=13, color="#1D1D1F"),
    )
    st.plotly_chart(fig_ch, use_container_width=True)

  with ec2:
    st.markdown("#### 월별 물동량 추이 및 Spike 구간")
    trend_exec = (
        filtered_df.groupby("year_month")["sales_quantity"].sum().reset_index()
    )
    fig_ex_trend = px.line(
        trend_exec,
        x="year_month",
        y="sales_quantity",
        title="전사 월별 출고량 추이",
    )
    fig_ex_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"tickangle": -45},
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=13, color="#1D1D1F"),
    )
    st.plotly_chart(fig_ex_trend, use_container_width=True)


elif selected_menu == "2. Daily Operation Dashboard":
  st.subheader("📅 Daily Operation Dashboard (일자별 운영 현황)")
  daily_agg = (
      filtered_df.groupby("date_str")
      .agg({
          "order_quantity": "sum",
          "sales_quantity": "sum",
          "total_logistics_cost": "sum",
          "stock_quantity": "sum",
          "utilization_rate": "mean",
      })
      .reset_index()
      .sort_values(by="date_str", ascending=False)
  )
  st.dataframe(daily_agg, use_container_width=True, height=450)


elif selected_menu == "3. Warehouse Dashboard":
  st.subheader("🏭 Warehouse Dashboard (물류센터 관제 센터)")

  wh_summary = (
      filtered_df.groupby("warehouse")
      .agg({
          "sales_quantity": "sum",
          "utilization_rate": "mean",
          "total_logistics_cost": "sum",
          "is_otd": lambda x: f"{x.mean()*100:.1f}%",
      })
      .reset_index()
  )

  # 7단계: Warehouse 카드 4개 동일 높이 카드 컨테이너 적용
  dc_cols = st.columns(4)
  for idx, row in wh_summary.iterrows():
    wh_name = row["warehouse"]
    util = row["utilization_rate"]
    ship_q = f"{row['sales_quantity']:,} EA"
    cost = f"₩{row['total_logistics_cost']/100000000:.1f}억"
    otd = row["is_otd"]

    status = "과부하" if util > 90 else ("주의" if util > 80 else "정상")
    border_color = (
        "#FF3B30"
        if status == "과부하"
        else ("#FF9500" if status == "주의" else "#34C759")
    )
    badge_html = (
        '<span class="badge-red">과부하 🔴</span>'
        if status == "과부하"
        else (
            '<span class="badge-yellow">주의 🟡</span>'
            if status == "주의"
            else '<span class="badge-green">정상 🟢</span>'
        )
    )

    with dc_cols[idx % 4]:
      st.markdown(
          f"""
            <div class="custom-card" style="border: 2px solid {border_color};">
                <h3 style="margin: 0 0 4px 0;">{wh_name}</h3>
                <p style="margin: 2px 0; font-size: 0.95rem;">출고량: <b>{ship_q}</b></p>
                <p style="margin: 2px 0; font-size: 0.95rem;">가동률: <b>{util:.1f}%</b></p>
                <p style="margin: 2px 0; font-size: 0.95rem;">상태: {badge_html}</p>
                <p style="margin: 2px 0; font-size: 0.95rem;">물류비: {cost}</p>
                <p style="margin: 2px 0; font-size: 0.95rem;">OTD: {otd}</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

  st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
  st.dataframe(wh_summary, use_container_width=True, height=300)


elif selected_menu == "4. Logistics Cost Dashboard":
  st.subheader("💰 Logistics Cost Dashboard (물류비 분석)")
  tot_c = filtered_df["total_logistics_cost"].sum()
  avg_cpu = filtered_df["cost_per_unit"].mean()

  # 8단계: Logistics Cost KPI 카드 디자인 시스템 통일
  lc1, lc2 = st.columns(2)
  with lc1:
    st.metric(label="총 물류비", value=f"₩{tot_c:,.0f}")
  with lc2:
    st.metric(label="단위당 물류비", value=f"₩{avg_cpu:,.1f}")

  st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
  cost_df = pd.DataFrame({
      "Cost_Type": ["운송비", "인건비", "보관비", "하역비", "포장비"],
      "Amount": [45, 25, 18, 7, 5],
  })
  fig_lc_pie = px.pie(
      cost_df, names="Cost_Type", values="Amount", title="물류비 세부 비중 (%)", hole=0.4
  )
  fig_lc_pie.update_layout(
      paper_bgcolor="rgba(0,0,0,0)", font=dict(size=13), height=380
  )
  st.plotly_chart(fig_lc_pie, use_container_width=True)


elif selected_menu == "5. Inventory Dashboard":
  st.subheader("📦 Inventory Dashboard (재고 최적화 및 품절 예방)")
  risk_sku = filtered_df[filtered_df["is_stockout_risk"]][
      ["warehouse", "product_name", "stock_quantity", "days_on_hand"]
  ].drop_duplicates()
  st.dataframe(risk_sku, use_container_width=True, height=450)


elif selected_menu == "6. Demand Forecast Dashboard":
  st.subheader("📈 Demand Forecast Dashboard (수요 예측 정확도 분석)")
  fc_df = (
      filtered_df.groupby("year_month")[["forecast_quantity", "sales_quantity"]]
      .sum()
      .reset_index()
  )
  st.dataframe(fc_df, use_container_width=True, height=450)


elif selected_menu == "7. ABC Analysis":
  st.subheader("📊 ABC Analysis (매출 기여도 기반 SKU 자동 분류)")
  sku_rev = filtered_df.groupby("product_name")["revenue"].sum().reset_index()
  sku_rev = sku_rev.sort_values(by="revenue", ascending=False)
  sku_rev["cum_pct"] = (
      sku_rev["revenue"].cumsum() / sku_rev["revenue"].sum()
  ) * 100


  def assign_abc(pct):
    if pct <= 80:
      return "A 등급 (상위 80% 핵심)"
    elif pct <= 95:
      return "B 등급 (중간 15% 중요)"
    else:
      return "C 등급 (하위 5% 일반)"


  sku_rev["abc_class"] = sku_rev["cum_pct"].apply(assign_abc)
  st.dataframe(sku_rev, use_container_width=True, height=450)


elif selected_menu == "8. ABC-XYZ Matrix":
  st.subheader("🔲 ABC-XYZ Matrix (재고 정책 최적화)")
  matrix_table = pd.DataFrame({
      "Matrix Zone": ["AX Zone", "AZ Zone", "CZ Zone"],
      "Description": [
          "핵심 관리 품목 (최우선 발주)",
          "재고 위험 품목 (집중 모니터링)",
          "단종 검토 품목",
      ],
      "Priority": ["최우선", "위험", "검토"],
  })
  st.dataframe(matrix_table, use_container_width=True, height=300)


elif selected_menu == "9. Supplier Dashboard":
  st.subheader("🌐 Supplier Dashboard (공급사 성과 및 리스크 평가)")
  sup_summary = (
      filtered_df.groupby("supplier")
      .agg({
          "lead_time_days": "mean",
          "is_otd": lambda x: f"{x.mean()*100:.1f}%",
      })
      .reset_index()
  )
  st.dataframe(sup_summary, use_container_width=True, height=400)


elif selected_menu == "10. 🎯 Digital Twin & What-if Planning (2027)":
  st.subheader(
      "🎯 Executive Digital Twin : Actual vs Target vs Forecast (2027)"
  )
  st.markdown(
      "경영진 사업계획 목표(Target)와 실시간 What-if 시뮬레이션 예측값(Forecast)을 전년 실적(Actual 2026)과 동일 높이 카드 격차로 비교합니다."
  )

  # 10단계: Digital Twin 3열 카드 동일 높이(custom-card) 적용
  dt1, dt2, dt3 = st.columns(3)

  with dt1:
    st.markdown(
        f"""
        <div class="custom-card" style="height: 240px;">
            <h3 style="margin: 0 0 10px 0; color: #1D1D1F;">📌 2026 Actual (실적)</h3>
            <p style="margin: 4px 0;">매출액: <b>₩{base_rev_2026:,.0f}</b></p>
            <p style="margin: 4px 0;">물동량: <b>{base_vol_2026:,} EA</b></p>
            <p style="margin: 4px 0;">물류비: <b>₩{base_cost_2026:,.0f}</b></p>
            <p style="margin: 4px 0;">정시배송률(OTD): <b>{base_otd_2026:.1f}%</b></p>
        </div>
    """,
        unsafe_allow_html=True,
    )

  with dt2:
    st.markdown(
        f"""
        <div class="custom-card" style="height: 240px;">
            <h3 style="margin: 0 0 10px 0; color: #0066CC;">🎯 2027 Target (목표)</h3>
            <p style="margin: 4px 0;">매출액 목표: <b>₩{target_rev_2027:,.0f} (+{target_rev_growth*100:.1f}%)</b></p>
            <p style="margin: 4px 0;">물동량 목표: <b>{int(base_vol_2026 * (1 + target_vol_growth)):,} EA</b></p>
            <p style="margin: 4px 0;">물류비 목표: <b>₩{target_cost_2027:,.0f}</b></p>
            <p style="margin: 4px 0;">OTD 목표: <b>{target_otd:.1f}%</b></p>
        </div>
    """,
        unsafe_allow_html=True,
    )

  with dt3:
    rev_diff = (
        (forecast_rev_2027 - target_rev_2027) / target_rev_2027
    ) * 100
    st.markdown(
        f"""
        <div class="custom-card" style="height: 240px;">
            <h3 style="margin: 0 0 10px 0; color: #34C759;">🔮 2027 Forecast (예측)</h3>
            <p style="margin: 4px 0;">예상 매출액: <b>₩{forecast_rev_2027:,.0f} ({rev_diff:+.1f}%)</b></p>
            <p style="margin: 4px 0;">예상 물동량: <b>{int(forecast_vol_2027):,} EA</b></p>
            <p style="margin: 4px 0;">예상 물류비: <b>₩{forecast_cost_2027:,.0f}</b></p>
            <p style="margin: 4px 0;">예상 OTD: <b>{forecast_otd_2027:.1f}%</b></p>
        </div>
    """,
        unsafe_allow_html=True,
    )

  st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
  st.markdown("### 📈 전사 월별 물동량 실적 및 2027 Digital Twin 예측 비교")

  monthly_actual = (
      df.groupby("year_month")["sales_quantity"].sum().reset_index()
  )
  monthly_actual["Type"] = "Actual (실적)"

  months_2027 = [f"2027-{m:02d}" for m in range(1, 13)]
  monthly_base_pattern = [
      0.08,
      0.07,
      0.09,
      0.08,
      0.08,
      0.09,
      0.08,
      0.07,
      0.10,
      0.09,
      0.09,
      0.08,
  ]
  forecast_vals = [
      forecast_vol_2027 * p * np.random.uniform(0.95, 1.05)
      for p in monthly_base_pattern
  ]

  monthly_forecast = pd.DataFrame({
      "year_month": months_2027,
      "sales_quantity": forecast_vals,
      "Type": "Forecast (2027 예측)",
  })

  combined_trend = pd.concat([monthly_actual, monthly_forecast])
  fig_twin = px.line(
      combined_trend,
      x="year_month",
      y="sales_quantity",
      color="Type",
      line_dash="Type",
      title="전사 월별 물동량 실적 및 2027 Digital Twin 예측",
  )
  fig_twin.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      xaxis={"tickangle": -45},
      font=dict(size=13, color="#1D1D1F"),
      height=400,
  )
  st.plotly_chart(fig_twin, use_container_width=True)


# ==========================================
# 16단계 원칙 준수: 하단 AI Executive Summary 경영진 브리핑
# ==========================================
sim_rev_val = forecast_rev_2027 / 100000000
achieve_cost_reduction = sim_cost_reduction * 100
target_cost_red_val = target_cost_reduction * 100

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="exec-summary-box">
        <h3 style="margin: 0 0 10px 0; color: #1D1D1F;">📝 AI Executive Summary (경영진용 종합 브리핑)</h3>
        <p style="margin: 0; color: #3A3A3C; font-size: 1.0rem; line-height: 1.7;">
            • <b>매출 및 물동량 전망:</b> 경영진 목표 매출 성장률({target_rev_growth*100:.1f}%)과 What-if 시뮬레이션 결과, 2027년 예상 매출액은 약 <b>{sim_rev_val:.1f}억원</b>으로 추정되며, 월평균 출고량 확대에 따른 선행 인프라 확충이 필요합니다.<br>
            • <b>물류센터 병목 관제:</b> BUSAN_DC 센터의 가동률이 95%를 초과({busan_avg_util:.1f}%)하여 과부하 상태이므로 추가 야간조 인력 투입 및 도크 분산 운영 검토가 시급합니다.<br>
            • <b>물류비 절감 달성도:</b> 현재 What-if 시뮬레이션 기준 물류비 절감률은 <b>{achieve_cost_reduction:.1f}%</b>로, 경영진 목표치({target_cost_red_val:.1f}%)에 소폭 미달하므로 운송비 효율화 대책이 필요합니다.<br>
            • <b>재고 및 공급망 리스크:</b> SKU 위험 품목은 현재 {filtered_df['is_stockout_risk'].sum()}개로 집계되며, Supplier_C의 리드타임 증가로 공급망 리스크가 확대되고 있습니다.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)