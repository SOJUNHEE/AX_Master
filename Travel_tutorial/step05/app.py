import os
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="세계 여행 및 국가 정보",
    page_icon="🌍",
    layout="wide"
)

# 2. 사이드바 메뉴 구성
st.sidebar.title("✈️ 국가 정보")
menu = st.sidebar.radio("이동할 페이지", ["홈 (대한민국)", "중국", "일본", "미국"])

# 3. 국가별 정보 데이터 (assets/images 경로 적용)
country_data = {
    "홈 (대한민국)": {
        "title": "대한민국 (South Korea)",
        "capital": "서울 (Seoul)",
        "language": "한국어",
        "currency": "원 (KRW)",
        "description": "유구한 역사와 최첨단 IT 기술, K-컬처가 공존하는 매력적인 나라입니다.",
        "travel_site": "https://kto.visitkorea.or.kr/",
        "travel_name": "대한민국 구석구석 (한국관광공사)",
        "image": "assets/images/korea.jpg"
    },
    "중국": {
        "title": "중국 (China)",
        "capital": "베이징 (Beijing)",
        "language": "중국어",
        "currency": "위안 (CNY)",
        "description": "만리장성, 자금성 등 방대한 역사 유적과 다채로운 미식 문화를 자랑합니다.",
        "travel_site": "https://www.travelchinaguide.com/",
        "travel_name": "China Travel Guide",
        "image": "assets/images/china.jpg"
    },
    "일본": {
        "title": "일본 (Japan)",
        "capital": "도쿄 (Tokyo)",
        "language": "일본어",
        "currency": "엔 (JPY)",
        "description": "전통과 현대가 조화를 이루며, 아름다운 자연경관과 훌륭한 인프라를 갖추고 있습니다.",
        "travel_site": "https://www.japan.travel/ko/",
        "travel_name": "JNTO 일본관광국",
        "image": "assets/images/japan.jpg"
    },
    "미국": {
        "title": "미국 (USA)",
        "capital": "워싱턴 D.C. (Washington, D.C.)",
        "language": "영어",
        "currency": "달러 (USD)",
        "description": "다양한 문화와 광활한 대자연, 세계적인 대도시들이 어우러진 국가입니다.",
        "travel_site": "https://www.visittheusa.com/",
        "travel_name": "Visit The USA",
        "image": "assets/images/usa.jpg"
    }
}

current = country_data[menu]

# 4. 메인 화면 출력
st.title(current["title"])
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📌 국가 개요")
    st.write(f"- **수도:** {current['capital']}")
    st.write(f"- **공용어:** {current['language']}")
    st.write(f"- **통화:** {current['currency']}")
    st.write(f"- **설명:** {current['description']}")
    
    st.markdown("### 🔗 여행 정보 사이트")
    st.markdown(f"👉 [{current['travel_name']} 바로가기]({current['travel_site']})", unsafe_allow_html=True)

with col2:
    # app.py가 있는 폴더 위치를 자동으로 찾아서 이미지 경로를 합쳐줍니다.
    img_path = os.path.join(os.path.dirname(__file__), current["image"])
    
    if os.path.exists(img_path):
        st.image(img_path, caption=current["title"], use_container_width=True)
    else:
        st.error(f"이 경로에 파일이 진짜 있는지 확인하세요: {img_path}")