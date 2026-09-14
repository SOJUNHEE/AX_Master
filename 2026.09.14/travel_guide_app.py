import os
import re
from pathlib import Path
from dotenv import load_dotenv
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# 0. 라이브러리 안전 임포트
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
# 2. 다국어(i18n) 및 글로벌 메타데이터
# -----------------------------------------------------------------------------
I18N = {
    "ko": {
        "title": "🧭 스마트 글로벌 트래블 매니저",
        "subtitle": "전 세계 도시 & 국내 전역 실시간 위치 기반 날씨·환율·명소 원스톱 가이드",
        "weather_tab": "🌤️ 현지 실시간 날씨",
        "fx_tab": "💱 전 세계 실시간 환율",
        "feels_like": "체감 온도",
        "humidity": "습도",
        "wind": "풍속",
        "travel_tip": "💡 오늘의 여행 팁",
        "tip_rain": "☔ 비 예보가 있습니다. 접이식 우산을 챙기세요.",
        "tip_hot": "☀️ 무더운 날씨입니다. 충분한 수분을 섭취하세요.",
        "tip_cold": "🧣 쌀쌀한 날씨입니다. 따뜻한 외투를 준비하세요.",
        "tip_good": "🚶 야외 여행과 시내 투어를 즐기기에 쾌적한 날씨입니다.",
        "calc_title": "💱 출발국 ⇄ 현지 통화 스마트 환전 계산",
        "amt_label": "환전할 금액",
        "res_label": "환전 수령 예상 금액",
        "rate_label": "기준 환율",
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
        "subtitle": "Real-time location, weather, exchange rate & local spots guide worldwide",
        "weather_tab": "🌤️ Live Weather",
        "fx_tab": "💱 Live Currency FX",
        "feels_like": "Feels Like",
        "humidity": "Humidity",
        "wind": "Wind Speed",
        "travel_tip": "💡 Travel Tip",
        "tip_rain": "☔ Rain expected. Don't forget your umbrella.",
        "tip_hot": "☀️ Very warm. Stay hydrated while exploring.",
        "tip_cold": "🧣 Chilly weather. Dress warmly.",
        "tip_good": "🚶 Perfect weather for walking and outdoor sightseeing.",
        "calc_title": "💱 Smart Currency Converter",
        "amt_label": "Amount to convert",
        "res_label": "Converted Amount",
        "rate_label": "Exchange Rate",
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
        "subtitle": "全世界の都市と韓国全域のリアルタイム天気・為替・観光地ワンストップガイド",
        "weather_tab": "🌤️ 現地のリアルタイム天気",
        "fx_tab": "💱 世界為替レート計算機",
        "feels_like": "体感温度",
        "humidity": "湿度",
        "wind": "風速",
        "travel_tip": "💡 旅行アドバイス",
        "tip_rain": "☔ 雨の予報です。折りたたみ傘をお持ちください。",
        "tip_hot": "☀️ 暑い日です。水分補給をしっかり行ってください。",
        "tip_cold": "🧣 肌寒い天気です。暖かい上着をご用意ください。",
        "tip_good": "🚶 散歩や市内観光に最適な快適な天気です。",
        "calc_title": "💱 自動為替計算",
        "amt_label": "換金する金額",
        "res_label": "受取予想金額",
        "rate_label": "基準為替レート",
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
    "CAD": "캐나다 달러 (CAD)", "CHF": "스위스 프랑 (CHF)", "PHP": "필리핀 페소 (PHP)", "MYR": "말레이시아 링깃 (MYR)",
    "IDR": "인도네시아 루피아 (IDR)"
}

# -----------------------------------------------------------------------------
# 3. 여행 감성 폰트(Pretendard) + 고시인성 스타일 CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&display=swap');

    .stApp {
        background-color: #f8fafc !important;
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
        font-size: 0.95rem !important;
        color: #64748b !important;
        margin-bottom: 1.5rem !important;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
    }
    section[data-testid="stSidebar"] * {
        color: #0f172a !important;
    }

    .target-banner-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 22px 28px;
        color: #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 20px;
    }
    .target-banner-name {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        margin-bottom: 6px !important;
    }
    .target-banner-addr {
        font-size: 0.95rem !important;
        color: #94a3b8 !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* 이미지 규격 및 둥근 모서리 통일 */
    [data-testid="stImage"] img {
        height: 220px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
    }

    [data-testid="stImageCaption"] {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        text-align: center !important;
        margin-top: 6px !important;
    }

    .premium-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
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
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 20px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f1f5f9 !important;
        border-radius: 12px !important;
        padding: 5px !important;
        gap: 6px !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.98rem !important;
        font-weight: 700 !important;
        color: #64748b !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
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
# 5. 엄선된 랜드마크 & 명칭(캡션) 매핑 이미지 DB
# -----------------------------------------------------------------------------
CURATED_CITY_IMAGES = {
    "중국": [
        {"name": "만리장성 (Great Wall of China)", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=900&q=80"},
        {"name": "자금성 (Forbidden City)", "url": "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?auto=format&fit=crop&w=900&q=80"},
        {"name": "상하이 와이탄 (The Bund Shanghai)", "url": "https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?auto=format&fit=crop&w=900&q=80"}
    ],
    "베이징": [
        {"name": "만리장성 (Great Wall of China)", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=900&q=80"},
        {"name": "자금성 (The Palace Museum)", "url": "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?auto=format&fit=crop&w=900&q=80"},
        {"name": "이화원 & 천단공원 (Summer Palace)", "url": "https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?auto=format&fit=crop&w=900&q=80"}
    ],
    "상하이": [
        {"name": "상하이 와이탄 야경 (The Bund)", "url": "https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?auto=format&fit=crop&w=900&q=80"},
        {"name": "동방명주 & 푸둥 스카이라인", "url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80"},
        {"name": "예원 전통 정원 (Yuyuan Garden)", "url": "https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?auto=format&fit=crop&w=900&q=80"}
    ],
    "도쿄": [
        {"name": "도쿄 타워 (Tokyo Tower)", "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=900&q=80"},
        {"name": "시부야 스크램블 교차로", "url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=900&q=80"},
        {"name": "센소지 아사쿠사 전통 사찰", "url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=900&q=80"}
    ],
    "파리": [
        {"name": "에펠탑 (Tour Eiffel)", "url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=900&q=80"},
        {"name": "루브르 박물관 (Musée du Louvre)", "url": "https://images.unsplash.com/photo-1550340499-a6c0f083dcb4?auto=format&fit=crop&w=900&q=80"},
        {"name": "개선문 & 샹젤리제 거리", "url": "https://images.unsplash.com/photo-1522093007470-ee8db030f9ec?auto=format&fit=crop&w=900&q=80"}
    ],
    "방콕": [
        {"name": "왓 아룬 새벽 사원 (Wat Arun)", "url": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=900&q=80"},
        {"name": "방콕 왕궁 (The Grand Palace)", "url": "https://images.unsplash.com/photo-1563492065599-3520f775eeed?auto=format&fit=crop&w=900&q=80"},
        {"name": "왓 포 거대 와불상 사원", "url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=900&q=80"}
    ],
    "뉴욕": [
        {"name": "타임스 스퀘어 (Times Square)", "url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=900&q=80"},
        {"name": "맨해튼 스카이라인 & 센트럴 파크", "url": "https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=900&q=80"},
        {"name": "브루클린 브릿지 (Brooklyn Bridge)", "url": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=900&q=80"}
    ],
    "다낭": [
        {"name": "바나힐 골든 브릿지 (Golden Bridge)", "url": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=900&q=80"},
        {"name": "미케 비치 (My Khe Beach)", "url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=900&q=80"},
        {"name": "오행산 마블 마운틴 (Marble Mountains)", "url": "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=900&q=80"}
    ],
    "런던": [
        {"name": "빅 벤 & 국회의사당 (Big Ben)", "url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=900&q=80"},
        {"name": "런던 아이 (London Eye)", "url": "https://images.unsplash.com/photo-1526129318478-62ed807ebdf9?auto=format&fit=crop&w=900&q=80"},
        {"name": "타워 브리지 (Tower Bridge)", "url": "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?auto=format&fit=crop&w=900&q=80"}
    ],
    "서울": [
        {"name": "경복궁 근정전 (Gyeongbokgung)", "url": "https://images.unsplash.com/photo-1538485399081-7191377e8241?auto=format&fit=crop&w=900&q=80"},
        {"name": "N서울타워 & 남산 야경", "url": "https://images.unsplash.com/photo-1578637387939-43c525ec9001?auto=format&fit=crop&w=900&q=80"},
        {"name": "북촌 한옥마을 전통 거리", "url": "https://images.unsplash.com/photo-1517154421773-0529f29ea451?auto=format&fit=crop&w=900&q=80"}
    ]
}

def get_wikipedia_thumbnail(query_text: str):
    clean_title = re.sub(r"\(.*?\)", "", query_text).strip()
    try:
        url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{clean_title}"
        res = requests.get(url, headers={"User-Agent": "TravelGuideApp/1.0"}, timeout=4)
        if res.status_code == 200:
            data = res.json()
            if "thumbnail" in data and "source" in data["thumbnail"]:
                return data["thumbnail"]["source"], data.get("title", clean_title)
    except Exception:
        pass
    return None, None

def get_nearby_tour_or_food_images(place_name: str, kakao_key: str, size: int = 3):
    for city_key, img_list in CURATED_CITY_IMAGES.items():
        if city_key in place_name:
            return img_list[:size]

    results = []
    clean_name = re.sub(r"\(.*?\)", "", place_name).strip()

    wiki_img, wiki_title = get_wikipedia_thumbnail(place_name)
    if wiki_img:
        results.append({"name": f"{clean_name} 전경 ({wiki_title})", "url": wiki_img})

    if kakao_key:
        try:
            url = "https://dapi.kakao.com/v2/search/image"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {"query": f"{clean_name} 풍경", "size": size, "sort": "accuracy"}
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
        {"name": f"{clean_name} 대표 랜드마크", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=900&q=80"},
        {"name": f"{clean_name} 도심 풍경", "url": "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?auto=format&fit=crop&w=900&q=80"},
        {"name": f"{clean_name} 전통 & 미식 명소", "url": "https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?auto=format&fit=crop&w=900&q=80"}
    ]
    for fb in general_fallbacks:
        if len(results) >= size:
            break
        results.append(fb)

    return results[:size]

# -----------------------------------------------------------------------------
# 6. 통화 및 국가 코드 스마트 판별
# -----------------------------------------------------------------------------
def detect_currency_and_cc(name_str: str):
    q = name_str.lower()
    mapping = [
        (["중국", "베이징", "상하이", "칭다오", "광저우", "china", "beijing", "shanghai"], ("CNY", "cn")),
        (["도쿄", "일본", "오사카", "교토", "후쿠오카", "tokyo", "japan", "osaka", "fukuoka"], ("JPY", "jp")),
        (["방콕", "태국", "푸켓", "치앙마이", "bangkok", "thailand", "phuket"], ("THB", "th")),
        (["파리", "프랑스", "paris", "france", "니스", "nice"], ("EUR", "fr")),
        (["뉴욕", "미국", "워싱턴", "샌프란시스코", "new york", "usa", "los angeles", "la"], ("USD", "us")),
        (["다낭", "베트남", "하노이", "호치민", "danang", "vietnam", "hanoi"], ("VND", "vn")),
        (["런던", "영국", "london", "uk", "잉글랜드"], ("GBP", "gb")),
        (["시드니", "호주", "멜버른", "sydney", "australia"], ("AUD", "au")),
        (["싱가포르", "singapore"], ("SGD", "sg")),
        (["타이베이", "대만", "taiwan", "taipei"], ("TWD", "tw")),
        (["홍콩", "hong kong"], ("HKD", "hk")),
        (["취리히", "스위스", "인터라켄", "switzerland", "zurich"], ("CHF", "ch"))
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
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "accept-language": "ko,en"
    }
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
    st.markdown("### 🌐 **언어 / Language**")
    lang_mode = st.selectbox("UI 언어 선택", ["한국어 (KO)", "English (EN)", "日本語 (JA)"])

    st.markdown("---")
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
                    st.warning(f"반경 {search_radius}m 내 검색 결과가 없습니다.")

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
            global_query = st.text_input("해외 도시/랜드마크 입력 (한글/영문)", placeholder="예: 중국, 베이징, 도쿄, 오사카, 방콕, 파리")
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
                else:
                    st.warning(f"'{global_query}' 관련 해외 위치를 찾지 못했습니다.")

# 언어 코드 확정
if lang_mode == "한국어 (KO)":
    active_lang = "ko"
elif lang_mode == "English (EN)":
    active_lang = "en"
else:
    active_lang = "ja"

t = I18N.get(active_lang, I18N["ko"])

# -----------------------------------------------------------------------------
# 8. 본문 레이아웃 (명칭 기반 갤러리 + 지도 + 날씨/환율 + 맛집/명소)
# -----------------------------------------------------------------------------
st.markdown(f'<div class="main-header-title">{t["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-header-sub">{t["subtitle"]}</div>', unsafe_allow_html=True)

if target_lat and target_lon:
    region_badge = "✈️ Global" if is_overseas else "🇰🇷 Domestic"
    st.markdown(f"""
    <div class="target-banner-card">
        <div class="target-banner-name">[{region_badge}] {target_name}</div>
        <div class="target-banner-addr"><span>Location / 주소:</span> {target_addr}</div>
    </div>
    """, unsafe_allow_html=True)

    # 🌟 각 사진의 실제 명칭이 캡션으로 출력되는 고품질 갤러리 (use_container_width 적용)
    place_images = get_nearby_tour_or_food_images(target_name, KAKAO_REST_KEY, size=3)
    if place_images:
        img_cols = st.columns(len(place_images))
        for idx, item in enumerate(place_images):
            with img_cols[idx]:
                st.image(item["url"], use_container_width=True, caption=f"📍 {item['name']}")
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    col_map, col_right = st.columns([6, 4], gap="large")

    # 8-1. [좌측] 인터랙티브 지도
    with col_map:
        st.markdown("#### 🗺️ 인터랙티브 여행 지도")
        st.caption("💡 마우스 휠 스크롤 또는 좌측 상단 [+], [-] 버튼으로 자유롭게 확대/축소할 수 있습니다.")

        if HAS_FOLIUM:
            m = folium.Map(location=[target_lat, target_lon], zoom_start=15)
            folium.Marker(
                [target_lat, target_lon],
                popup=target_name,
                tooltip=target_name,
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
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

    # 8-2. [우측] 실시간 날씨 & 전 세계 통화 계산기
    with col_right:
        tab_weather, tab_fx_quick = st.tabs([t["weather_tab"], t["fx_tab"]])

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

            calc_amt = st.number_input(
                f"{t['amt_label']} ({from_cur})", 
                min_value=0.0, 
                value=100000.0 if from_cur == "KRW" else 100.0, 
                step=1000.0, 
                format="%.2f",
                key="quick_amt_input"
            )

            from_usd_rate = rates_dict.get(from_cur, 1.0)
            to_usd_rate = rates_dict.get(to_cur, 1.0)

            exchange_rate = to_usd_rate / from_usd_rate if from_usd_rate > 0 else 0
            reverse_rate = from_usd_rate / to_usd_rate if to_usd_rate > 0 else 0
            converted_result = calc_amt * exchange_rate

            st.markdown(f"""
            <div class="glass-metric-card" style="margin-top: 10px;">
                <div style="font-size: 0.85rem; color: #64748b; font-weight: 700;">{t['res_label']} ({to_cur})</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #2563eb; margin: 4px 0;">{converted_result:,.2f} {to_cur}</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">
                    • 1 {from_cur} = {exchange_rate:,.4f} {to_cur}<br>
                    • 1 {to_cur} = <b>{reverse_rate:,.2f} {from_cur}</b> (여행 체감 물가)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 8-3. 주변 맛집/명소/리뷰 섹션 (국내 & 해외 통합 카드 UI)
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
    st.info("👈 왼쪽 사이드바에서 원하는 목적지를 선택하거나 검색해 보세요.")