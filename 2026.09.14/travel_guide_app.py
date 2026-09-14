import os
import re
from pathlib import Path
from dotenv import load_dotenv
import requests
import streamlit as st
import io

# -----------------------------------------------------------------------------
# 0. 라이브러리 안전 임포트 및 PDF 생성 라이브러리 확인
# -----------------------------------------------------------------------------
try:
    from streamlit_geolocation import streamlit_geolocation
    HAS_GEO = True
except (ImportError, ModuleNotFoundError):
    HAS_GEO = False
    streamlit_geolocation = None

try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except (ImportError, ModuleNotFoundError):
    HAS_FOLIUM = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_REPORTLAB = True
except (ImportError, ModuleNotFoundError):
    HAS_REPORTLAB = False

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
GEMINI_API_KEY = get_secret_key("GEMINI_API_KEY")

st.set_page_config(
    page_title="스마트 글로벌 트래블 매니저",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not KAKAO_REST_KEY:
    st.error("⚠️ `KAKAO_MAP_KEY` (카카오 REST API 키)를 .env 또는 Streamlit Secrets에 설정해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 다국어(i18n) 메타데이터
# -----------------------------------------------------------------------------
I18N = {
    "ko": {
        "title": "🧭 스마트 글로벌 트래블 매니저",
        "subtitle": "전 세계 도시 & 국내 전역 실시간 위치 기반 날씨·환율·항공권·AI 여행 코스 원스톱 가이드",
        "weather_tab": "🌤️ 현지 실시간 날씨",
        "fx_tab": "💱 실시간 환율 & 항공권",
        "ai_tab": "🤖 AI 맞춤형 여행 코스",
        "feels_like": "체감 온도",
        "humidity": "습도",
        "wind": "풍속",
        "travel_tip": "💡 오늘의 여행 팁",
        "tip_rain": "☔ 비 예보가 있습니다. 우산을 꼭 챙기세요.",
        "tip_hot": "☀️ 날씨가 많이 더우니 충분한 수분을 섭취하세요.",
        "tip_cold": "🧣 쌀쌀한 날씨입니다. 따뜻한 외투를 준비하세요.",
        "tip_good": "🚶 야외 활동과 산책을 즐기기 쾌적한 날씨입니다.",
        "calc_title": "💱 출발국 ⇄ 현지 통화 스마트 환전 계산",
        "amt_label": "환전할 금액",
        "res_label": "환전 수령 예상 금액",
        "rate_label": "기준 환율",
        "flight_title": "✈️ 실시간 항공권 예상 가격 & 예약 사이트",
        "food_tab": "🍴 주변 인기 맛집",
        "tour_tab": "🏛️ 주변 관광 명소",
        "portal_tab": "🔍 실시간 블로그/후기",
        "review_btn": "메뉴 / 리뷰",
        "detail_btn": "명소 상세",
        "google_food": "🍽️ 구글 현지 인기 맛집",
        "google_tour": "🏛️ 구글 주변 관광 명소",
        "tripadvisor": "🦉 트립어드바이저 랭킹",
        "naver_blog": "🟢 네이버 여행기 검색"
    },
    "en": {
        "title": "🧭 Smart Global Travel Manager",
        "subtitle": "Real-time location, weather, exchange rate, flights & AI itinerary guide worldwide",
        "weather_tab": "🌤️ Live Weather",
        "fx_tab": "💱 Live FX & Flights",
        "ai_tab": "🤖 AI Travel Itinerary",
        "feels_like": "Feels Like",
        "humidity": "Humidity",
        "wind": "Wind Speed",
        "travel_tip": "💡 Travel Tip",
        "tip_rain": "☔ Rain expected. Don't forget your umbrella.",
        "tip_hot": "☀️ Very warm. Stay hydrated while exploring.",
        "tip_cold": "🧣 Chilly weather. Dress warmly.",
        "tip_good": "🚶 Perfect weather for walking and sightseeing.",
        "calc_title": "💱 Smart Currency Converter",
        "amt_label": "Amount to convert",
        "res_label": "Converted Amount",
        "rate_label": "Exchange Rate",
        "flight_title": "✈️ Flight Price Estimates & Booking",
        "food_tab": "🍴 Popular Restaurants",
        "tour_tab": "🏛️ Top Attractions",
        "portal_tab": "🔍 Travel Blogs & Search",
        "review_btn": "Menu / Reviews",
        "detail_btn": "Details",
        "google_food": "🍽️ Google Popular Foods",
        "google_tour": "🏛️ Top Attractions",
        "tripadvisor": "🦉 TripAdvisor Reviews",
        "naver_blog": "🟢 Travel Blog Reviews"
    },
    "ja": {
        "title": "🧭 スマートグローバルトラベルガイド",
        "subtitle": "全世界の都市と韓国全域のリアルタイム天気・為替・航空券・AI旅行コースワンストップガイド",
        "weather_tab": "🌤️ 現地のリアルタイム天気",
        "fx_tab": "💱 為替レート & 航空券",
        "ai_tab": "🤖 AIトラベルプラン",
        "feels_like": "体感温度",
        "humidity": "湿度",
        "wind": "風速",
        "travel_tip": "💡 おすすめアドバイス",
        "tip_rain": "☔ 雨の予報です。折りたたみ傘をお持ちください。",
        "tip_hot": "☀️ 暑い日です。水分補給をしっかり行ってください。",
        "tip_cold": "🧣 肌寒い天気です。暖かい上着をご用意ください。",
        "tip_good": "🚶 お散歩や観光に最適な快適な天気です。",
        "calc_title": "💱 自動為替計算",
        "amt_label": "換金する金額",
        "res_label": "受取予想金額",
        "rate_label": "基準為替レート",
        "flight_title": "✈️ 航空券の予想価格 & 予約サイト",
        "food_tab": "🍴 周辺の人気グルメ",
        "tour_tab": "🏛️ 周辺の観光名所",
        "portal_tab": "🔍 旅行レビュー・検索",
        "review_btn": "メニュー / レビュー",
        "detail_btn": "スポット詳細",
        "google_food": "🍽️ Google 人気グルメ",
        "google_tour": "🏛️ 周辺観光名所",
        "tripadvisor": "🦉 トリップアドバイザー",
        "naver_blog": "🟢 旅行ブログ検索"
    }
}

GLOBAL_CURRENCY_NAMES = {
    "KRW": "대한민국 원 (KRW)", "USD": "미국 달러 (USD)", "JPY": "일본 엔 (JPY)", "EUR": "유로존 유로 (EUR)",
    "GBP": "영국 파운드 (GBP)", "CNY": "중국 위안 (CNY)", "VND": "베트남 동 (VND)", "THB": "태국 바트 (THB)",
    "TWD": "대만 달러 (TWD)", "HKD": "홍콩 달러 (HKD)", "SGD": "싱가포르 달러 (SGD)", "AUD": "호주 달러 (AUD)",
    "CAD": "캐나다 달러 (CAD)", "CHF": "스위스 프랑 (CHF)", "PHP": "필리핀 페소 (PHP)"
}

# -----------------------------------------------------------------------------
# 3. 탭 선택 시 흰색이 너무 튀지 않도록 부드럽게 어우러지는 모던 스타일 CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    .main-header-title {
        font-family: 'Plus Jakarta Sans', 'Pretendard', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem !important;
    }
    .main-header-sub {
        font-size: 0.98rem !important;
        color: #475569 !important;
        margin-bottom: 1.5rem !important;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1.5px solid #e2e8f0 !important;
        box-shadow: 4px 0 20px rgba(226, 232, 240, 0.5);
    }
    section[data-testid="stSidebar"] * {
        color: #0f172a !important;
    }

    .target-banner-card {
        background: linear-gradient(135deg, #1e293b 10%, #0f172a 100%);
        border-radius: 18px;
        padding: 22px 28px;
        color: #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
        margin-bottom: 20px;
    }
    .target-banner-name {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-bottom: 6px !important;
    }
    .target-banner-addr {
        font-size: 0.95rem !important;
        color: #94a3b8 !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    [data-testid="stImage"] img {
        height: 220px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 16px rgba(148, 163, 184, 0.2) !important;
        border: 2px solid #ffffff;
    }

    [data-testid="stImageCaption"] {
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        text-align: center !important;
        margin-top: 8px !important;
    }

    .premium-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.6) !important;
    }
    .place-name-text {
        font-size: 1.18rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }
    .badge-tag {
        display: inline-block;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #2563eb !important;
        background: #eff6ff !important;
        border: 1px solid #dbeafe !important;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-left: 8px;
        vertical-align: middle;
    }
    .badge-dist {
        display: inline-block;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #ea580c !important;
        background: #fff7ed !important;
        border: 1px solid #ffedd5 !important;
        padding: 3px 9px;
        border-radius: 6px;
        margin-left: 6px;
    }
    .place-addr-text {
        font-size: 0.92rem !important;
        color: #475569 !important;
        margin-top: 8px !important;
        line-height: 1.4;
    }

    .glass-metric-card {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(8px);
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(226, 232, 240, 0.5) !important;
    }

    /* 탭 스타일 수정: 선택 시 하얗게 둥둥 뜨는 느낌을 줄이고 부드러운 그림자와 톤앤매너 적용 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 5px !important;
        gap: 4px !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #64748b !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        background-color: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
        border: 1px solid #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 전 세계 환율 피드 API
# -----------------------------------------------------------------------------
@st.cache_data(ttl=1800)
def get_global_exchange_rates(api_key: str):
    if not api_key:
        return None, "외환 API 키 미설정"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {}), None
            return None, data.get("error-type", "데이터 피드 에러")
        return None, f"서버 에러 ({res.status_code})"
    except Exception as e:
        return None, f"통신 장애: {e}"

live_rates, _ = get_global_exchange_rates(EXCHANGE_KEY)
fallback_rates = {
    "USD": 1.0, "KRW": 1380.0, "JPY": 154.5, "EUR": 0.92, "GBP": 0.79,
    "CNY": 7.24, "VND": 25400.0, "THB": 36.5, "TWD": 32.3, "HKD": 7.82,
    "SGD": 1.35, "AUD": 1.52, "CAD": 1.37, "CHF": 0.91, "PHP": 58.0
}
rates_dict = live_rates if (live_rates and isinstance(live_rates, dict)) else fallback_rates

priority_currencies = ["KRW", "USD", "JPY", "EUR", "CNY", "GBP", "VND", "THB", "TWD", "HKD", "SGD", "AUD", "CAD", "CHF", "PHP"]
all_supported_currencies = priority_currencies + sorted([k for k in rates_dict.keys() if k not in priority_currencies])

# -----------------------------------------------------------------------------
# 5. 이미지 링크 DB
# -----------------------------------------------------------------------------
CURATED_CITY_IMAGES = {
    "중국": [
        {"name": "만리장성 (Great Wall of China)", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=900&q=80"},
        {"name": "자금성 (Forbidden City)", "url": "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=900&q=80"},
        {"name": "상하이 와이탄 (The Bund)", "url": "https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=900&q=80"}
    ],
    "베이징": [
        {"name": "만리장성", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=900&q=80"},
        {"name": "자금성", "url": "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=900&q=80"},
        {"name": "이화원 & 천단공원", "url": "https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=900&q=80"}
    ],
    "상하이": [
        {"name": "상하이 와이탄 야경", "url": "https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=900&q=80"},
        {"name": "동방명주 & 푸둥 스카이라인", "url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=900&q=80"},
        {"name": "예원 전통 정원", "url": "https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=900&q=80"}
    ],
    "도쿄": [
        {"name": "도쿄 타워", "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=900&q=80"},
        {"name": "시부야 스크램블 교차로", "url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=900&q=80"},
        {"name": "센소지 아사쿠사", "url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=900&q=80"}
    ],
    "파리": [
        {"name": "에펠탑 (Tour Eiffel)", "url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=900&q=80"},
        {"name": "루브르 박물관", "url": "https://images.unsplash.com/photo-1550340499-a6c0f083dcb4?w=900&q=80"},
        {"name": "개선문 & 샹젤리제 거리", "url": "https://images.unsplash.com/photo-1522093007470-ee8db030f9ec?w=900&q=80"}
    ],
    "방콕": [
        {"name": "왓 아룬 새벽 사원", "url": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=900&q=80"},
        {"name": "방콕 왕궁", "url": "https://images.unsplash.com/photo-1563492065599-3520f775eeed?w=900&q=80"},
        {"name": "왓 포 거대 와불상", "url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=900&q=80"}
    ],
    "뉴욕": [
        {"name": "타임스 스퀘어", "url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=900&q=80"},
        {"name": "맨해튼 스카이라인", "url": "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=900&q=80"},
        {"name": "브루클린 브릿지", "url": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=900&q=80"}
    ],
    "다낭": [
        {"name": "바나힐 골든 브릿지", "url": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=900&q=80"},
        {"name": "미케 비치", "url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=900&q=80"},
        {"name": "오행산 마블 마운틴", "url": "https://images.unsplash.com/photo-1528127269322-539801943592?w=900&q=80"}
    ],
    "런던": [
        {"name": "빅 벤 & 국회의사당", "url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=900&q=80"},
        {"name": "런던 아이", "url": "https://images.unsplash.com/photo-1526129318478-62ed807ebdf9?w=900&q=80"},
        {"name": "타워 브리지", "url": "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?w=900&q=80"}
    ],
    "서울": [
        {"name": "경복궁 근정전", "url": "https://images.unsplash.com/photo-1538485399081-7191377e8241?w=900&q=80"},
        {"name": "N서울타워 & 남산 야경", "url": "https://images.unsplash.com/photo-1578637387939-43c525ec9001?w=900&q=80"},
        {"name": "북촌 한옥마을 전통 거리", "url": "https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=900&q=80"}
    ]
}

def get_nearby_tour_or_food_images(place_name: str, kakao_key: str, size: int = 3):
    for city_key, img_list in CURATED_CITY_IMAGES.items():
        if city_key in place_name:
            return img_list[:size]

    results = []
    clean_name = re.sub(r"\(.*?\)", "", place_name).strip()

    if kakao_key:
        try:
            url = "https://dapi.kakao.com/v2/search/image"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {"query": f"{clean_name} 풍경 명소", "size": size, "sort": "accuracy"}
            res = requests.get(url, headers=headers, params=params, timeout=4)
            if res.status_code == 200:
                docs = res.json().get("documents", [])
                for idx, d in enumerate(docs):
                    img_u = d.get("image_url")
                    if img_u and not any(r["url"] == img_u for r in results):
                        results.append({"name": f"{clean_name} 랜드마크 {idx+1}", "url": img_u})
        except Exception:
            pass

    general_fallbacks = [
        {"name": f"{clean_name} 대표 랜드마크", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=900&q=80"},
        {"name": f"{clean_name} 도심 스카이라인", "url": "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=900&q=80"},
        {"name": f"{clean_name} 감성 투어 명소", "url": "https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=900&q=80"}
    ]
    for fb in general_fallbacks:
        if len(results) >= size:
            break
        results.append(fb)

    return results[:size]

# -----------------------------------------------------------------------------
# 6. 통화 및 국가 코드 판별
# -----------------------------------------------------------------------------
def detect_currency_and_cc(name_str: str):
    q = name_str.lower()
    mapping = [
        (["중국", "베이징", "상하이", "china", "beijing", "shanghai"], ("CNY", "cn")),
        (["도쿄", "일본", "오사카", "tokyo", "japan", "osaka"], ("JPY", "jp")),
        (["방콕", "태국", "bangkok", "thailand"], ("THB", "th")),
        (["파리", "프랑스", "paris", "france"], ("EUR", "fr")),
        (["뉴욕", "미국", "new york", "usa"], ("USD", "us")),
        (["다낭", "베트남", "danang", "vietnam"], ("VND", "vn")),
        (["런던", "영국", "london", "uk"], ("GBP", "gb")),
        (["시드니", "호주", "sydney", "australia"], ("AUD", "au")),
        (["싱가포르", "singapore"], ("SGD", "sg")),
        (["타이베이", "대만", "taiwan"], ("TWD", "tw")),
        (["홍콩", "hong kong"], ("HKD", "hk")),
        (["취리히", "스위스", "switzerland"], ("CHF", "ch"))
    ]
    for keywords, res in mapping:
        if any(k in q for k in keywords):
            return res
    return "USD", "us"

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
        return None, f"카카오 검색 실패 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

def search_global_place_osm(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "addressdetails": 1, "limit": 5, "accept-language": "ko,en"}
    headers = {"User-Agent": "GlobalSmartTravelGuide/2.0"}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=6)
        if res.status_code == 200:
            return res.json(), None
        return None, "글로벌 검색 실패"
    except Exception as e:
        return None, f"해외 네트워크 오류: {e}"

def get_nearby_places_by_category(category_code: str, lat: float, lon: float, kakao_key: str, radius: int = 2000):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    params = {"category_group_code": category_code, "x": str(lon), "y": str(lat), "radius": str(radius), "sort": "distance", "size": 5}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("documents", []), None
        return [], "카테고리 검색 실패"
    except Exception as e:
        return [], f"네트워크 오류: {e}"

def get_weather_by_coords(lat: float, lon: float, weather_key: str, lang: str = "kr"):
    if not weather_key:
        return None, "날씨 API 키 미설정"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": weather_key, "units": "metric", "lang": lang}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json(), None
        return None, f"날씨 호출 실패 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

# -----------------------------------------------------------------------------
# 6-1. AI 여행 경로 생성 함수
# -----------------------------------------------------------------------------
def generate_ai_travel_itinerary(dest_name: str, days: int, style: str):
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            prompt = f"'{dest_name}' 여행지에서 {days}일 동안의 '{style}' 스타일 맞춤형 일정을 오전, 오후, 저녁으로 나누어 상세하고 실용적으로 작성해 주세요."
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    return f"""
스마트 맞춤형 [{dest_name}] {days}일 [{style}] 추천 코스

[ Day 1: 핵심 명소 탐방 ]
- 09:30 ~ 11:30 | {dest_name} 중심가 도착 및 랜드마크 스냅 사진 촬영
- 12:00 ~ 13:30 | 현지 인기 로컬 맛집에서 대표 미식 체험
- 14:00 ~ 17:00 | 역사와 문화가 숨쉬는 핵심 박물관 또는 전통 거리 산책
- 18:30 ~ | 아름다운 야경을 감상할 수 있는 전망대 및 디너 코스

[ Day 2: 힐링 및 로컬 체험 코스 ]
- 10:00 ~ 12:30 | 탁 트인 자연 경관 또는 핫플레이스 카페 투어
- 13:00 ~ 14:30 | 현지인들이 사랑하는 로컬 푸드 점심 식사
- 15:00 ~ 18:00 | 기념품 쇼핑 및 트렌디한 편집샵 탐방
- 19:00 ~ | 여행의 피로를 녹여줄 아늑한 바 또는 휴식 시간

(안내: 현지 상황에 맞춰 유연하게 일정에 변화를 주어 더욱 풍성한 여행을 즐겨보세요!)
"""

# -----------------------------------------------------------------------------
# 6-2. PDF 생성 함수 (ReportLab 이용 - 없을 경우 텍스트 fallback 지원으로 다운로드 보장)
# -----------------------------------------------------------------------------
def create_travel_pdf(dest_name: str, itinerary_text: str):
    if not HAS_REPORTLAB:
        return None
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    try:
        font_path = "C:/Windows/Fonts/malgun.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Malgun', font_path))
            c.setFont('Malgun', 16)
        else:
            c.setFont('Helvetica-Bold', 16)
    except Exception:
        c.setFont('Helvetica-Bold', 16)

    c.drawString(50, height - 50, f"Smart Travel Manager - Itinerary Report")
    c.setFont('Malgun', 12) if 'Malgun' in pdfmetrics.getRegisteredFonts() else c.setFont('Helvetica', 12)
    c.drawString(50, height - 80, f"Destination: {dest_name}")
    c.line(50, height - 90, width - 50, height - 90)

    text_object = c.beginText(50, height - 120)
    text_object.setFont('Malgun', 10) if 'Malgun' in pdfmetrics.getRegisteredFonts() else text_object.setFont('Helvetica', 10)
    
    for line in itinerary_text.split('\n'):
        clean_line = re.sub(r'[^\w\s\.,!?()~|:\-\[\]가-힣]', '', line)
        text_object.textLine(clean_line)
        
    c.drawText(text_object)
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 7. 사이드바 UI
# -----------------------------------------------------------------------------
preset_places = {
    "경복궁": {"lat": 37.5796, "lon": 126.9770, "address": "서울 종로구 사직로 161", "kakao_url": "https://place.map.kakao.com/18600021", "is_overseas": False, "cc": "kr", "currency": "KRW"},
    "N서울타워": {"lat": 37.5512, "lon": 126.9882, "address": "서울 용산구 남산공원길 105", "kakao_url": "https://place.map.kakao.com/8120619", "is_overseas": False, "cc": "kr", "currency": "KRW"},
    "도쿄 시부야 (일본)": {"lat": 35.6580, "lon": 139.7016, "address": "Tokyo, Shibuya City, Japan", "kakao_url": None, "is_overseas": True, "currency": "JPY", "cc": "jp"},
    "파리 에펠탑 (프랑스)": {"lat": 48.8584, "lon": 2.2945, "address": "Champ de Mars, Paris, France", "kakao_url": None, "is_overseas": True, "currency": "EUR", "cc": "fr"},
    "뉴욕 타임스스퀘어 (미국)": {"lat": 40.7580, "lon": -73.9855, "address": "Manhattan, NY 10036, USA", "kakao_url": None, "is_overseas": True, "currency": "USD", "cc": "us"},
    "방콕 왓 아룬 (태국)": {"lat": 13.7437, "lon": 100.4888, "address": "Bangkok Yai, Bangkok, Thailand", "kakao_url": None, "is_overseas": True, "currency": "THB", "cc": "th"},
    "다낭 미케비치 (베트남)": {"lat": 16.0592, "lon": 108.2435, "address": "My Khe Beach, Da Nang, Vietnam", "kakao_url": None, "is_overseas": True, "currency": "VND", "cc": "vn"},
    "런던 빅벤 (영국)": {"lat": 51.5007, "lon": -0.1246, "address": "London SW1A 0AA, UK", "kakao_url": None, "is_overseas": True, "currency": "GBP", "cc": "gb"},
}

with st.sidebar:
    st.markdown("### 🌐 **언어 설정 / Language**")
    lang_mode = st.selectbox("UI 언어 선택", ["한국어 (KO)", "English (EN)", "日本語 (JA)"])

    st.markdown("---")
    st.markdown("👉 **여행할 권역을 선택해주세요!**")
    region_type = st.radio("여행지 권역", ["🇰🇷 국내 여행", "✈️ 해외 여행"])

    target_name = None
    target_lat = None
    target_lon = None
    target_addr = ""
    target_url = None
    target_cc = "kr"
    is_overseas = (region_type == "✈️ 해외 여행")
    auto_currency = "KRW"

    if not is_overseas:
        domestic_mode = st.radio("국내 탐색 방식", ["국내 추천 명소", "전국 장소 검색", "내 주변 반경 검색"])

        if domestic_mode == "국내 추천 명소":
            dom_presets = {k: v for k, v in preset_places.items() if not v["is_overseas"]}
            selected_name = st.selectbox("추천 명소 선택", list(dom_presets.keys()))
            target_name = selected_name
            target_lat = dom_presets[selected_name]["lat"]
            target_lon = dom_presets[selected_name]["lon"]
            target_addr = dom_presets[selected_name]["address"]
            target_url = dom_presets[selected_name]["kakao_url"]
            target_cc = "kr"
            auto_currency = "KRW"

        elif domestic_mode == "전국 장소 검색":
            search_query = st.text_input("국내 장소/주소 입력", placeholder="예: 부산역, 해운대, 성수동")
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
                    target_cc = "kr"
                    auto_currency = "KRW"
                else:
                    st.warning(f"'{search_query}' 검색 결과가 없습니다.")

        else:
            st.caption("현재 위치를 기반으로 반경을 검색합니다.")
            if HAS_GEO and streamlit_geolocation:
                geo_location = streamlit_geolocation()
                if geo_location and geo_location.get("latitude"):
                    my_lat = geo_location["latitude"]
                    my_lon = geo_location["longitude"]
                    st.success(f"현재 위치 감지됨 ({my_lat:.4f}, {my_lon:.4f})")
                else:
                    st.info("위치 권한 대기 중: 기본 위치(서울시청)로 설정됩니다.")
                    my_lat, my_lon = 37.5665, 126.9780
            else:
                st.info("📍 위치 모듈 기본값: 서울시청 기준으로 작동합니다.")
                my_lat, my_lon = 37.5665, 126.9780

            search_radius = st.slider("검색 반경 (미터)", min_value=300, max_value=5000, value=1000, step=100)
            search_query = st.text_input("내 주변 검색어 입력", placeholder="예: 카페, 편의점, 맛집")

            if search_query:
                places_found, search_err = search_kakao_place(
                    keyword=search_query, kakao_key=KAKAO_REST_KEY, center_lat=my_lat, center_lon=my_lon, radius=search_radius
                )
                if search_err:
                    st.error(search_err)
                elif places_found:
                    place_names = [f"{p['place_name']} [{p.get('distance', '?')}m]" for p in places_found]
                    selected_idx = st.selectbox("반경 내 검색 결과", range(len(place_names)), format_func=lambda x: place_names[x])
                    chosen = places_found[selected_idx]
                    target_name = chosen["place_name"]
                    target_lat = float(chosen["y"])
                    target_lon = float(chosen["x"])
                    target_addr = chosen.get("road_address_name") or chosen.get("address_name")
                    target_url = chosen.get("place_url")
                    target_cc = "kr"
                    auto_currency = "KRW"

    else:
        global_mode = st.radio("해외 탐색 방식", ["해외 추천 도시 6선", "전 세계 도시/명소 직접 검색"])

        if global_mode == "해외 추천 도시 6선":
            overseas_presets = {k: v for k, v in preset_places.items() if v["is_overseas"]}
            selected_name = st.selectbox("해외 추천 도시", list(overseas_presets.keys()))
            target_name = selected_name
            target_lat = overseas_presets[selected_name]["lat"]
            target_lon = overseas_presets[selected_name]["lon"]
            target_addr = overseas_presets[selected_name]["address"]
            target_cc = overseas_presets[selected_name].get("cc", "us")
            auto_currency = overseas_presets[selected_name].get("currency", "USD")

        else:
            global_query = st.text_input("해외 도시/랜드마크 입력", placeholder="예: 도쿄, 파리, 뉴욕, 방콕")
            if global_query:
                osm_results, osm_err = search_global_place_osm(global_query)
                if osm_err:
                    st.error(osm_err)
                elif osm_results:
                    osm_names = [f"{item.get('display_name')[:48]}..." for item in osm_results]
                    sel_osm_idx = st.selectbox("해외 위치 검색 결과", range(len(osm_names)), format_func=lambda x: osm_names[x])
                    chosen_osm = osm_results[sel_osm_idx]
                    target_name = chosen_osm.get("name") or global_query
                    target_lat = float(chosen_osm["lat"])
                    target_lon = float(chosen_osm["lon"])
                    target_addr = chosen_osm.get("display_name")
                    
                    detected_cur, detected_cc = detect_currency_and_cc(target_name + " " + global_query)
                    auto_currency = detected_cur if detected_cur in rates_dict else "USD"
                    target_cc = detected_cc

# 언어 코드 확정
if lang_mode == "한국어 (KO)":
    active_lang = "ko"
elif lang_mode == "English (EN)":
    active_lang = "en"
else:
    active_lang = "ja"

t = I18N.get(active_lang, I18N["ko"])

# -----------------------------------------------------------------------------
# 8. 본문 레이아웃
# -----------------------------------------------------------------------------
st.markdown(f'<div class="main-header-title">{t["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-header-sub">{t["subtitle"]}</div>', unsafe_allow_html=True)

if target_lat and target_lon:
    region_badge = "✈️ Global" if is_overseas else "🇰🇷 Domestic"
    st.markdown(f"""
    <div class="target-banner-card">
        <div class="target-banner-name">[{region_badge}] {target_name}</div>
        <div class="target-banner-addr"><span>📍 Location / 주소:</span> {target_addr}</div>
    </div>
    """, unsafe_allow_html=True)

    # 갤러리 이미지 출력
    place_images = get_nearby_tour_or_food_images(target_name, KAKAO_REST_KEY, size=3)
    if place_images:
        img_cols = st.columns(len(place_images))
        for idx, item in enumerate(place_images):
            with img_cols[idx]:
                st.image(item["url"], use_container_width=True, caption=f"📸 {item['name']}")
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    col_map, col_right = st.columns([6, 4], gap="large")

    # 8-1. [좌측] 지도 & 길찾기
    with col_map:
        st.markdown("#### 🗺️ 인터랙티브 여행 지도")
        if HAS_FOLIUM:
            m = folium.Map(location=[target_lat, target_lon], zoom_start=15)
            folium.Marker([target_lat, target_lon], popup=target_name, tooltip=target_name, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
            st_folium(m, width="100%", height=450, returned_objects=[])
        else:
            st.map([{"lat": target_lat, "lon": target_lon}], zoom=14)

        btn_col1, btn_col2 = st.columns(2)
        if not is_overseas:
            kakao_link = target_url if target_url else f"https://map.kakao.com/link/map/{target_name},{target_lat},{target_lon}"
            route_link = f"https://map.kakao.com/link/to/{target_name},{target_lat},{target_lon}"
            with btn_col1:
                st.link_button("📍 카카오맵 상세 보기", kakao_link, use_container_width=True)
            with btn_col2:
                st.link_button("🚗 카카오맵 길찾기", route_link, use_container_width=True)
        else:
            google_map_link = f"https://www.google.com/maps/search/?api=1&query={target_lat},{target_lon}"
            with btn_col1:
                st.link_button("🌐 구글 맵스 열기", google_map_link, use_container_width=True)
            with btn_col2:
                st.link_button("🧭 구글 길찾기", f"{google_map_link}&dirflg=d", use_container_width=True)

    # 8-2. [우측] 날씨 & 환율 계산기 & AI 여행 코스 및 다운로드 탭
    with col_right:
        tab_weather, tab_fx_quick, tab_ai_route = st.tabs([t["weather_tab"], t["fx_tab"], t["ai_tab"]])

        with tab_weather:
            weather_api_lang = "kr" if active_lang == "ko" else ("ja" if active_lang == "ja" else "en")
            w_data, w_err = get_weather_by_coords(target_lat, target_lon, WEATHER_KEY, lang=weather_api_lang)

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

                st.markdown(f"""
                <div class="glass-metric-card">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <img src="{icon_url}" width="70" />
                        <div>
                            <div style="font-size: 2.1rem; font-weight: 800; color: #0f172a; line-height: 1.1;">{temp:.1f} °C</div>
                            <div style="font-size: 1.0rem; font-weight: 700; color: #475569; margin-top: 4px;">{weather_desc}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric(t["feels_like"], f"{feels_like:.1f} °C")
                m2.metric(t["humidity"], f"{humidity} %")
                st.metric(t["wind"], f"{wind} m/s")

                st.markdown(f"##### {t['travel_tip']}")
                if "비" in weather_desc or "rain" in weather_desc.lower() or "雨" in weather_desc:
                    st.info(t["tip_rain"])
                elif temp >= 28:
                    st.warning(t["tip_hot"])
                elif temp <= 5:
                    st.info(t["tip_cold"])
                else:
                    st.success(t["tip_good"])

        with tab_fx_quick:
            st.markdown(f"<div style='font-size: 1.0rem; font-weight: 800; color: #0f172a; margin-bottom: 6px;'>{t['calc_title']}</div>", unsafe_allow_html=True)

            if is_overseas:
                detected_cur, _ = detect_currency_and_cc(target_name)
                auto_currency = detected_cur

            target_to_currency = auto_currency if auto_currency in all_supported_currencies else ("USD" if is_overseas else "KRW")
            
            if "last_dest_key" not in st.session_state or st.session_state["last_dest_key"] != target_name:
                st.session_state["last_dest_key"] = target_name
                st.session_state["quick_to_cur"] = target_to_currency

            def format_currency_label(code):
                return GLOBAL_CURRENCY_NAMES.get(code, f"{code} (공식 통화)")

            col_src, col_dst = st.columns(2)
            with col_src:
                from_cur = st.selectbox("출발 통화", all_supported_currencies, index=0, format_func=format_currency_label, key="quick_from_cur")
            with col_dst:
                to_cur = st.selectbox("도착지 통화 (현지)", all_supported_currencies, format_func=format_currency_label, key="quick_to_cur")

            calc_amt = st.number_input(f"{t['amt_label']} ({from_cur})", min_value=0.0, value=100000.0 if from_cur == "KRW" else 100.0, step=1000.0, format="%.2f", key="quick_amt_input")

            from_usd_rate = rates_dict.get(from_cur, 1.0)
            to_usd_rate = rates_dict.get(to_cur, 1.0)

            exchange_rate = to_usd_rate / from_usd_rate if from_usd_rate > 0 else 0
            reverse_rate = from_usd_rate / to_usd_rate if to_usd_rate > 0 else 0
            converted_result = calc_amt * exchange_rate

            st.markdown(f"""
            <div class="glass-metric-card" style="margin-top: 10px;">
                <div style="font-size: 0.85rem; color: #475569; font-weight: 700;">{t['res_label']} ({to_cur})</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #2563eb; margin: 4px 0;">{converted_result:,.2f} {to_cur}</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">
                    • 1 {from_cur} = {exchange_rate:,.4f} {to_cur}<br>
                    • 1 {to_cur} = <b>{reverse_rate:,.2f} {from_cur}</b> (여행 체감 물가)
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 항공권 정보 및 예약 사이트 버튼
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 1.0rem; font-weight: 800; color: #0f172a; margin-bottom: 6px;'>{t['flight_title']}</div>", unsafe_allow_html=True)
            
            clean_dest = target_name.split("(")[0].strip()
            skyscanner_url = f"https://www.skyscanner.co.kr/transport/flights/{target_cc}/"
            google_flights_url = f"https://www.google.com/travel/flights?q=flights+to+{clean_dest}"
            naver_flight_url = f"https://flight.naver.com/"

            st.markdown(f"""
            <div class="glass-metric-card" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;">
                <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">
                    ✈️ 인천(ICN) ⇄ {target_name} 항공편
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-bottom: 12px;">
                    • 예상 평균 가격: <b>{'약 30만 ~ 120만 원 (시즌별 상이)' if is_overseas else '국내선 / KTX 이용권역'}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                st.link_button("🌐 스카이스캐너", skyscanner_url, use_container_width=True)
            with f_col2:
                st.link_button("✈️ 구글 플라이트", google_flights_url, use_container_width=True)
            with f_col3:
                st.link_button("🟢 네이버 항공권", naver_flight_url, use_container_width=True)

        with tab_ai_route:
            st.markdown("<div style='font-size: 1.0rem; font-weight: 800; color: #0f172a; margin-bottom: 6px;'>🤖 AI 맞춤형 여행 일정 플래너</div>", unsafe_allow_html=True)
            st.caption("선택한 목적지의 맞춤 일정을 생성하고 즉시 다운로드할 수 있습니다!")

            ai_days = st.slider("여행 기간 (일)", min_value=1, max_value=7, value=2, key="ai_days_slider")
            ai_style = st.selectbox("여행 스타일", ["힐링 & 미식 투어", "역사 & 문화 탐방", "인생샷 & 액티비티", "로컬 감성 산책"], key="ai_style_select")

            if st.button("✨ AI 맞춤 일정 생성하기", use_container_width=True):
                with st.spinner("최적의 여행 경로를 생성하는 중입니다..."):
                    itinerary_result = generate_ai_travel_itinerary(target_name, ai_days, ai_style)
                    st.session_state["generated_itinerary"] = itinerary_result
                    st.success("여행 일정이 완성되었습니다!")

            if "generated_itinerary" in st.session_state and st.session_state["generated_itinerary"]:
                st.markdown("---")
                st.markdown(st.session_state["generated_itinerary"])
                
                # ReportLab 설치 여부와 관계없이 다운로드가 항상 가능하도록 예외 처리 및 텍스트/PDF 분기 처리
                pdf_data = create_travel_pdf(target_name, st.session_state["generated_itinerary"])
                if pdf_data:
                    st.download_button(
                        label="📄 여행 일정표 PDF 다운로드",
                        data=pdf_data,
                        file_name=f"{target_name}_travel_itinerary.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    # reportlab이 없을 때 즉시 다운로드 가능한 텍스트(.txt) 다운로드 버튼 제공
                    st.download_button(
                        label="📄 여행 일정표 텍스트(.txt) 다운로드",
                        data=st.session_state["generated_itinerary"],
                        file_name=f"{target_name}_travel_itinerary.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

    # -------------------------------------------------------------------------
    # 8-3. 주변 맛집/명소/리뷰 섹션
    # -------------------------------------------------------------------------
    st.divider()

    st.markdown(f"### 🍽️ **{target_name}** {t['food_tab']} & {t['tour_tab']}")
    tab_food, tab_tour, tab_search = st.tabs([t["food_tab"], t["tour_tab"], t["portal_tab"]])

    if not is_overseas:
        foods_list, _ = get_nearby_places_by_category("FD6", target_lat, target_lon, KAKAO_REST_KEY, radius=2000)
        tours_list, _ = get_nearby_places_by_category("AT4", target_lat, target_lon, KAKAO_REST_KEY, radius=3000)

        with tab_food:
            if foods_list:
                for item in foods_list:
                    addr = item.get('road_address_name') or item.get('address_name')
                    dist = item.get('distance', '?')
                    cat = item.get('category_name', '').split(' > ')[-1]

                    c_info, c_btn = st.columns([4.2, 1.2])
                    with c_info:
                        st.markdown(f"""
                        <div class="premium-card">
                            <div>
                                <span class="place-name-text">{item['place_name']}</span>
                                <span class="badge-tag">{cat}</span>
                                <span class="badge-dist">{dist}m</span>
                            </div>
                            <div class="place-addr-text">📍 {addr}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_btn:
                        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                        st.link_button(t["review_btn"], item["place_url"], use_container_width=True)
            else:
                st.info("반경 2km 이내에 등록된 맛집 정보가 없습니다.")

        with tab_tour:
            if tours_list:
                for item in tours_list:
                    addr = item.get('road_address_name') or item.get('address_name')
                    dist = item.get('distance', '?')

                    c_info, c_btn = st.columns([4.2, 1.2])
                    with c_info:
                        st.markdown(f"""
                        <div class="premium-card">
                            <div>
                                <span class="place-name-text">{item['place_name']}</span>
                                <span class="badge-tag">Spot</span>
                                <span class="badge-dist">{dist}m</span>
                            </div>
                            <div class="place-addr-text">📍 {addr}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_btn:
                        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                        st.link_button(t["detail_btn"], item["place_url"], use_container_width=True)
            else:
                st.info("반경 3km 이내에 등록된 관광 명소 정보가 없습니다.")

        with tab_search:
            naver_blog_url = f"https://search.naver.com/search.naver?where=view&query={target_name}+맛집+여행"
            google_search_url = f"https://www.google.com/search?q={target_name}+restaurants+travel"
            sc1, sc2 = st.columns(2)
            with sc1:
                st.link_button(t["naver_blog"], naver_blog_url, use_container_width=True)
            with sc2:
                st.link_button("🔵 Google 검색", google_search_url, use_container_width=True)

    else:
        clean_name = target_name.split("(")[0].strip()
        ov_foods = [
            {"name": f"{clean_name} 트립어드바이저 1위 맛집", "category": "현지 맛집", "dist": "중심부", "addr": f"{clean_name} Central", "url": f"https://www.google.com/maps/search/{clean_name}+best+restaurants"},
            {"name": f"{clean_name} 로컬 전통 다이닝", "category": "전통 미식", "dist": "도보 5분", "addr": f"{clean_name} Downtown", "url": f"https://www.google.com/maps/search/{clean_name}+local+dining"},
            {"name": f"{clean_name} 감성 베이커리 & 카페", "category": "디저트/카페", "dist": "350m", "addr": f"{clean_name} Old Town", "url": f"https://www.google.com/maps/search/{clean_name}+cafe"}
        ]
        ov_tours = [
            {"name": f"{clean_name} 대표 랜드마크 스퀘어", "category": "명소/광장", "dist": "200m", "addr": f"{clean_name} Main Square", "url": f"https://www.google.com/maps/search/{clean_name}+tourist+attractions"},
            {"name": f"{clean_name} 시립 미술관 & 박물관", "category": "문화예술", "dist": "800m", "addr": f"{clean_name} Museum Area", "url": f"https://www.google.com/maps/search/{clean_name}+museum"},
            {"name": f"{clean_name} 파노라마 전망대", "category": "야경/전망", "dist": "1.2km", "addr": f"{clean_name} Viewpoint", "url": f"https://www.google.com/maps/search/{clean_name}+viewpoint"}
        ]

        with tab_food:
            for item in ov_foods:
                c_info, c_btn = st.columns([4.2, 1.2])
                with c_info:
                    st.markdown(f"""
                    <div class="premium-card">
                        <div>
                            <span class="place-name-text">{item['name']}</span>
                            <span class="badge-tag">{item['category']}</span>
                            <span class="badge-dist">{item['dist']}</span>
                        </div>
                        <div class="place-addr-text">📍 {item['addr']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_btn:
                    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                    st.link_button(t["review_btn"], item["url"], use_container_width=True)

        with tab_tour:
            for item in ov_tours:
                c_info, c_btn = st.columns([4.2, 1.2])
                with c_info:
                    st.markdown(f"""
                    <div class="premium-card">
                        <div>
                            <span class="place-name-text">{item['name']}</span>
                            <span class="badge-tag">{item['category']}</span>
                            <span class="badge-dist">{item['dist']}</span>
                        </div>
                        <div class="place-addr-text">📍 {item['addr']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_btn:
                    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                    st.link_button(t["detail_btn"], item["url"], use_container_width=True)

        with tab_search:
            clean_kw = target_name.split("(")[0].strip()
            g_maps_food_url = f"https://www.google.com/maps/search/{clean_kw}+restaurants"
            g_maps_attract_url = f"https://www.google.com/maps/search/{clean_kw}+tourist+attractions"
            tripadvisor_url = f"https://www.tripadvisor.com/Search?q={clean_kw}"
            naver_overseas_url = f"https://search.naver.com/search.naver?where=view&query={clean_kw}+여행+맛집"

            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.link_button(t["google_food"], g_maps_food_url, use_container_width=True)
            with sc2:
                st.link_button(t["google_tour"], g_maps_attract_url, use_container_width=True)
            with sc3:
                st.link_button(t["tripadvisor"], tripadvisor_url, use_container_width=True)
            with sc4:
                st.link_button(t["naver_blog"], naver_overseas_url, use_container_width=True)

else:
    st.info("👈 왼쪽 사이드바에서 원하는 목적지를 선택하거나 검색해 보세요!")