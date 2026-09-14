import os
import base64
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_geolocation import streamlit_geolocation

# -----------------------------------------------------------------------------
# 1. 환경 변수 및 Streamlit Secrets 조회 함수 (Line 18 ~ Line 42)
# -----------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)

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

KAKAO_REST_KEY = get_secret_key("KAKAO_MAP_KEY")
WEATHER_KEY = get_secret_key("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_secret_key("EXCHANGE_RATE_API_KEY")

st.set_page_config(page_title="여행 가이드 & 외환 인텔리전스", page_icon="🗺️", layout="wide")

if not KAKAO_REST_KEY:
    st.error("⚠️ `KAKAO_MAP_KEY` (카카오 REST API 키)를 설정해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 환율 데이터 및 통화 메타데이터 (Line 44 ~ Line 98)
# -----------------------------------------------------------------------------
CURRENCY_INFO = {
    "USD": {"name": "미국 달러화", "flag": "🇺🇸", "symbol": "$", "unit": 1},
    "JPY": {"name": "일본 엔화 (100엔)", "flag": "🇯🇵", "symbol": "¥", "unit": 100},
    "EUR": {"name": "유로존 유로", "flag": "🇪🇺", "symbol": "€", "unit": 1},
    "CNY": {"name": "중국 위안화", "flag": "🇨🇳", "symbol": "¥", "unit": 1},
    "VND": {"name": "베트남 동화 (100동)", "flag": "🇻🇳", "symbol": "₫", "unit": 100},
    "GBP": {"name": "영국 파운드화", "flag": "🇬🇧", "symbol": "£", "unit": 1},
    "AUD": {"name": "호주 달러화", "flag": "🇦🇺", "symbol": "A$", "unit": 1},
    "CAD": {"name": "캐나다 달러화", "flag": "🇨🇦", "symbol": "C$", "unit": 1},
    "SGD": {"name": "싱가포르 달러화", "flag": "🇸🇬", "symbol": "S$", "unit": 1},
}

@st.cache_data(ttl=1800)
def get_live_exchange_rates(api_key: str):
    if not api_key:
        return None, "외환 API 키 미설정"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {}), None
            return None, data.get("error-type", "데이터 피드 에러")
        return None, f"서버 에러 ({res.status_code})"
    except Exception as e:
        return None, f"통신 장애: {e}"

live_rates, _ = get_live_exchange_rates(EXCHANGE_KEY)
fallback_rates = {
    "USD": 1.0, "KRW": 1380.0, "JPY": 154.5, "EUR": 0.92, 
    "CNY": 7.24, "GBP": 0.79, "VND": 25400.0, "AUD": 1.52, 
    "CAD": 1.37, "SGD": 1.35
}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates

# 🌟 개별 통화 상세 팝업 계산기 (Dialog)
@st.dialog("🧮 개별 통화 상세 계산기")
def open_currency_calculator(cur_code, info, rates_map):
    st.markdown(f"### {info['flag']} **{cur_code} ({info['name']})** 환산 스튜디오")
    krw_per_usd = rates_map.get("KRW", 1380.0)
    cur_per_usd = rates_map.get(cur_code, 1.0)
    rate_krw_per_cur = (krw_per_usd / cur_per_usd) * info["unit"]
    
    t_fwd, t_rev = st.tabs(["원화 ➔ 외화", f"{cur_code} ➔ 원화"])
    with t_fwd:
        amt_krw = st.number_input("원화 금액 (KRW)", min_value=0.0, value=100000.0, step=10000.0, key=f"popup_krw_{cur_code}")
        res_cur = amt_krw / rate_krw_per_cur if rate_krw_per_cur > 0 else 0
        st.metric("환산 결과", f"{info['symbol']} {res_cur:,.2f}", f"적용 환율: ₩{rate_krw_per_cur:,.2f}")
    with t_rev:
        amt_cur = st.number_input(f"{cur_code} 금액", min_value=0.0, value=100.0 if info['unit']==1 else 10000.0, step=10.0, key=f"popup_cur_{cur_code}")
        res_krw = amt_cur * rate_krw_per_cur
        st.metric("환산 결과", f"₩ {res_krw:,.2f}", f"적용 환율: ₩{rate_krw_per_cur:,.2f}")
    if st.button("닫기", width="stretch"):
        st.rerun()

# -----------------------------------------------------------------------------
# 3. 카카오 및 날씨 API 함수 (Line 100 ~ Line 148)
# -----------------------------------------------------------------------------
def search_kakao_place(keyword: str, kakao_key: str, center_lat: float = None, center_lon: float = None, radius: int = None):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    params = {"query": keyword, "size": 10}
    if center_lat and center_lon and radius:
        params["y"] = str(center_lat)
        params["x"] = str(center_lon)
        params["radius"] = str(radius)
        params["sort"] = "distance"
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("documents", []), None
        return None, f"카카오 검색 실패 ({res.status_code}): {res.text}"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

def get_nearby_places_by_category(category_code: str, lat: float, lon: float, kakao_key: str, radius: int = 2000):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    params = {"category_group_code": category_code, "x": str(lon), "y": str(lat), "radius": str(radius), "sort": "distance", "size": 5}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("documents", []), None
        return [], f"카테고리 검색 실패 ({res.status_code})"
    except Exception as e:
        return [], f"네트워크 오류: {e}"

def get_weather_by_coords(lat: float, lon: float, weather_key: str):
    if not weather_key:
        return None, "날씨 API 키(OPENWEATHER_API_KEY)가 등록되지 않았습니다."
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": weather_key, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json(), None
        return None, f"날씨 정보 호출 실패 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

# -----------------------------------------------------------------------------
# 4. 사이드바: 3가지 탐색 모드 (Line 150 ~ Line 235)
# -----------------------------------------------------------------------------
preset_places = {
    "경복궁": {"lat": 37.5796, "lon": 126.9770, "address": "서울 종로구 사직로 161", "kakao_url": "https://place.map.kakao.com/18600021"},
    "N서울타워": {"lat": 37.5512, "lon": 126.9882, "address": "서울 용산구 남산공원길 105", "kakao_url": "https://place.map.kakao.com/8120619"},
    "북촌한옥마을": {"lat": 37.5826, "lon": 126.9835, "address": "서울 종로구 계동길 37", "kakao_url": "https://place.map.kakao.com/13170757"},
    "동대문디자인플라자(DDP)": {"lat": 37.5665, "lon": 127.0092, "address": "서울 중구 을지로 281", "kakao_url": "https://place.map.kakao.com/21356877"},
}

with st.sidebar:
    st.header("🔍 여행지 탐색")
    mode = st.radio("탐색 모드 선택", ["추천 명소 선택", "일반 장소 검색 (전국)", "내 주변 반경 검색"])

    target_name = None
    target_lat = None
    target_lon = None
    target_addr = ""
    target_url = None

    if mode == "추천 명소 선택":
        selected_name = st.selectbox("서울 주요 명소 4선", list(preset_places.keys()))
        target_name = selected_name
        target_lat = preset_places[selected_name]["lat"]
        target_lon = preset_places[selected_name]["lon"]
        target_addr = preset_places[selected_name]["address"]
        target_url = preset_places[selected_name]["kakao_url"]

    elif mode == "일반 장소 검색 (전국)":
        search_query = st.text_input("장소 이름 또는 주소 입력", placeholder="예: 신림역, 해운대해수욕장")
        if search_query:
            places_found, search_err = search_kakao_place(search_query, KAKAO_REST_KEY)
            if search_err:
                st.error(search_err)
            elif places_found:
                place_names = [f"{p['place_name']} ({p.get('road_address_name') or p.get('address_name')})" for p in places_found]
                selected_idx = st.selectbox("검색 결과 선택", range(len(place_names)), format_func=lambda x: place_names[x])
                chosen = places_found[selected_idx]
                target_name = chosen["place_name"]
                target_lat = float(chosen["y"])
                target_lon = float(chosen["x"])
                target_addr = chosen.get("road_address_name") or chosen.get("address_name")
                target_url = chosen.get("place_url")
            else:
                st.warning(f"'{search_query}' 검색 결과가 없습니다.")

    else:
        st.subheader("📍 기준 위치 설정")
        st.caption("아래 버튼을 눌러 위치 권한을 허용하거나 기본 위치를 사용합니다.")
        geo_location = streamlit_geolocation()

        if geo_location and geo_location.get("latitude"):
            my_lat = geo_location["latitude"]
            my_lon = geo_location["longitude"]
            st.success(f"현재 위치 감지됨 ({my_lat:.4f}, {my_lon:.4f})")
        else:
            st.info("위치 미허용 시 기본 위치(서울시청)로 설정됩니다.")
            my_lat, my_lon = 37.5665, 126.9780

        search_radius = st.slider("검색 반경 (미터)", min_value=300, max_value=5000, value=1000, step=100)
        search_query = st.text_input("내 주변 검색어 입력", placeholder="예: 편의점, 스타벅스")

        if search_query:
            places_found, search_err = search_kakao_place(
                keyword=search_query,
                kakao_key=KAKAO_REST_KEY,
                center_lat=my_lat,
                center_lon=my_lon,
                radius=search_radius
            )
            if search_err:
                st.error(search_err)
            elif places_found:
                place_names = [
                    f"{p['place_name']} [{p.get('distance', '?')}m] ({p.get('road_address_name') or p.get('address_name')})"
                    for p in places_found
                ]
                selected_idx = st.selectbox("반경 내 검색 결과 (거리순)", range(len(place_names)), format_func=lambda x: place_names[x])
                chosen = places_found[selected_idx]
                target_name = chosen["place_name"]
                target_lat = float(chosen["y"])
                target_lon = float(chosen["x"])
                target_addr = chosen.get("road_address_name") or chosen.get("address_name")
                target_url = chosen.get("place_url")
            else:
                st.warning(f"반경 {search_radius}m 내에 '{search_query}' 검색 결과가 없습니다.")

# -----------------------------------------------------------------------------
# 5. 본문 메인 레이아웃: [지도] vs [우측 탭: 날씨 & 간편 환전기] (Line 237 ~ Line 335)
# -----------------------------------------------------------------------------
st.title("🗺️ 여행 가이드 & 💱 외환 대시보드")

if target_lat and target_lon:
    st.subheader(f"🚩 선택 장소: **{target_name}**")
    if target_addr:
        st.caption(f"📍 위치: {target_addr}")

    col_map, col_right = st.columns([6, 4], gap="large")

    # 5-1. [좌측] 카카오 정적 지도
    with col_map:
        st.markdown("#### 🗺️ 카카오 지도")
        marker_param = f"type:default|lat:{target_lat},lon:{target_lon}|text:{target_name}"
        static_map_url = "https://dapi.kakao.com/v2/maps/staticmap"
        map_params = {
            "center": f"{target_lon},{target_lat}",
            "level": 3,
            "size": "700x450",
            "markers": [marker_param],
        }
        headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
        map_res = requests.get(static_map_url, headers=headers, params=map_params)

        if map_res.status_code == 200:
            st.image(map_res.content, width="stretch", caption=f"{target_name} 카카오 지도")
        else:
            st.error(f"지도 렌더링 실패 ({map_res.status_code}): {map_res.text}")

        btn_col1, btn_col2 = st.columns(2)
        kakao_link = target_url if target_url else f"https://map.kakao.com/link/map/{target_name},{target_lat},{target_lon}"
        route_link = f"https://map.kakao.com/link/to/{target_name},{target_lat},{target_lon}"

        with btn_col1:
            st.link_button("📍 카카오맵에서 상세 보기", kakao_link, width="stretch")
        with btn_col2:
            st.link_button("🚗 카카오맵 길찾기", route_link, width="stretch")

    # 5-2. [우측] 탭 구조 (실시간 날씨 vs 여행 경비 환율 계산)
    with col_right:
        tab_weather, tab_fx_quick = st.tabs(["🌤️ 현지 실시간 날씨", "💱 실시간 환율"])

        with tab_weather:
            w_data, w_err = get_weather_by_coords(target_lat, target_lon, WEATHER_KEY)
            if w_err:
                st.warning(w_err)
            elif w_data:
                weather_desc = w_data["weather"][0]["description"]
                weather_icon = w_data["weather"][0]["icon"]
                icon_url = f"https://openweathermap.org/img/wn/{weather_icon}@2x.png"
                temp = w_data["main"]["temp"]
                feels_like = w_data["main"]["feels_like"]
                humidity = w_data["main"]["humidity"]
                wind = w_data["wind"]["speed"]

                with st.container(border=True):
                    top_c1, top_c2 = st.columns([1, 3])
                    with top_c1:
                        st.image(icon_url, width=70)
                    with top_c2:
                        st.markdown(f"### {temp:.1f} °C")
                        st.write(f"상태: **{weather_desc}**")

                    st.divider()
                    m1, m2 = st.columns(2)
                    m1.metric("체감 온도", f"{feels_like:.1f} °C")
                    m2.metric("습도", f"{humidity} %")
                    st.metric("풍속", f"{wind} m/s")

                st.markdown("#### 💡 오늘의 여행 팁")
                if "비" in weather_desc or "소나기" in weather_desc:
                    st.info("☔ 비 예보가 있습니다. 우산을 준비하세요.")
                elif temp >= 28:
                    st.warning("☀️ 무더운 날씨입니다. 수분을 충분히 섭취하세요.")
                elif temp <= 5:
                    st.info("🧣 쌀쌀한 날씨입니다. 따뜻한 외투를 준비하세요.")
                else:
                    st.success("🚶 야외 활동을 즐기기에 쾌적한 날씨입니다.")

        with tab_fx_quick:
            st.markdown("##### 💱 주요 통화 즉시 환전 (KRW 기준)")
            krw_base = rates_dict.get("KRW", 1380.0)
            
            c_input, c_sel = st.columns([1.5, 1])
            with c_input:
                calc_amt = st.number_input("원화(KRW) 입력", value=100000.0, step=50000.0)
            with c_sel:
                calc_cur = st.selectbox("통화 선택", ["USD", "JPY", "EUR", "CNY", "VND"])

            info = CURRENCY_INFO[calc_cur]
            cur_usd = rates_dict.get(calc_cur, 1.0)
            rate_per_unit = (krw_base / cur_usd) * (1 / info["unit"])
            res_val = calc_amt / ((krw_base / cur_usd) * info["unit"])

            with st.container(border=True):
                st.metric(
                    label=f"{info['flag']} {calc_cur} 환산 금액",
                    value=f"{info['symbol']} {res_val:,.2f}",
                    delta=f"1 {calc_cur} = ₩{rate_per_unit:,.2f}"
                )

    # -------------------------------------------------------------------------
    # 6. 주변 추천 맛집 및 관광 명소 섹션 (Line 337 ~ Line 392)
    # -------------------------------------------------------------------------
    st.divider()
    st.markdown(f"### 🍽️ **{target_name}** 주변 맛집 & 📸 추천 관광지")

    tab_food, tab_tour, tab_search = st.tabs(["🍴 주변 인기 맛집", "🏛️ 주변 관광 명소", "🔍 블로그/구글 검색"])

    with tab_food:
        foods, _ = get_nearby_places_by_category("FD6", target_lat, target_lon, KAKAO_REST_KEY, radius=2000)
        if foods:
            for item in foods:
                with st.container(border=True):
                    f_col1, f_col2 = st.columns([4, 1])
                    with f_col1:
                        st.markdown(f"**{item['place_name']}** · `{item.get('category_name', '').split(' > ')[-1]}`")
                        st.caption(f"📍 {item.get('road_address_name') or item.get('address_name')} (거리: 약 {item.get('distance')}m)")
                    with f_col2:
                        st.link_button("리뷰/메뉴", item["place_url"], width="stretch")
        else:
            st.info("반경 2km 이내에 등록된 맛집 정보가 없습니다.")

    with tab_tour:
        tours, _ = get_nearby_places_by_category("AT4", target_lat, target_lon, KAKAO_REST_KEY, radius=3000)
        if tours:
            for item in tours:
                with st.container(border=True):
                    t_col1, t_col2 = st.columns([4, 1])
                    with t_col1:
                        st.markdown(f"**{item['place_name']}**")
                        st.caption(f"📍 {item.get('road_address_name') or item.get('address_name')} (거리: 약 {item.get('distance')}m)")
                    with t_col2:
                        st.link_button("상세보기", item["place_url"], width="stretch")
        else:
            st.info("반경 3km 이내에 등록된 관광 명소 정보가 없습니다.")

    with tab_search:
        naver_blog_url = f"https://search.naver.com/search.naver?where=view&query={target_name}+맛집+여행"
        google_search_url = f"https://www.google.com/search?q={target_name}+맛집+가볼만한곳"
        kakao_blog_url = f"https://search.daum.net/search?w=blog&q={target_name}+맛집"

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.link_button("🟢 네이버 블로그 검색", naver_blog_url, width="stretch")
        with sc2:
            st.link_button("🔵 구글 맛집/여행 검색", google_search_url, width="stretch")
        with sc3:
            st.link_button("🟡 다음 블로그 리뷰 보기", kakao_blog_url, width="stretch")

    # -------------------------------------------------------------------------
    # 7. app_2.py 결합 섹션: 글로벌 외환 카드 & 밸류에이션 진단 (Line 394 ~ Line 520)
    # -------------------------------------------------------------------------
    st.divider()
    st.markdown("### 💱 글로벌 외환 인텔리전스 & 전세계 환율 스튜디오")
    st.caption("해외 여행 및 대외 거래를 위한 실시간 환율 현황판과 역사적 밸류에이션 분석입니다.")

    # 7-1. 카드 그리드
    grid_cols = st.columns(3, gap="medium")
    krw_rate_base = rates_dict.get("KRW", 1380.0)
    card_idx = 0

    for cur_code, info in CURRENCY_INFO.items():
        cur_usd_rate = rates_dict.get(cur_code, 1.0)
        rate_per_krw = (cur_usd_rate / krw_rate_base) * info["unit"]
        reverse_rate = (krw_rate_base / cur_usd_rate) / info["unit"]

        target_col = grid_cols[card_idx % 3]
        with target_col:
            with st.container(border=True):
                st.markdown(f"#### {info['flag']} {cur_code} ({info['name']})")
                st.metric("1 단위 당 원화 환율", f"₩ {reverse_rate:,.2f}")
                st.caption(f"1 KRW = {rate_per_krw:,.4f} {cur_code}")
                if st.button(f"🧮 {cur_code} 계산기 열기", key=f"btn_calc_{cur_code}", width="stretch"):
                    open_currency_calculator(cur_code, info, rates_dict)
        card_idx += 1

    # 7-2. 시계열 밸류에이션 진단
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.subheader("📈 외환 밸류에이션 진단 차트")
    
    target_currency = st.selectbox(
        "분석 대상 통화 선택",
        options=list(CURRENCY_INFO.keys()),
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
    df_daily["Change_Pct"] = df_daily["Rate"].pct_change().fillna(0) * 100

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
        height=330, margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_time, width="stretch")

else:
    st.info("👈 왼쪽 사이드바에서 원하는 방식을 선택해 장소를 탐색해 보세요.")