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

st.set_page_config(page_title="Global Smart Travel Guide", page_icon="✈️", layout="wide")

if not KAKAO_REST_KEY:
    st.error("⚠️ `KAKAO_MAP_KEY` (카카오 REST API 키)를 설정해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 다국어(i18n) & 전 세계 국가 코드 ⇄ 통화 매핑
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
        "travel_tip": "💡 현지 여행 팁",
        "tip_rain": "☔ 비 예보가 있습니다. 접이식 우산을 챙기세요.",
        "tip_hot": "☀️ 무더운 날씨입니다. 충분한 수분을 섭취하세요.",
        "tip_cold": "🧣 쌀쌀한 날씨입니다. 따뜻한 외투를 준비하세요.",
        "tip_good": "🚶 야외 여행과 시내 투어를 즐기기에 쾌적한 날씨입니다.",
        "calc_title": "💱 출발국 ⇄ 현지 통화 자동 환전",
        "amt_label": "환전할 금액",
        "res_label": "환전 수령 예상 금액",
        "rate_label": "기준 환율",
        "food_tab": "🍴 주변 인기 맛집",
        "tour_tab": "🏛️ 주변 관광 명소",
        "portal_tab": "🔍 블로그/포털 검색",
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
        "weather_tab": "🌤️ Local Live Weather",
        "fx_tab": "💱 Global Live FX",
        "feels_like": "Feels Like",
        "humidity": "Humidity",
        "wind": "Wind Speed",
        "travel_tip": "💡 Travel Tip",
        "tip_rain": "☔ Rain expected. Don't forget your umbrella.",
        "tip_hot": "☀️ Very warm. Stay hydrated while exploring.",
        "tip_cold": "🧣 Chilly weather. Dress warmly.",
        "tip_good": "🚶 Perfect weather for walking and outdoor sightseeing.",
        "calc_title": "💱 Global Currency Converter",
        "amt_label": "Amount to convert",
        "res_label": "Converted Amount",
        "rate_label": "Exchange Rate",
        "food_tab": "🍴 Popular Restaurants",
        "tour_tab": "🏛️ Tourist Attractions",
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
    },
    "zh": {
        "title": "🧭 智能全球旅行指南",
        "subtitle": "全球城市与韩国实时天气、汇率换算与旅游景点一站式向导",
        "weather_tab": "🌤️ 当地实时天气",
        "fx_tab": "💱 全球实时汇率",
        "feels_like": "体感温度",
        "humidity": "湿度",
        "wind": "风速",
        "travel_tip": "💡 旅行贴士",
        "tip_rain": "☔ 有雨，请随身携带雨伞。",
        "tip_hot": "☀️ 天气炎热，请多补充水分。",
        "tip_cold": "🧣 天气较冷，请注意添衣保暖。",
        "tip_good": "🚶 天气舒适，非常适合漫步与户外游览。",
        "calc_title": "💱 实时汇率计算",
        "amt_label": "兑换金额",
        "res_label": "预计兑换金额",
        "rate_label": "参考汇率",
        "food_tab": "🍴 周边人气美食",
        "tour_tab": "🏛️ 周边热门景点",
        "portal_tab": "🔍 旅行游记与搜索",
        "review_btn": "菜单 / 评价",
        "detail_btn": "景点详情",
        "google_food": "🍽️ 谷歌热门美食",
        "google_tour": "🏛️ 谷歌必游景点",
        "tripadvisor": "🦉 猫途鹰 TripAdvisor",
        "naver_blog": "🟢 旅行游记搜索"
    },
    "fr": {
        "title": "🧭 Guide de Voyage Intelligent",
        "subtitle": "Météo en direct, taux de change et lieux incontournables dans le monde entier",
        "weather_tab": "🌤️ Météo Locale en Direct",
        "fx_tab": "💱 Taux de Change Mondial",
        "feels_like": "Température ressentie",
        "humidity": "Humidité",
        "wind": "Vitesse du vent",
        "travel_tip": "💡 Conseil de Voyage",
        "tip_rain": "☔ Pluie prévue. N'oubliez pas votre parapluie.",
        "tip_hot": "☀️ Temps chaud. Pensez à bien vous hydrater.",
        "tip_cold": "🧣 Temps frais. Prévoyez des vêtements chauds.",
        "tip_good": "🚶 Temps idéal pour les visites en plein air.",
        "calc_title": "💱 Convertisseur de Devises",
        "amt_label": "Montant à convertir",
        "res_label": "Montant converti",
        "rate_label": "Taux de change",
        "food_tab": "🍴 Restaurants populaires",
        "tour_tab": "🏛️ Attractions touristiques",
        "portal_tab": "🔍 Blogs et Recherche",
        "review_btn": "Avis / Menu",
        "detail_btn": "Détails",
        "google_food": "🍽️ Restaurants Google",
        "google_tour": "🏛️ Attractions Google",
        "tripadvisor": "🦉 Avis TripAdvisor",
        "naver_blog": "🟢 Recherche de blogs"
    },
    "vi": {
        "title": "🧭 Hướng Dẫn Du Lịch Toàn Cầu Thông Minh",
        "subtitle": "Thời tiết thực tế, tỷ giá tiền tệ toàn cầu và các điểm đến hàng đầu",
        "weather_tab": "🌤️ Thời Tiết Thực Tế",
        "fx_tab": "💱 Tỷ Giá Hối Đoái Toàn Cầu",
        "feels_like": "Nhiệt độ cảm nhận",
        "humidity": "Độ ẩm",
        "wind": "Tốc độ gió",
        "travel_tip": "💡 Lời khuyên du lịch",
        "tip_rain": "☔ Dự báo có mưa. Đừng quên mang theo ô.",
        "tip_hot": "☀️ Thời tiết nắng nóng. Hãy uống đủ nước.",
        "tip_cold": "🧣 Trời lạnh. Hãy mặc ấm.",
        "tip_good": "🚶 Thời tiết tuyệt vời cho các hoạt động ngoài trời.",
        "calc_title": "💱 Quy đổi Tiền tệ",
        "amt_label": "Số tiền cần đổi",
        "res_label": "Số tiền quy đổi",
        "rate_label": "Tỷ giá tham khảo",
        "food_tab": "🍴 Ẩm thực nổi tiếng",
        "tour_tab": "🏛️ Địa điểm du lịch",
        "portal_tab": "🔍 Đánh giá du lịch",
        "review_btn": "Thực đơn / Đánh giá",
        "detail_btn": "Chi tiết",
        "google_food": "🍽️ Quán ăn nổi tiếng Google",
        "google_tour": "🏛️ Điểm tham quan Google",
        "tripadvisor": "🦉 Đánh giá TripAdvisor",
        "naver_blog": "🟢 Tìm kiếm bài viết"
    }
}

GLOBAL_COUNTRY_DATA = {
    "kr": ("KRW", "ko"), "us": ("USD", "en"), "jp": ("JPY", "ja"), "gb": ("GBP", "en"),
    "fr": ("EUR", "fr"), "de": ("EUR", "en"), "it": ("EUR", "en"), "es": ("EUR", "en"),
    "pt": ("EUR", "en"), "nl": ("EUR", "en"), "be": ("EUR", "fr"), "at": ("EUR", "en"),
    "gr": ("EUR", "en"), "ie": ("EUR", "en"), "fi": ("EUR", "en"), "vn": ("VND", "vi"),
    "cn": ("CNY", "zh"), "tw": ("TWD", "zh"), "hk": ("HKD", "zh"), "mo": ("MOP", "zh"),
    "th": ("THB", "en"), "ph": ("PHP", "en"), "sg": ("SGD", "en"), "my": ("MYR", "en"),
    "id": ("IDR", "en"), "au": ("AUD", "en"), "ca": ("CAD", "en"), "nz": ("NZD", "en"),
    "ch": ("CHF", "en"), "se": ("SEK", "en"), "no": ("NOK", "en"), "dk": ("DKK", "en"),
    "ae": ("AED", "en"), "sa": ("SAR", "en"), "tr": ("TRY", "en"), "eg": ("EGP", "en"),
    "in": ("INR", "en"), "br": ("BRL", "en"), "mx": ("MXN", "en"), "za": ("ZAR", "en")
}

GLOBAL_CURRENCY_NAMES = {
    "KRW": "대한민국 원 (KRW)", "USD": "미국 달러 (USD)", "JPY": "일본 엔 (JPY)", "EUR": "유로존 유로 (EUR)",
    "GBP": "영국 파운드 (GBP)", "CNY": "중국 위안 (CNY)", "VND": "베트남 동 (VND)", "THB": "태국 바트 (THB)",
    "TWD": "대만 달러 (TWD)", "HKD": "홍콩 달러 (HKD)", "SGD": "싱가포르 달러 (SGD)", "AUD": "호주 달러 (AUD)",
    "CAD": "캐나다 달러 (CAD)", "CHF": "스위스 프랑 (CHF)", "PHP": "필리핀 페소 (PHP)", "MYR": "말레이시아 링깃 (MYR)",
    "IDR": "인도네시아 루피아 (IDR)", "NZD": "뉴질랜드 달러 (NZD)", "AED": "UAE 디르함 (AED)", "SAR": "사우디 리얄 (SAR)",
    "TRY": "튀르키예 리라 (TRY)", "INR": "인도 루피 (INR)", "BRL": "브라질 헤알 (BRL)", "MXN": "멕시코 페소 (MXN)",
    "SEK": "스웨덴 크로나 (SEK)", "NOK": "노르웨이 크로네 (NOK)", "DKK": "덴마크 크로네 (DKK)"
}

# -----------------------------------------------------------------------------
# 3. 고시인성 프리미엄 UI CSS
# -----------------------------------------------------------------------------
modern_clean_css = """
<style>
    .stApp {
        background-color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", Roboto, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
    }
    section[data-testid="stSidebar"] * {
        color: #0f172a !important;
    }
    .main-header-title {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.3rem !important;
    }
    .main-header-sub {
        font-size: 0.95rem !important;
        color: #64748b !important;
        margin-bottom: 1.5rem !important;
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
    .premium-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    .place-name-text {
        font-size: 1.2rem !important;
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
        font-size: 1.0rem !important;
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
    .stTextInput>div>div>input, .stSelectbox>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    @media (max-width: 768px) {
        .block-container { padding: 1.2rem 0.8rem !important; }
        .main-header-title { font-size: 1.6rem !important; }
        .target-banner-name { font-size: 1.3rem !important; }
    }
</style>
"""
st.markdown(modern_clean_css, unsafe_allow_html=True)

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
# 5. 검색 및 이미지 폴백 처리 함수
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

def search_global_place_osm(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "accept-language": "ko,en"
    }
    headers = {"User-Agent": "WorldWideTravelGuideStreamlit/1.0"}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=6)
        if res.status_code == 200:
            return res.json(), None
        return None, f"글로벌 검색 실패 ({res.status_code})"
    except Exception as e:
        return None, f"해외 네트워크 오류: {e}"

def get_nearby_tour_or_food_images(place_name: str, kakao_key: str, size: int = 3):
    """카카오 이미지 검색 실패 시 Unsplash 고화질 여행지 뷰로 폴백 제공"""
    url = "https://dapi.kakao.com/v2/search/image"
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    
    # 정제된 검색 쿼리 (가괄호 및 국가명 제거하여 정확도 상승)
    clean_query = place_name.split("(")[0].strip()
    params = {"query": f"{clean_query} 랜드마크 풍경", "size": size, "sort": "accuracy"}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=4)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            images = [doc["image_url"] for doc in docs if doc.get("image_url")]
            if images:
                return images[:size]
    except Exception:
        pass
    
    # 2차 검색 시도 (영문 키워드 조합)
    try:
        params2 = {"query": f"{clean_query} travel landscape", "size": size}
        res2 = requests.get(url, headers=headers, params=params2, timeout=4)
        if res2.status_code == 200:
            docs = res2.json().get("documents", [])
            images = [doc["image_url"] for doc in docs if doc.get("image_url")]
            if images:
                return images[:size]
    except Exception:
        pass

    # 최종 폴백: 언스플래시(Unsplash) 안정적인 여행지 샘플 이미지 반환
    fallback_images = [
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1503220317375-aaad61436b1b?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80"
    ]
    return fallback_images[:size]

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

def get_weather_by_coords(lat: float, lon: float, weather_key: str, lang: str = "kr"):
    if not weather_key:
        return None, "날씨 API 키(OPENWEATHER_API_KEY)가 등록되지 않았습니다."
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": weather_key, "units": "metric", "lang": lang}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json(), None
        return None, f"날씨 정보 호출 실패 ({res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

# -----------------------------------------------------------------------------
# 6. 사이드바: 다국어 및 목적지 탐색 (통화 정보 포함)
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
    st.markdown("### 🌐 **Language / 言語 / 언어**")
    lang_mode = st.selectbox("UI 언어 선택", ["한국어 (KO)", "English (EN)", "현지 여행지 언어 (Auto Local)"])

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
            search_query = st.text_input("국내 장소/주소 입력", placeholder="예: 부산역, 신림역, 해운대")
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
        global_mode = st.radio("해외 탐색 방식", ["해외 인기 명소", "전 세계 도시/명소 직접 검색"])

        if global_mode == "해외 인기 명소":
            overseas_presets = {k: v for k, v in preset_places.items() if v["is_overseas"]}
            selected_name = st.selectbox("해외 추천 도시", list(overseas_presets.keys()))
            target_name = selected_name
            target_lat = overseas_presets[selected_name]["lat"]
            target_lon = overseas_presets[selected_name]["lon"]
            target_addr = overseas_presets[selected_name]["address"]
            target_cc = overseas_presets[selected_name].get("cc", "us")
            auto_currency = overseas_presets[selected_name].get("currency", "USD")

        else:
            global_query = st.text_input("해외 도시/랜드마크 입력 (한글/영문)", placeholder="예: 방콕, 타이베이, 취리히, 시드니, 싱가포르, 로마")
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
                    target_cc = chosen_osm.get("address", {}).get("country_code", "us").lower()
                    
                    mapped_cur, _ = GLOBAL_COUNTRY_DATA.get(target_cc, ("USD", "en"))
                    auto_currency = mapped_cur if mapped_cur in rates_dict else "USD"
                else:
                    st.warning(f"'{global_query}' 관련 해외 위치를 찾지 못했습니다.")

# 언어 코드 결정
if lang_mode == "한국어 (KO)":
    active_lang = "ko"
elif lang_mode == "English (EN)":
    active_lang = "en"
else:
    _, local_code = GLOBAL_COUNTRY_DATA.get(target_cc, ("USD", "en"))
    active_lang = local_code if local_code in I18N else "en"

t = I18N.get(active_lang, I18N["en"])

# -----------------------------------------------------------------------------
# 7. 본문 메인 레이아웃
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

    with st.spinner("Fetching photos..."):
        place_images = get_nearby_tour_or_food_images(target_name, KAKAO_REST_KEY, size=3)

    if place_images:
        img_cols = st.columns(len(place_images))
        for idx, img_url in enumerate(place_images):
            with img_cols[idx]:
                st.image(img_url, width="stretch", caption=f"Local View {idx+1}")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_map, col_right = st.columns([6, 4], gap="large")

    # 7-1. [좌측] 인터랙티브 지도
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
                st.link_button("📍 카카오맵에서 보기", kakao_link, width="stretch")
            with btn_col2:
                st.link_button("🚗 카카오맵 길찾기", route_link, width="stretch")
        else:
            google_map_link = f"https://www.google.com/maps/search/?api=1&query={target_lat},{target_lon}"
            with btn_col1:
                st.link_button("🌐 구글 맵스 열기", google_map_link, width="stretch")
            with btn_col2:
                st.link_button("🧭 길찾기 (Google)", f"{google_map_link}&dirflg=d", width="stretch")

    # 7-2. [우측] 실시간 날씨 & 전 세계 통화 호환 환율 계산기 (글자 크기 및 레이아웃 최적화)
    with col_right:
        tab_weather, tab_fx_quick = st.tabs([t["weather_tab"], t["fx_tab"]])

        with tab_weather:
            weather_api_lang = "kr" if active_lang == "ko" else ("ja" if active_lang == "ja" else ("zh_cn" if active_lang == "zh" else ("fr" if active_lang == "fr" else ("vi" if active_lang == "vi" else "en"))))
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
                if "rain" in weather_desc.lower() or "비" in weather_desc or "雨" in weather_desc:
                    st.info(t["tip_rain"])
                elif temp >= 28:
                    st.warning(t["tip_hot"])
                elif temp <= 5:
                    st.info(t["tip_cold"])
                else:
                    st.success(t["tip_good"])

        with tab_fx_quick:
            # 🌟 레이아웃 및 폰트 크기 최적화로 찌그러짐 방지
            st.markdown(f"<div style='font-size: 1.05rem; font-weight: 800; color: #0f172a; margin-bottom: 8px;'>{t['calc_title']}</div>", unsafe_allow_html=True)

            # 🌟 해외 선택 시 해당 국가 통화로 확실히 매칭되도록 보정
            target_to_currency = auto_currency if auto_currency in all_supported_currencies else ("USD" if is_overseas else "KRW")
            try:
                to_default_idx = all_supported_currencies.index(target_to_currency)
            except ValueError:
                to_default_idx = 0

            def format_currency_label(code):
                return GLOBAL_CURRENCY_NAMES.get(code, f"{code} (전세계 공식 통화)")

            col_src, col_dst = st.columns(2)
            with col_src:
                from_cur = st.selectbox("From (출발)", all_supported_currencies, index=0, format_func=format_currency_label, key="quick_from_cur")
            with col_dst:
                to_cur = st.selectbox("To (현지 통화)", all_supported_currencies, index=to_default_idx, format_func=format_currency_label, key="quick_to_cur")

            calc_amt = st.number_input(
                f"{t['amt_label']} ({from_cur})", 
                min_value=0.0, 
                value=0.0, 
                step=1000.0, 
                format="%.2f",
                key="quick_amt_input"
            )

            from_usd_rate = rates_dict.get(from_cur, 1.0)
            to_usd_rate = rates_dict.get(to_cur, 1.0)

            exchange_rate = to_usd_rate / from_usd_rate if from_usd_rate > 0 else 0
            converted_result = calc_amt * exchange_rate

            st.markdown(f"""
            <div class="glass-metric-card" style="margin-top: 10px;">
                <div style="font-size: 0.85rem; color: #64748b; font-weight: 700;">{t['res_label']} ({to_cur})</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: #2563eb; margin: 4px 0;">{converted_result:,.2f} {to_cur}</div>
                <div style="font-size: 0.82rem; color: #475569;">{t['rate_label']}: 1 {from_cur} = {exchange_rate:,.4f} {to_cur}</div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 8. 주변 맛집/명소/리뷰 섹션
    # -------------------------------------------------------------------------
    st.divider()

    if not is_overseas:
        st.markdown(f"### 🍽️ **{target_name}** {t['food_tab']} & {t['tour_tab']}")
        tab_food, tab_tour, tab_search = st.tabs([t["food_tab"], t["tour_tab"], t["portal_tab"]])

        with tab_food:
            foods, _ = get_nearby_places_by_category("FD6", target_lat, target_lon, KAKAO_REST_KEY, radius=2000)
            if foods:
                for item in foods:
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
                        st.link_button(t["review_btn"], item["place_url"], width="stretch")
            else:
                st.info("No restaurants found within 2km.")

        with tab_tour:
            tours, _ = get_nearby_places_by_category("AT4", target_lat, target_lon, KAKAO_REST_KEY, radius=3000)
            if tours:
                for item in tours:
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
                        st.link_button(t["detail_btn"], item["place_url"], width="stretch")
            else:
                st.info("No tourist spots found within 3km.")

        with tab_search:
            naver_blog_url = f"https://search.naver.com/search.naver?where=view&query={target_name}+맛집+여행"
            google_search_url = f"https://www.google.com/search?q={target_name}+restaurants+travel"
            sc1, sc2 = st.columns(2)
            with sc1:
                st.link_button(t["naver_blog"], naver_blog_url, width="stretch")
            with sc2:
                st.link_button("🔵 Google Search", google_search_url, width="stretch")

    else:
        st.markdown(f"### 🌍 **{target_name}** Travel Platform Hub")
        g_maps_food_url = f"https://www.google.com/maps/search/{target_name}+restaurants"
        g_maps_attract_url = f"https://www.google.com/maps/search/{target_name}+tourist+attractions"
        tripadvisor_url = f"https://www.tripadvisor.com/Search?q={target_name}"
        naver_overseas_url = f"https://search.naver.com/search.naver?where=view&query={target_name}+여행+맛집"

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.link_button(t["google_food"], g_maps_food_url, width="stretch")
        with sc2:
            st.link_button(t["google_tour"], g_maps_attract_url, width="stretch")
        with sc3:
            st.link_button(t["tripadvisor"], tripadvisor_url, width="stretch")
        with sc4:
            st.link_button(t["naver_blog"], naver_overseas_url, width="stretch")

else:
    st.info("👈 Please select or search for a destination from the sidebar.")