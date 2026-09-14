# # folium으로 지도에 마커를 표시하는 예제 코드
# # import folium -> pip install folium
# # 서울 시내 명소 4곳의 좌표(위도,경도)와 이름을 리스트로 받아서 folium 지도를 만들고
# # 각 좌표에 이름표가 붙은 마커를 찍은 다음, basic_map.html 파일로 저장하는 예제 코드입니다.
# # 저장된 basic_map.html을 웹 브라우저로 열어서 확인
# # python 2026.09.14_test.py


# import folium
# import streamlit as st
# from streamlit_folium import st_folium

# # 페이지 설정
# st.set_page_config(page_title="서울 주요 명소 지도", layout="wide")
# st.title("📍 서울 시내 주요 명소 4곳")
# st.caption(
#     "Folium과 Streamlit을 활용한 인터랙티브 지도 (OpenStreetMap 무료 타일 사용)"
# )

# # 1. 서울 명소 데이터 리스트 (가시성 높은 마커 색상 및 아이콘)
# places = [
#     {
#         "name": "경복궁",
#         "lat": 37.5796,
#         "lon": 126.9770,
#         "color": "red",
#         "icon": "fort-awesome",
#     },
#     {
#         "name": "N서울타워",
#         "lat": 37.5512,
#         "lon": 126.9882,
#         "color": "blue",
#         "icon": "tower-broadcast",
#     },
#     {
#         "name": "북촌한옥마을",
#         "lat": 37.5826,
#         "lon": 126.9835,
#         "color": "darkgreen",
#         "icon": "house",
#     },
#     {
#         "name": "동대문디자인플라자(DDP)",
#         "lat": 37.5665,
#         "lon": 127.0092,
#         "color": "purple",
#         "icon": "palette",
#     },
# ]

# # 2. 중심 좌표 계산
# avg_lat = sum(p["lat"] for p in places) / len(places)
# avg_lon = sum(p["lon"] for p in places) / len(places)

# # 3. 지도 객체 생성 (API Key 워터마크 없는 공식 무료 OSM 타일)
# m = folium.Map(
#     location=[avg_lat, avg_lon],
#     zoom_start=13,
#     tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
#     attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
# )

# # 4. 리스트를 순회하며 지도에 마커 추가
# for place in places:
#     marker_icon = folium.Icon(
#         color=place["color"], icon=place["icon"], prefix="fa"
#     )
#     folium.Marker(
#         location=[place["lat"], place["lon"]],
#         popup=folium.Popup(f"<b>{place['name']}</b>", max_width=200),
#         tooltip=place["name"],
#         icon=marker_icon,
#     ).add_to(m)

# # 5. (선택사항) HTML 파일로도 남겨두고 싶다면 저장 유지
# html_filename = "basic_map.html"
# m.save(html_filename)

# # 6. Streamlit 웹 화면에 지도 렌더링
# st_folium(m, width=900, height=550)

import os
import webbrowser
import folium

# 1. 서울 명소 데이터 리스트 (가시성 높은 마커 색상 및 아이콘)
places = [
    {
        "name": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "color": "red",
        "icon": "fort-awesome",
    },
    {
        "name": "N서울타워",
        "lat": 37.5512,
        "lon": 126.9882,
        "color": "blue",
        "icon": "tower-broadcast",
    },
    {
        "name": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9835,
        "color": "darkgreen",
        "icon": "house",
    },
    {
        "name": "동대문디자인플라자(DDP)",
        "lat": 37.5665,
        "lon": 127.0092,
        "color": "purple",
        "icon": "palette",
    },
]

# 2. 명소 4곳의 중심 좌표 계산
avg_lat = sum(p["lat"] for p in places) / len(places)
avg_lon = sum(p["lon"] for p in places) / len(places)

# 3. 지도 객체 생성 (API Key 워터마크가 일절 없는 공식 무료 OpenStreetMap 타일)
m = folium.Map(
    location=[avg_lat, avg_lon],
    zoom_start=13,
    tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
)

# 4. 리스트를 순회하며 지도에 마커 추가
for place in places:
    marker_icon = folium.Icon(
        color=place["color"], icon=place["icon"], prefix="fa"
    )
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(f"<b>{place['name']}</b>", max_width=200),
        tooltip=place["name"],
        icon=marker_icon,
    ).add_to(m)

# 5. basic_map.html 파일로 저장
html_filename = "basic_map.html"
m.save(html_filename)
print(f"'{html_filename}' 파일 생성이 완료되었습니다.")

# 6. 저장된 HTML 파일을 기본 웹 브라우저로 자동 열기
file_path = os.path.abspath(html_filename)
webbrowser.open("file://" + file_path)
print(f"기본 웹 브라우저로 지도를 열었습니다: {file_path}")