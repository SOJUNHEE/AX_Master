# 날씨 API 실습
# OpenWeatherMap 현재 날씨 API로 특정 도시의 날씨를 가져와 출력한다
# 사전준비 OpenWeatherMap 회원 가입 후 API 발급
# pip install requests python-dotenv
# .env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은_API_KEY  -> 깃에 안올림
# .env.example OPENWEATHER_API_KEY=your_KEY -> 깃에 올림 (남에게 본인의 api 키 주지 않고 본인껄로 작업)
# .env.example를 받아서 .env로 파일명 변경 후 자기 API를 채운다.
# API 키를 직접 노출 해선 안된다.


import os
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 1. 상위 폴더의 .env 로드 및 키 조회 함수 (로컬/클라우드 환경 분기)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def get_secret_key(key_name: str):
    """로컬 .env 환경 변수를 먼저 확인하고, 없으면 Streamlit Secrets를 안전하게 조회합니다."""
    # 1순위: 로컬 .env
    val = os.getenv(key_name)
    if val:
        return val
    # 2순위: Streamlit Cloud (secrets.toml이 없어도 에러 방지)
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return None

WEATHER_KEY = get_secret_key("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_secret_key("EXCHANGE_RATE_API_KEY")

# -----------------------------------------------------------------------------
# 2. 날씨 API 요청 함수
# -----------------------------------------------------------------------------
def get_current_weather(city_name: str, api_key: str):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name.strip(),
        "appid": api_key,
        "units": "metric",  # 섭씨
        "lang": "kr",        # 한국어 상태 설명
    }
    try:
        res = requests.get(base_url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json(), None
        elif res.status_code == 404:
            return None, f"'{city_name}' 도시를 찾을 수 없습니다."
        elif res.status_code == 401:
            return None, "날씨 API 키 인증에 실패했습니다. 키를 확인하세요."
        else:
            return None, f"날씨 API 오류 ({res.status_code})"
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 오류: {e}"

# -----------------------------------------------------------------------------
# 3. 환율 API 요청 함수 (30분 캐싱)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=1800)
def get_exchange_rates(api_key: str):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {}), None
            return None, data.get("error-type", "환율 데이터를 가져올 수 없습니다.")
        elif res.status_code == 401:
            return None, "환율 API 키 인증에 실패했습니다."
        else:
            return None, f"환율 API 오류 ({res.status_code})"
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 오류: {e}"

# 국가 코드 -> 통화 코드 매핑
COUNTRY_CURRENCY = {
    "KR": "KRW",
    "US": "USD",
    "JP": "JPY",
    "GB": "GBP",
    "FR": "EUR",
    "DE": "EUR",
    "IT": "EUR",
    "ES": "EUR",
    "CN": "CNY",
    "AU": "AUD",
    "CA": "CAD",
    "VN": "VND",
    "TH": "THB",
    "SG": "SGD",
}

# -----------------------------------------------------------------------------
# 4. Streamlit UI
# -----------------------------------------------------------------------------
st.set_page_config(page_title="실시간 날씨 & 환율", page_icon="🌤️", layout="wide")

st.title("🌤️ 실시간 날씨 & 💱 환율 대시보드")
st.write("목록을 클릭하여 원하는 도시를 선택하면 날씨와 관련 환율을 함께 확인합니다.")

# API Key 유효성 검사 안내
if not WEATHER_KEY:
    st.error(f"⚠️ `OPENWEATHER_API_KEY`를 찾을 수 없습니다. 상위 폴더의 `.env` 파일을 확인하세요. (확인 경로: `{env_path}`)")
    st.stop()

# 드롭다운 리스트 옵션
city_options = {
    "서울 (Seoul)": "Seoul",
    "도쿄 (Tokyo)": "Tokyo",
    "뉴욕 (New York)": "New York",
    "런던 (London)": "London",
    "파리 (Paris)": "Paris",
    "시드니 (Sydney)": "Sydney",
    "방콕 (Bangkok)": "Bangkok",
    "싱가포르 (Singapore)": "Singapore",
    "직접 입력": "CUSTOM",
}

selected_label = st.selectbox("도시 선택", options=list(city_options.keys()), index=0)

if selected_label == "직접 입력":
    target_city = st.text_input("도시 영문 이름 (예: Berlin, Toronto)", value="")
else:
    target_city = city_options[selected_label]

st.divider()

# -----------------------------------------------------------------------------
# 5. 결과 영역 (좌: 날씨 / 우: 환율)
# -----------------------------------------------------------------------------
if target_city:
    col_weather, col_exchange = st.columns(2, gap="medium")

    # 5-1. [왼쪽] 날씨 카드
    with col_weather:
        st.subheader("🌤️ 현재 날씨")
        with st.spinner("날씨 데이터를 불러오는 중..."):
            w_data, w_error = get_current_weather(target_city, WEATHER_KEY)

        target_country = "KR"

        if w_error:
            st.error(w_error)
        elif w_data:
            desc = w_data["weather"][0]["description"]
            icon_code = w_data["weather"][0]["icon"]
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            temp = w_data["main"]["temp"]
            feels_like = w_data["main"]["feels_like"]
            humidity = w_data["main"]["humidity"]
            wind_speed = w_data["wind"]["speed"]
            target_country = w_data["sys"].get("country", "KR")

            with st.container(border=True):
                c_icon, c_info = st.columns([1, 4])
                with c_icon:
                    st.image(icon_url, width=80)
                with c_info:
                    st.markdown(f"### {w_data['name']} ({target_country})")
                    st.write(f"상태: **{desc}**")

                st.divider()
                m1, m2, m3 = st.columns(3)
                m1.metric("기온", f"{temp:.1f} °C", delta=f"체감 {feels_like:.1f} °C")
                m2.metric("습도", f"{humidity} %")
                m3.metric("풍속", f"{wind_speed} m/s")

    # 5-2. [오른쪽] 환율 카드
    with col_exchange:
        st.subheader("💱 실시간 환율 (KRW 기준)")
        if not EXCHANGE_KEY:
            st.warning("⚠️ `EXCHANGE_RATE_API_KEY`가 없습니다. `.env` 파일에 키를 등록하면 환율이 표시됩니다.")
        else:
            with st.spinner("환율 데이터를 불러오는 중..."):
                rates, ex_error = get_exchange_rates(EXCHANGE_KEY)

            if ex_error:
                st.error(ex_error)
            elif rates:
                krw_per_usd = rates.get("KRW", 1.0)
                local_curr = COUNTRY_CURRENCY.get(target_country, "USD")
                local_per_usd = rates.get(local_curr, 1.0)

                with st.container(border=True):
                    # 선택 국가 통화 환율 환산
                    if local_curr != "KRW" and local_per_usd > 0:
                        krw_per_local = krw_per_usd / local_per_usd
                        if local_curr in ["JPY", "VND"]:
                            st.metric(f"100 {local_curr}", f"{krw_per_local * 100:,.2f} 원")
                        else:
                            st.metric(f"1 {local_curr}", f"{krw_per_local:,.2f} 원")
                    else:
                        st.metric("기준 통화", "대한민국 원 (KRW)")

                    st.divider()
                    st.caption("📌 주요 글로벌 환율 (KRW)")
                    em1, em2, em3 = st.columns(3)
                    em1.metric("1 USD", f"{krw_per_usd:,.1f} 원")
                    jpy_krw = (krw_per_usd / rates.get("JPY", 1.0)) * 100
                    em2.metric("100 JPY", f"{jpy_krw:,.1f} 원")
                    eur_krw = krw_per_usd / rates.get("EUR", 1.0)
                    em3.metric("1 EUR", f"{eur_krw:,.1f} 원")