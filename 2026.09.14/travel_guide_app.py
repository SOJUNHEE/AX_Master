import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# -----------------------------------------------------------------------------
# 1. 환경 변수 및 Streamlit Secrets 조회
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

st.set_page_config(page_title="여행 가이드 & 스마트 여행 비서", page_icon="🗺️", layout="wide")

if not KAKAO_REST_KEY:
    st.error("⚠️ `KAKAO_MAP_KEY` (카카오 REST API 키)를 설정해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 환율 데이터 로드 (간편 계산기용)
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

# -----------------------------------------------------------------------------
# 3. 카카오 REST API 및 날씨 API 함수
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

def get_kakao_place_images(query: str, kakao_key: str, size: int = 3):
    """카카오 Daum 이미지 검색 REST API를 이용해 장소 실사진을 가져옵니다."""
    url = "https://dapi.kakao.com/v2/search/image"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    params = {"query": query, "size": size, "sort": "accuracy"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            return [doc["image_url"] for doc in docs if doc.get("image_url")]
        return []
    except Exception:
        return []

def get_nearby_places_by_category(category_code: str, lat: float, lon: float, kakao_key: str, radius: int = 2000):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    params = {
        "category_group_code": category_code,
        "x": str(lon),
        "y": str(lat),
        "radius": str(radius),
        "sort": "distance",
        "size": 5
    }
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
# 4. 사이드바: 3가지 장소 탐색 모드
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
# 5. 본문 메인 레이아웃
# -----------------------------------------------------------------------------
st.title("🗺️ 여행 가이드 & 스마트 여행 비서")

if target_lat and target_lon:
    st.subheader(f"🚩 **{target_name}**")
    if target_addr:
        st.caption(f"📍 위치: {target_addr}")

    # 🌟 신규 추가: 선택한 명소 실사진 갤러리 렌더링
    with st.spinner(f"'{target_name}' 관련 사진을 불러오는 중..."):
        place_images = get_kakao_place_images(target_name, KAKAO_REST_KEY, size=3)

    if place_images:
        img_cols = st.columns(len(place_images))
        for idx, img_url in enumerate(place_images):
            with img_cols[idx]:
                st.image(img_url, width="stretch", caption=f"{target_name} 풍경 {idx+1}")
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col_map, col_right = st.columns([6, 4], gap="large")

    # 5-1. [좌측] 카카오 정적 지도 및 줌 컨트롤러
    with col_map:
        st.markdown("#### 🗺️ 카카오 지도")

        if "map_zoom_level" not in st.session_state:
            st.session_state.map_zoom_level = 3

        zoom_col1, zoom_col2, zoom_col3 = st.columns([1, 1, 3])
        with zoom_col1:
            if st.button("➕ 확대", key="zoom_in_btn", width="stretch"):
                if st.session_state.map_zoom_level > 1:
                    st.session_state.map_zoom_level -= 1
                    st.rerun()
        with zoom_col2:
            if st.button("➖ 축소", key="zoom_out_btn", width="stretch"):
                if st.session_state.map_zoom_level < 14:
                    st.session_state.map_zoom_level += 1
                    st.rerun()
        with zoom_col3:
            selected_zoom = st.slider(
                "지도 줌 레벨",
                min_value=1,
                max_value=14,
                value=st.session_state.map_zoom_level,
                key="zoom_slider",
                label_visibility="collapsed"
            )
            st.session_state.map_zoom_level = selected_zoom

        marker_param = f"type:default|lat:{target_lat},lon:{target_lon}|text:{target_name}"
        static_map_url = "https://dapi.kakao.com/v2/maps/staticmap"[cite: 1]
        map_params = {
            "center": f"{target_lon},{target_lat}",[cite: 1]
            "level": st.session_state.map_zoom_level,
            "size": "700x450",
            "markers": [marker_param],
        }
        headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}[cite: 1]
        map_res = requests.get(static_map_url, headers=headers, params=map_params)[cite: 1]

        if map_res.status_code == 200:[cite: 1]
            st.image(
                map_res.content,
                width="stretch",
                caption=f"{target_name} 카카오 지도 (확대 레벨: {st.session_state.map_zoom_level})"
            )
        else:
            st.error(f"지도 렌더링 실패 ({map_res.status_code}): {map_res.text}")[cite: 1]

        btn_col1, btn_col2 = st.columns(2)
        kakao_link = target_url if target_url else f"https://map.kakao.com/link/map/{target_name},{target_lat},{target_lon}"
        route_link = f"https://map.kakao.com/link/to/{target_name},{target_lat},{target_lon}"

        with btn_col1:
            st.link_button("📍 카카오맵에서 상세 보기", kakao_link, width="stretch")
        with btn_col2:
            st.link_button("🚗 카카오맵 길찾기", route_link, width="stretch")

    # 5-2. [우측] 탭 구조 (실시간 날씨 & 맞춤 환율 계산기)
    with col_right:
        tab_weather, tab_fx_quick = st.tabs(["🌤️ 현지 실시간 날씨", "💱 맞춤 환율 계산기"])

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
            st.markdown("##### 💱 출발국 ⇄ 여행지 맞춤 환율 계산")
            curr_keys = list(CURRENCY_INFO.keys())
            all_currs = ["KRW"] + [k for k in curr_keys if k != "KRW"]

            col_src, col_dst = st.columns(2)
            with col_src:
                from_cur = st.selectbox("출발 국가 통화 (기준)", all_currs, index=0, key="quick_from_cur")
            with col_dst:
                to_cur = st.selectbox("여행지 통화 (대상)", all_currs, index=all_currs.index("JPY") if "JPY" in all_currs else 1, key="quick_to_cur")

            calc_amt = st.number_input(
                f"환전할 금액 ({from_cur})", 
                min_value=0.0, 
                value=0.0, 
                step=1000.0, 
                format="%.2f",
                key="quick_amt_input"
            )

            krw_base = rates_dict.get("KRW", 1380.0)
            from_rate_usd = 1.0 if from_cur == "USD" else (krw_base if from_cur == "KRW" else rates_dict.get(from_cur, 1.0))
            to_rate_usd = 1.0 if to_cur == "USD" else (krw_base if to_cur == "KRW" else rates_dict.get(to_cur, 1.0))

            exchange_rate = to_rate_usd / from_rate_usd if from_rate_usd > 0 else 0
            converted_result = calc_amt * exchange_rate

            dst_symbol = CURRENCY_INFO.get(to_cur, {}).get("symbol", "₩" if to_cur == "KRW" else "")
            
            with st.container(border=True):
                st.metric(
                    label=f"환전 수령 금액 ({to_cur})",
                    value=f"{dst_symbol} {converted_result:,.2f}",
                    delta=f"1 {from_cur} = {exchange_rate:,.4f} {to_cur}"
                )
                if calc_amt == 0:
                    st.caption("💡 금액을 입력하면 실시간으로 환전 금액이 계산됩니다.")

    # -------------------------------------------------------------------------
    # 6. 주변 추천 맛집 및 관광 명소 섹션
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
                    with f_col2:
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

else:
    st.info("👈 왼쪽 사이드바에서 원하는 방식을 선택해 장소를 탐색해 보세요.")