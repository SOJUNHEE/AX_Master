import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# -----------------------------------------------------------------------------
# 1. 최상위 루트 .env 로드
# -----------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)

KAKAO_REST_KEY = os.getenv("KAKAO_MAP_KEY")
WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="여행 가이드 & 실시간 날씨", page_icon="🗺️", layout="wide")
st.title("🗺️ 여행 가이드: 카카오맵 & 실시간 날씨 대시보드")
st.caption("장소를 검색하면 카카오 지도, 실시간 날씨 및 주변 추천 맛집/명소 정보를 한눈에 확인할 수 있습니다.")

if not KAKAO_REST_KEY:
    st.error("⚠️ `.env` 파일에 `KAKAO_MAP_KEY` (카카오 REST API 키)를 설정해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 카카오 키워드 장소 검색 함수
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
            documents = res.json().get("documents", [])
            return documents, None
        return None, f"카카오 검색 실패 ({res.status_code}): {res.text}"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

# -----------------------------------------------------------------------------
# 3. 카카오 주변 카테고리 검색 함수 (맛집/명소 추천용)
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 4. OpenWeatherMap 위도/경도 기반 날씨 조회 함수
# -----------------------------------------------------------------------------
def get_weather_by_coords(lat: float, lon: float, weather_key: str):
    if not weather_key:
        return None, "날씨 API 키(OPENWEATHER_API_KEY)가 등록되지 않았습니다."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": weather_key,
        "units": "metric",
        "lang": "kr",
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json(), None
        return None, f"날씨 정보 호출 실패 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

# -----------------------------------------------------------------------------
# 5. 사이드바: 탐색 모드
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
# 6. 본문 메인 레이아웃: 지도 & 날씨
# -----------------------------------------------------------------------------
if target_lat and target_lon:
    st.subheader(f"🚩 선택 장소: **{target_name}**")
    if target_addr:
        st.caption(f"📍 위치: {target_addr}")

    col_map, col_info = st.columns([6, 4], gap="large")

    # 6-1. [좌측] 지도
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

    # 6-2. [우측] 날씨 카드
    with col_info:
        st.markdown("#### 🌤️ 현지 실시간 날씨")
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

            st.markdown("#### 💡 오늘의 여행/활동 팁")
            if "비" in weather_desc or "소나기" in weather_desc:
                st.info("☔ 비 예보가 있습니다. 우산을 준비하세요.")
            elif temp >= 28:
                st.warning("☀️ 무더운 날씨입니다. 충분한 수분을 섭취하세요.")
            elif temp <= 5:
                st.info("🧣 쌀쌀한 날씨입니다. 따뜻하게 입으세요.")
            else:
                st.success("🚶 야외 활동을 즐기기에 쾌적한 날씨입니다.")

    # -------------------------------------------------------------------------
    # 7. 주변 추천 맛집 및 관광 명소 섹션
    # -------------------------------------------------------------------------
    st.divider()
    st.markdown(f"### 🍽️ **{target_name}** 주변 맛집 & 📸 추천 관광지")

    tab_food, tab_tour, tab_search = st.tabs(["🍴 주변 인기 맛집", "🏛️ 주변 관광 명소", "🔍 블로그/구글 원클릭 검색"])

    # 7-1. 주변 맛집 탭 (카카오 카테고리 FD6)
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

    # 7-2. 주변 관광지 탭 (카카오 카테고리 AT4)
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

    # 7-3. 네이버 블로그 및 구글 리뷰 원클릭 탐색 탭
    with tab_search:
        st.write(f"포털 사이트에서 실제 방문자 후기와 여행 코스를 직접 확인해보세요.")
        
        naver_blog_url = f"https://search.naver.com/search.naver?where=view&query={target_name}+맛집+여행"
        google_search_url = f"https://www.google.com/search?q={target_name}+맛집+가볼만한곳"
        kakao_blog_url = f"https://search.daum.net/search?w=blog&q={target_name}+맛집"

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.link_button("🟢 네이버 블로그 후기 검색", naver_blog_url, width="stretch")
        with sc2:
            st.link_button("🔵 구글 맛집/여행 검색", google_search_url, width="stretch")
        with sc3:
            st.link_button("🟡 다음 블로그 리뷰 보기", kakao_blog_url, width="stretch")
else:
    st.info("👈 왼쪽 사이드바에서 원하는 방식을 선택해 장소를 탐색해 보세요.")