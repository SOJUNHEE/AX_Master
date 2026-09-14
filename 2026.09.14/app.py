import os
from dotenv import load_dotenv
import requests
import streamlit as st

# 1. .env 파일의 환경 변수 로드 (Line 7 ~ Line 17)
load_dotenv()
KAKAO_REST_KEY = os.getenv("KAKAO_MAP_KEY")

st.set_page_config(page_title="카카오맵 연동 지도", layout="wide")
st.title("📍 카카오맵 REST API 연동 - 서울 주요 명소")

if not KAKAO_REST_KEY:
    st.error(".env 파일에 `KAKAO_MAP_KEY=자신의_REST_API_키`를 입력해주세요.")
    st.stop()

# 2. 명소 4곳 데이터 정의 (Line 19 ~ Line 26)
places = [
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "N서울타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "북촌한옥마을", "lat": 37.5826, "lon": 126.9835},
    {"name": "동대문디자인플라자(DDP)", "lat": 37.5665, "lon": 127.0092},
]

# 3. 중심 좌표 계산 (Line 28 ~ Line 30)
center_lat = sum(p["lat"] for p in places) / len(places)
center_lon = sum(p["lon"] for p in places) / len(places)

# 4. 카카오 정적 지도 파라미터 구성 (Line 32 ~ Line 49)
markers_list = []
for p in places:
    # 카카오 정적 지도 마커 규격
    markers_list.append(
        f"type:default|lat:{p['lat']},lon:{p['lon']}|text:{p['name']}"
    )

static_map_url = "https://dapi.kakao.com/v2/maps/staticmap"

# size(가로x세로) 및 필수 파라미터 설정
params = {
    "center": f"{center_lon},{center_lat}",
    "level": 6,
    "size": "800x550",
    "markers": markers_list,
}

# 5. REST API 인증 헤더 및 단일 요청 (Line 51 ~ Line 67)
headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}

response = requests.get(static_map_url, headers=headers, params=params)

if response.status_code == 200:
    st.success("카카오 REST API 연동 성공!")
    st.image(
        response.content,
        caption="카카오 REST API 정적 지도",
        use_container_width=True,
    )
else:
    st.error(
        f"지도 호출 실패 (상태 코드: {response.status_code})\n"
        f"에러 메시지: {response.text}"
    )