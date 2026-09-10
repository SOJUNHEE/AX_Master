import base64
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 페이지 기본 설정 (와이드/모바일 자동 대응)
st.set_page_config(
    page_title="Trade MBTI | 나의 무역 직무 DNA 찾기",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. 커스텀 폰트 로드 (경로 자동 인식)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
title_font_path = os.path.join(BASE_DIR, "font_title.otf")
body_font_path = os.path.join(BASE_DIR, "font_body.otf")

title_font_base64 = ""
body_font_base64 = ""

if os.path.exists(title_font_path):
    with open(title_font_path, "rb") as f:
        title_font_base64 = base64.b64encode(f.read()).decode()

if os.path.exists(body_font_path):
    with open(body_font_path, "rb") as f:
        body_font_base64 = base64.b64encode(f.read()).decode()

# 3-1. 폰트 주입 (변수가 필요한 부분만 f-string 처리)
st.markdown(
    f"""
<style>
    @font-face {{
        font-family: 'PretendardTitle';
        src: url(data:font/otf;charset=utf-8;base64,{title_font_base64}) format('opentype');
        font-weight: 700;
        font-display: swap;
    }}
    @font-face {{
        font-family: 'PretendardBody';
        src: url(data:font/otf;charset=utf-8;base64,{body_font_base64}) format('opentype');
        font-weight: 500;
        font-display: swap;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# 3-2. PC/모바일 반응형 디자인 CSS (일반 문자열로 f-string 중괄호 오류 원천 차단)
st.markdown(
    """
<style>
    /* 전체 앱 배경 및 반응형 컨테이너 */
    .stApp {
        background: linear-gradient(135deg, #F0F4FF 0%, #E6EDF9 50%, #F5F3FF 100%);
        font-family: 'PretendardBody', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    /* PC / 태블릿 / 모바일 적응형 가로 폭 제어 */
    .block-container {
        width: 100% !important;
        max-width: 820px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        padding-left: clamp(1rem, 3vw, 2.5rem) !important;
        padding-right: clamp(1rem, 3vw, 2.5rem) !important;
    }

    /* 기본 텍스트 폰트 적용 */
    html, body, [class*="css"], p, span, label, div, .stMarkdown, .stText {
        font-family: 'PretendardBody', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    h1, h2, h3, .hero-title, .result-role, .stButton>button {
        font-family: 'PretendardTitle', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* 히어로 헤더 */
    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.25);
    }

    .hero-title {
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 900;
        line-height: 1.25;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 8px;
    }

    .hero-sub {
        font-size: clamp(0.95rem, 2vw, 1.15rem);
        color: #475569;
        text-align: center;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    /* 카드 스타일 (PC/모바일 하이브리드) */
    .intro-box {
        background: rgba(255, 255, 255, 0.96) !important;
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
        border: 1.5px solid rgba(226, 232, 240, 0.9);
        border-radius: 20px;
        padding: 32px 28px 24px 28px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04);
    }

    .slide-card {
        background: rgba(255, 255, 255, 0.94);
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
        border: 1.5px solid rgba(226, 232, 240, 0.9);
        border-radius: 20px;
        padding: clamp(18px, 3.5vw, 32px);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    @media (hover: hover) {
        .slide-card:hover {
            box-shadow: 0 16px 36px -6px rgba(59, 130, 246, 0.08);
            transform: translateY(-2px);
        }
    }

    .intro-highlight {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 1.2rem;
        margin-bottom: 12px;
    }

    .intro-desc {
        color: #334155;
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 18px;
    }

    /* 반응형 사양 그리드 */
    .spec-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 18px;
        padding-top: 16px;
        border-top: 1px dashed #CBD5E1;
        text-align: center;
    }

    .spec-item {
        background: #F8FAFC;
        padding: 10px 8px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }

    .spec-title {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: 600;
    }

    .spec-val {
        font-size: clamp(0.95rem, 1.8vw, 1.15rem);
        color: #2563EB;
        font-weight: 800;
        margin-top: 2px;
    }

    /* 문항 배지 및 질문 본문 */
    .q-badge {
        color: #3B82F6;
        font-weight: 900;
        font-size: clamp(1rem, 2vw, 1.25rem);
        margin-bottom: 6px;
    }

    .q-text {
        color: #0F172A;
        font-weight: 700;
        font-size: clamp(1.05rem, 2.2vw, 1.28rem);
        line-height: 1.55;
    }

    /* 선택지 라디오 버튼 커스텀 */
    div[role="radiogroup"] {
        gap: 10px !important;
    }

    div[role="radiogroup"] > label {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        padding: clamp(12px, 2.5vw, 18px) clamp(14px, 3vw, 22px) !important;
        border-radius: 14px !important;
        margin-bottom: 8px !important;
        width: 100% !important;
        min-height: 52px !important;
        display: flex !important;
        align-items: center !important;
        -webkit-tap-highlight-color: transparent !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease !important;
    }

    @media (hover: hover) {
        div[role="radiogroup"] > label:hover {
            border-color: #93C5FD !important;
            background-color: #F8FAFC !important;
            transform: translateX(4px);
        }
    }

    div[role="radiogroup"] > label:active {
        background-color: #EFF6FF !important;
        border-color: #3B82F6 !important;
    }

    div[role="radiogroup"] > label p {
        font-size: clamp(0.95rem, 1.8vw, 1.05rem) !important;
        line-height: 1.5 !important;
        color: #1E293B !important;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(90deg, #2563EB 0%, #4F46E5 50%, #7C3AED 100%) !important;
        color: white !important;
        font-size: clamp(1rem, 2vw, 1.15rem) !important;
        font-weight: 700 !important;
        min-height: 50px !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 8px 20px -3px rgba(79, 70, 229, 0.35) !important;
        -webkit-tap-highlight-color: transparent !important;
        transition: all 0.25s ease !important;
    }

    @media (hover: hover) {
        .stButton > button:hover {
            transform: scale(1.015) !important;
            box-shadow: 0 12px 24px -3px rgba(79, 70, 229, 0.5) !important;
        }
    }

    /* 결과 배너 */
    .result-banner {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #1E3A8A 100%);
        border-radius: 20px;
        padding: clamp(26px, 5vw, 42px) clamp(18px, 4vw, 32px);
        text-align: center;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 16px 35px -8px rgba(30, 27, 75, 0.45);
    }

    .result-subtext {
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #93C5FD;
        margin-bottom: 6px;
    }

    .result-role {
        font-size: clamp(1.9rem, 5vw, 2.8rem);
        font-weight: 900;
        background: linear-gradient(90deg, #60A5FA, #A78BFA, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
        line-height: 1.25;
    }

    .result-tagline {
        font-size: clamp(0.98rem, 2vw, 1.18rem);
        color: #E2E8F0;
        line-height: 1.5;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 4. 직무 상세 정보 데이터 (6개 직무)
JOBS_DATA = {
    "해외영업": {
        "title": "글로벌 시장을 개척하는 첨병, 해외영업 (Overseas Sales)",
        "tagline": "탁월한 협상력과 글로벌 소통 감각으로 전 세계 판로를 개척하는 도전자",
        "keywords": ["#바이어발굴", "#단가협상", "#해외전시회", "#영업전략"],
        "description": "글로벌 신규 바이어를 발굴하고 시장 수요에 맞는 제품을 제안하여 수출 계약을 성사시킵니다. 문화적 다양성을 이해하고 외국어 및 네고 능력을 바탕으로 회사의 매출을 직접 견인합니다.",
        "skills": "외국어 커뮤니케이션, 대인 관계 협상력, 글로벌 시장 트렌드 파악력",
        "certs": "국제무역사, 무역영어 1급, 토익스피킹/OPIc IH 이상",
    },
    "무역영업관리/사무": {
        "title": "빈틈없는 계약 수호자, 무역영업관리/사무 (Trade Operations)",
        "tagline": "인코텀즈와 무역 서류의 정밀한 통제로 무결점 수출입을 보장하는 컨트롤 타워",
        "keywords": ["#신용장통제", "#인코텀즈", "#선적서류", "#납기관리"],
        "description": "수출입 계약 체결 이후 선적 서류(B/L, C/I, P/L, L/C 등) 발행 및 심사, 대금 결제, 납기 일정을 철저히 통제합니다. 작은 오타 하나도 용납하지 않는 꼼꼼함으로 리스크를 차단합니다.",
        "skills": "무역서류 정밀 검토 능력, 인코텀즈 2020 이해도, 결제 방식(L/C 등) 프로세스 통제력",
        "certs": "국제무역사, 외환전문역, 무역영어",
    },
    "국제물류/포워딩": {
        "title": "글로벌 물류 루트의 지휘자, 국제물류/포워딩 (Forwarding & Logistics)",
        "tagline": "돌발 변수를 즉각 해결하고 최적의 운송 루트를 설계하는 신속 대응 스페셜리스트",
        "keywords": ["#선복확보", "#운임네고", "#스케줄링", "#돌발대응"],
        "description": "선사 및 항공사와의 운임 협상, 선복(Space) 예약, 내륙 운송과 통관을 연계하는 화물 운송 플래너입니다. 항만 파업, 결항 등 돌발 변수 발생 시 즉각적인 대체 루트를 찾아냅니다.",
        "skills": "순발력 및 위기 대응 능력, 복합 운송 루트 설계, 화물 스케줄링 및 운임 협상력",
        "certs": "물류관리사, 유통관리사 2급, 국제무역사",
    },
    "글로벌 소싱/구매": {
        "title": "원가와 품질을 쥐락펴락하는, 글로벌 소싱/구매 (Global Sourcing)",
        "tagline": "치밀한 원가 구조 분석과 최적의 공급사 발굴로 기업 경쟁력을 극대화하는 전략가",
        "keywords": ["#제조사발굴", "#원가분석", "#SCM최적화", "#공급망다변화"],
        "description": "해외 원부자재 및 완제품의 공급망을 발굴하고, 원가 구조를 철저히 분석하여 가장 경쟁력 있는 단가로 조달합니다. 리스크 분산을 위한 공급망 다변화와 품질 관리를 총괄합니다.",
        "skills": "원가 견적서 분해 분석력, 공급망 리스크 관리, 계약 조건 네고 능력",
        "certs": "CPIM (생산재고관리사), CPSM (공인공급관리전문가), 유통관리사",
    },
    "무역 컴플라이언스/통관": {
        "title": "수출입 법률 방어의 핵심, 무역 컴플라이언스/통관 (Trade Compliance)",
        "tagline": "원산지 규정과 관세율을 철저히 분석하여 법적 리스크와 관세를 방어하는 규정 전문가",
        "keywords": ["#FTA원산지", "#관세율산정", "#HS코드", "#수출통제"],
        "description": "HS Code 품목 분류, FTA 원산지 판정, 세관 조사 대비, 전략물자 수출 통제 등 무역 관련 법적 리스크를 선제적으로 방어합니다. 기업의 합법적 절세와 컴플라이언스를 담당합니다.",
        "skills": "관세법 및 무역관련 법령 해석력, HS Code 품목분류 정밀성, FTA 원산지 관리",
        "certs": "원산지관리사, 보세사, 관세사(전문 자격)",
    },
    "무역/물류 데이터 분석가": {
        "title": "데이터로 공급망을 혁신하는, 무역 데이터 분석가 (Trade Data Analyst)",
        "tagline": "방대한 통관·물동량 데이터 속에서 보이지 않는 패턴을 읽어내는 공급망 설계자",
        "keywords": ["#물동량예측", "#SCM데이터", "#빅데이터", "#운송최적화"],
        "description": "통관 데이터, 선박 AIS 위치 정보, 운임 시세, 물동량 추이 데이터를 추출 및 가공하여 리드타임 지연을 예측하고 물류 비용을 최소화하는 통계적 솔루션을 제안합니다.",
        "skills": "SQL, Python 데이터 분석, SCM KPI 시각화, 수요/물동량 예측 모델링",
        "certs": "SQLD, ADsP, 빅데이터분석기사, 정보처리기사",
    },
}

# 5. 실무 시나리오 기반 20문항 데이터셋
QUESTIONS = [
    {
        "id": 1,
        "q": "글로벌 무역 실무에서 가장 가슴 뛰고 보람을 느낄 것 같은 순간은?",
        "options": [
            ("까다로운 해외 바이어를 몇 달간 설득해 대형 수출 계약을 성사시켰을 때", "해외영업"),
            ("수십 장에 달하는 신용장(L/C)의 오탈자와 불일치 조항을 완벽히 교정했을 때", "무역영업관리/사무"),
            ("선적 지연 위기를 대체 선박과 환적 루트로 번개처럼 해결해 제때 운송했을 때", "국제물류/포워딩"),
            ("해외 신규 공장을 직접 발굴해 기존 원가를 20% 절감하는 데 성공했을 때", "글로벌 소싱/구매"),
        ],
    },
    {
        "id": 2,
        "q": "미국 수출 통관 중 새로운 관세 장벽 이슈가 발생했다. 나의 첫 번째 행동은?",
        "options": [
            ("해당 품목의 HS Code 분류 기준과 FTA 협정문 원산지 결정 기준(PSR)을 법리적으로 파고든다.", "무역 컴플라이언스/통관"),
            ("과거 유사 품목의 통관 거부 데이터와 관세청 수입 통계를 추출해 트렌드를 분석한다.", "무역/물류 데이터 분석가"),
            ("현지 통관 관세사 및 현지 바이어에게 즉각 유선 연락하여 실무적 해결책을 협의한다.", "무역영업관리/사무"),
            ("운송 중인 화물의 보세창고 보관료와 대기 리드타임을 계산해 물류비 손실을 줄인다.", "국제물류/포워딩"),
        ],
    },
    {
        "id": 3,
        "q": "내가 평소 문서를 작성하거나 업무를 처리할 때 가장 돋보이는 강점은?",
        "options": [
            ("상대방의 마음을 움직이고 구매 욕구를 자극하는 세련된 제안서 작성", "해외영업"),
            ("인코텀즈 규칙과 계약 조항, 숫자 하나 틀리지 않는 극도의 정밀함", "무역영업관리/사무"),
            ("수치와 통계 지표를 시각화하여 한눈에 문제점을 파악할 수 있는 대시보드 제작", "무역/물류 데이터 분석가"),
            ("복잡한 공급망 구조를 도식화하고 원가 절감 포인트를 짚어내는 기획서", "글로벌 소싱/구매"),
        ],
    },
    {
        "id": 4,
        "q": "출근하자마자 수에즈 운하 정체로 선박 입항이 2주 지연된다는 속보를 접했다. 나의 반응은?",
        "options": [
            ("즉시 포워더와 항공사, 대체 철도 운송 옵션을 비교하며 비상 루트를 섭외한다.", "국제물류/포워딩"),
            ("계약서상 불가항력(Force Majeure) 조항 및 지체상금(LD) 발생 가능성을 법률 검토한다.", "무역 컴플라이언스/통관"),
            ("바이어에게 지연 상황을 브리핑하고, 신뢰가 깨지지 않도록 대화로 조율한다.", "해외영업"),
            ("공장 생산 일정과 국내 재고 상황을 파악해 납기 변경 통지서를 발송한다.", "무역영업관리/사무"),
        ],
    },
    {
        "id": 5,
        "q": "직무를 선택할 때 내가 가장 중요하게 생각하는 업무 환경은?",
        "options": [
            ("해외 출장과 글로벌 네트워킹을 통해 새로운 사람들을 만날 기회가 많은 곳", "해외영업"),
            ("정해진 무역 규정과 절차에 맞춰 안정적이고 체계적으로 돌아가는 시스템", "무역영업관리/사무"),
            ("현장의 긴박한 흐름 속에서 문제를 신속히 해결하고 역동성을 느끼는 곳", "국제물류/포워딩"),
            ("대량의 로그와 데이터를 분석하여 논리적인 결론과 인사이트를 도출하는 환경", "무역/물류 데이터 분석가"),
        ],
    },
    {
        "id": 6,
        "q": "원자재 가격이 급등해 제품 제조 원가가 크게 상승했다. 나는 어떻게 대응할까?",
        "options": [
            ("동남아, 중남미 등 신규 대체 공급사를 리서치하여 단가 네고에 돌입한다.", "글로벌 소싱/구매"),
            ("원자재 가격 변동 추이 데이터를 회귀 분석하여 향후 6개월간의 가격을 예측한다.", "무역/물류 데이터 분석가"),
            ("바이어에게 원자재 상승 요인을 프리젠테이션하고 판매 단가 인상을 유도한다.", "해외영업"),
            ("무관세 혜택이 가능한 FTA 적용 국가의 부품으로 원산지를 대체할 수 있는지 검토한다.", "무역 컴플라이언스/통관"),
        ],
    },
    {
        "id": 7,
        "q": "바이어와의 온라인 화상 미팅을 앞두고 가장 집중해서 준비하는 자료는?",
        "options": [
            ("자사 제품의 강점을 극대화한 카탈로그와 설득력 있는 스토리라인", "해외영업"),
            ("철저하게 계산된 원가 분석표와 생산 가능 수량, 납기 시뮬레이션", "글로벌 소싱/구매"),
            ("선적 서류 샘플과 결제 조건(T/T, L/C), 인코텀즈 2020 세부 조건", "무역영업관리/사무"),
            ("최근 3개년 글로벌 시장 수요 데이터 및 경쟁사 판매량 추이 분석 리포트", "무역/물류 데이터 분석가"),
        ],
    },
    {
        "id": 8,
        "q": "관세청에서 '수출입 안전관리 우수업체(AEO)' 인증 갱신 심사를 나온다고 한다. 나의 태도는?",
        "options": [
            ("법령 기준에 따라 관리 프로세스와 증빙 서류를 한 치의 오차 없이 검증한다.", "무역 컴플라이언스/통관"),
            ("수출입 프로세스별 리드타임 지표와 오류율 데이터를 정량적으로 정리한다.", "무역/물류 데이터 분석가"),
            ("선적 및 통관 관련 서류철을 체계적으로 분류하여 즉각 제출할 수 있도록 정비한다.", "무역영업관리/사무"),
            ("심사 과정에서 규제 요건에 맞지 않는 물류 창고 현장 동선을 신속히 재배치한다.", "국제물류/포워딩"),
        ],
    },
    {
        "id": 9,
        "q": "포워더로부터 해상 운임 견적서를 받았을 때 내가 가장 먼저 하는 일은?",
        "options": [
            ("유류할증료(BAF), 통화할증료(CAF) 등 항목별 비용을 타 포워더와 치열하게 비교 네고한다.", "국제물류/포워딩"),
            ("과거 분기별 해상운임지수(SCFI) 변동 추이 데이터와 비교 분석한다.", "무역/물류 데이터 분석가"),
            ("기존 제품 판매가에 운임 상승분이 적절히 반영되어 마진이 남는지 원가를 재산출한다.", "글로벌 소싱/구매"),
            ("견적 조건(CIF, FOB 등)이 바이어와의 수출 계약서 조건과 일치하는지 대조한다.", "무역영업관리/사무"),
        ],
    },
    {
        "id": 10,
        "q": "해외 전시회(부스)에 파견되었을 때 내가 가장 자연스럽게 맡고 싶은 역할은?",
        "options": [
            ("부스를 지나가는 글로벌 바이어들에게 적극적으로 말을 걸고 명함을 교환하는 프론트 역할", "해외영업"),
            ("부스에서 수집된 바이어 명함 정보를 정리하고 사후 팔로업 메일을 체계적으로 발송하는 역할", "무역영업관리/사무"),
            ("타사 부스를 돌며 경쟁사 제품의 제조 국가, 부품 규격, 추정 원가를 리서치하는 역할", "글로벌 소싱/구매"),
            ("현지 물류 센터 위치와 운송 여건, 통관 규제 사항을 현장에서 조사하는 역할", "국제물류/포워딩"),
        ],
    },
    {
        "id": 11,
        "q": "자유무역협정(FTA) 개정으로 특정 품목의 관세율이 인하된다는 뉴스를 보았다. 나의 반응은?",
        "options": [
            ("협정별 원산지 결정 기준(PSR)을 충족하는지 BOM(자재명세서)을 즉각 확인한다.", "무역 컴플라이언스/통관"),
            ("관세 인하 혜택을 마케팅 포인트로 삼아 현지 바이어들에게 판촉 프로모션을 건다.", "해외영업"),
            ("관세 절감액이 전체 제품 원가율과 물동량에 미칠 재무적 효과를 시뮬레이션한다.", "무역/물류 데이터 분석가"),
            ("관세 인하 효과가 큰 국가의 원자재 공급처로 구매 소싱을 전환할지 검토한다.", "글로벌 소싱/구매"),
        ],
    },
    {
        "id": 12,
        "q": "수출 대금 회수(결제) 방식 중 내가 가장 선호하고 안도감을 느끼는 방식은?",
        "options": [
            ("은행의 지급 보증이 수반되어 서류 일치 시 리스크가 가장 적은 신용장(L/C)", "무역영업관리/사무"),
            ("바이어와의 끈끈한 유대 관계와 신뢰를 바탕으로 계약금을 먼저 받는 T/T 선송금", "해외영업"),
            ("공급업체에 대한 엄격한 신용 평가 데이터 모델링을 거친 후 결정하는 외상 거래", "무역/물류 데이터 분석가"),
            ("국제 결제 분쟁 시 법적 안전장치가 완벽히 구비된 에스크로 및 보증 계약", "무역 컴플라이언스/통관"),
        ],
    },
    {
        "id": 13,
        "q": "화물이 공항 보세구역에서 규격 외 포장으로 인해 선적이 거부되었다. 나의 해결책은?",
        "options": [
            ("즉각 현장 리패킹(Re-packing) 업체를 섭외해 당일 야간 비행기 화물로 재부킹한다.", "국제물류/포워딩"),
            ("위험물 규정(DGR) 및 IATA 국제 항공 규격 조항을 확인해 법적 예외 승인이 가능한지 체크한다.", "무역 컴플라이언스/통관"),
            ("수입자에게 포장 규격 이슈로 인한 비행편 변경 사실을 정확한 공문으로 고지한다.", "무역영업관리/사무"),
            ("포장 불량의 근본 원인을 찾아내어 공장 출하 패키징 가이드라인을 데이터화하여 개선한다.", "글로벌 소싱/구매"),
        ],
    },
    {
        "id": 14,
        "q": "엑셀이나 데이터 툴을 켤 때 내가 주로 하고 싶은 작업은?",
        "options": [
            ("수만 건의 물동량 로그 데이터를 피벗 테이블이나 Python으로 분석해 이상치 탐지", "무역/물류 데이터 분석가"),
            ("수출입 건별 원산지 증빙 서류 및 선적 서류 발급 현황을 체크리스트로 일목요연하게 관리", "무역영업관리/사무"),
            ("해외 거래처별 분기별 매출 달성률과 마진율을 그래프로 시각화", "해외영업"),
            ("전 세계 공급사별 견적 단가와 납기(Lead Time)를 비교 분석하는 매트릭스 작성", "글로벌 소싱/구매"),
        ],
    },
    {
        "id": 15,
        "q": "공급사가 부품 단가를 15% 기습 인상하겠다고 일방적으로 통보해왔다. 나의 대처는?",
        "options": [
            ("원자재 가격 공시 지표와 제조 공정 원가를 분해하여 인상률의 부당함을 데이터로 압박한다.", "글로벌 소싱/구매"),
            ("기존 계약서의 단가 유효기간 조항과 계약 위반 벌칙 조항을 근거로 법적 이의를 제기한다.", "무역 컴플라이언스/통관"),
            ("공급사 대표와 긴급 대면 미팅을 잡아 물량 보증을 조건으로 절충안을 모색한다.", "해외영업"),
            ("타 포워더를 통해 물류 운송비를 절감하여 부품 단가 인상분을 흡수할 방법을 찾는다.", "국제물류/포워딩"),
        ],
    },
    {
        "id": 16,
        "q": "선하증권(B/L)에 표기된 화물 수량과 실제 인보이스 수량이 1개 차이 나는 것을 발견했다.",
        "options": [
            ("신용장 불일치(Discrepancy)로 결제가 거절될 수 있으므로 즉시 수정 B/L 발행을 요청한다.", "무역영업관리/사무"),
            ("세관 허위 신고 및 밀수 혐의가 적용될 수 있으므로 정정 신고 요건을 즉시 확인한다.", "무역 컴플라이언스/통관"),
            ("선적지 창고와 선사에 즉시 무전을 쳐서 잔여 화물이 누락되었는지 현장 확인한다.", "국제물류/포워딩"),
            ("최근 1년간의 선적 오차율 데이터를 조회해 특정 포워더나 창고의 오류 빈도를 파악한다.", "무역/물류 데이터 분석가"),
        ],
    },
    {
        "id": 17,
        "q": "복잡한 공급망 관리(SCM) 프로젝트에서 내가 가장 기여하고 싶은 분야는?",
        "options": [
            ("해외 생산 기지부터 최종 고객 도착까지의 리드타임을 데이터 알고리즘으로 최적화", "무역/물류 데이터 분석가"),
            ("가장 저렴하고 안정적인 원자재 공급처 풀(Pool)을 글로벌 단위로 확장", "글로벌 소싱/구매"),
            ("해상-철도-항공 복합 운송의 최단 경로와 최적 물류 파트너 라인업 구축", "국제물류/포워딩"),
            ("글로벌 무역 분쟁과 관세 규제 리스크를 우회할 수 있는 안전한 합법 통관 루트 확보", "무역 컴플라이언스/통관"),
        ],
    },
    {
        "id": 18,
        "q": "신규 바이어가 자국 시장 독점 판매권을 요구하며 파격적인 첫 주문을 제안했다.",
        "options": [
            ("바이어의 현지 유통망과 잠재력을 평가하여 분기별 최소 판매량 조건을 걸고 적극 계약한다.", "해외영업"),
            ("독점권 부여 시 국내외 경쟁법 위반 소지 및 계약 해지 조건(독소 조항)을 철저히 검토한다.", "무역 컴플라이언스/통관"),
            ("해당 국가의 연간 화물 수입 물동량과 성장률 데이터를 먼저 분석해 진정성을 검증한다.", "무역/물류 데이터 분석가"),
            ("대량 주문을 감당할 수 있는 생산 라인 스케줄과 선복 예약 가능 여부를 먼저 파악한다.", "무역영업관리/사무"),
        ],
    },
    {
        "id": 19,
        "q": "현장 물류창고(보세구역)에 방문했을 때 나의 주된 시선이 머무는 곳은?",
        "options": [
            ("지게차 동선, 컨테이너 적재 효율, 화물 입출고의 빠른 회전 속도", "국제물류/포워딩"),
            ("보세화물 보관 기준 준수 여부, 라벨링 규정 및 세관 봉인 상태", "무역 컴플라이언스/통관"),
            ("포장된 박스의 규격과 파레트 적재비율을 통한 패키징 개선 및 원가 절감 가능성", "글로벌 소싱/구매"),
            ("화물 바코드 스캔 시스템과 WMS(창고관리시스템)의 실시간 데이터 처리 흐름", "무역/물류 데이터 분석가"),
        ],
    },
    {
        "id": 20,
        "q": "10년 후 무역 분야의 전문가로서 내가 꿈꾸는 나의 모습은?",
        "options": [
            ("전 세계 대륙을 누비며 수천억 규모의 글로벌 비즈니스를 주도하는 영업 본부장", "해외영업"),
            ("글로벌 공급망 전체의 선적·통관·결제를 오차 없이 통제하는 무역 총괄 운영자", "무역영업관리/사무"),
            ("전 세계 물류망을 손바닥 보듯 꿰뚫고 어떤 위기에도 화물을 목적지에 보내는 물류 디렉터", "국제물류/포워딩"),
            ("글로벌 소싱 네트워크를 구축해 최상의 가성비와 품질을 창출하는 구매 총괄 CPO", "글로벌 소싱/구매"),
        ],
    },
]

# 6. 세션 상태 관리 (인트로/슬라이드 단계/결과)
if "started" not in st.session_state:
    st.session_state.started = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

total_questions = len(QUESTIONS)

# 7. 화면 렌더링 분기

# 7-1. [홈 / 인트로 화면]
if not st.session_state.started:
    st.markdown(
        '<div style="text-align: center;"><span class="hero-badge">🌐 GLOBAL CAREER SOLUTION</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-title">나의 무역 직무 DNA 찾기</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-sub">"무역은 단순히 외국어만 잘하면 끝날까요?"</div>',
        unsafe_allow_html=True,
    )

    # 기획 의도 설명 박스 (PC/모바일 공통 반응형)
    st.markdown(
        """
        <div class="intro-box">
            <div class="intro-highlight">
                🎯 왜 이 테스트를 꼭 해봐야 할까요?
            </div>
            <div class="intro-desc">
                무역·글로벌 비즈니스는 바이어와 단가를 협상하는 <b>해외영업</b>부터 서류의 완결성을 통제하는 <b>영업관리</b>, 돌발 변수에 즉각 대응하는 <b>국제물류</b>, 관세와 규제를 방어하는 <b>컴플라이언스</b>, 공급망을 최적화하는 <b>데이터 분석</b>까지 직무 스펙트럼이 매우 넓습니다.<br><br>
                자신의 문제 해결 스타일과 맞지 않는 직무를 선택하면 실무 적응에 큰 혼란을 겪을 수 있습니다. 본 테스트는 <b>실제 무역 현장에서 마주치는 20가지 생생한 돌발 시나리오</b>를 통해 나에게 가장 잘 어울리는 <b>단 하나의 최적 직무</b>를 명확히 짚어드립니다.
            </div>
            <div class="spec-grid">
                <div class="spec-item">
                    <div class="spec-title">소요 시간</div>
                    <div class="spec-val">약 3분</div>
                </div>
                <div class="spec-item">
                    <div class="spec-title">진단 문항</div>
                    <div class="spec-val">20개 문항</div>
                </div>
                <div class="spec-item">
                    <div class="spec-title">제공 혜택</div>
                    <div class="spec-val">자격증 로드맵</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")  # 박스와 버튼 사이 여백 분리
    if st.button("🚀 나의 무역 DNA 진단 시작하기", use_container_width=True):
        st.session_state.started = True
        st.rerun()

# 7-2. [슬라이드 질문 화면]
elif not st.session_state.submitted:
    step = st.session_state.current_step
    q_data = QUESTIONS[step]

    # 상단 진행률 게이지 바
    progress_val = (step + 1) / total_questions
    st.progress(progress_val)
    st.caption(f"진행도: {step + 1} / {total_questions} (Q{q_data['id']})")

    # 질문 카드
    st.markdown(
        f"""
        <div class="slide-card">
            <div class="q-badge">Question {step + 1:02d}</div>
            <div class="q-text">{q_data['q']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 이전 답변 불러오기
    prev_selected_text = st.session_state.user_answers.get(step, None)
    labels = [opt[0] for opt in q_data["options"]]
    default_index = labels.index(prev_selected_text) if prev_selected_text in labels else None

    # 선택지 렌더링
    selected_option = st.radio(
        f"q_radio_{step}",
        labels,
        index=default_index,
        key=f"radio_step_{step}",
        label_visibility="collapsed",
    )

    st.write("")

    # 이전 / 다음 버튼 (모바일 2열 균등 배치)
    col1, col2 = st.columns(2)

    with col1:
        if step > 0:
            if st.button("⬅️ 이전", use_container_width=True):
                if selected_option is not None:
                    st.session_state.user_answers[step] = selected_option
                st.session_state.current_step -= 1
                st.rerun()

    with col2:
        if step < total_questions - 1:
            if st.button("다음 ➡️", use_container_width=True):
                if selected_option is None:
                    st.warning("⚠️ 답변을 선택해 주세요!")
                else:
                    st.session_state.user_answers[step] = selected_option
                    st.session_state.current_step += 1
                    st.rerun()
        else:
            if st.button("✨ 결과 보기", use_container_width=True):
                if selected_option is None:
                    st.warning("⚠️ 마지막 문항의 답변을 선택해 주세요!")
                else:
                    st.session_state.user_answers[step] = selected_option
                    
                    # 최종 채점 진행
                    scores = {job: 0 for job in JOBS_DATA.keys()}
                    for s_idx, q in enumerate(QUESTIONS):
                        ans_text = st.session_state.user_answers.get(s_idx)
                        for opt_text, opt_job in q["options"]:
                            if opt_text == ans_text:
                                scores[opt_job] += 1
                                break
                    
                    st.session_state.scores = scores
                    st.session_state.submitted = True
                    st.rerun()

# 7-3. [진단 결과 화면]
else:
    scores = st.session_state.scores
    best_job = max(scores, key=scores.get)
    job_info = JOBS_DATA[best_job]

    st.balloons()

    st.markdown(
        f"""
        <div class="result-banner">
            <div class="result-subtext">Best Career Match</div>
            <div class="result-role">{best_job}</div>
            <div class="result-tagline">"{job_info['tagline']}"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(" ".join([f"`{kw}`" for kw in job_info["keywords"]]))
    st.write("")

    tab1, tab2 = st.tabs(["📋 직무 상세 리포트", "📊 직무 적합도 차트"])

    with tab1:
        st.subheader("💡 주요 업무")
        st.write(job_info["description"])

        st.subheader("🛠️ 필요 역량")
        st.info(job_info["skills"])

        st.subheader("🎓 추천 자격증")
        st.success(job_info["certs"])

    with tab2:
        st.subheader("직무별 매칭 점수 분석")

        df_scores = pd.DataFrame(list(scores.items()), columns=["직무", "점수"])
        fig = px.line_polar(df_scores, r="점수", theta="직무", line_close=True)
        fig.update_traces(
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.25)",
            line_color="#6366F1",
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(scores.values()) + 1]),
                angularaxis=dict(tickfont=dict(size=11))
            ),
            showlegend=False,
            margin=dict(l=30, r=30, t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        df_rank = pd.DataFrame(
            sorted_scores, columns=["직무명", "매칭 점수"]
        )
        st.dataframe(df_rank, use_container_width=True, hide_index=True)

    st.write("")
    if st.button("🔄 다시 테스트하기", use_container_width=True):
        st.session_state.started = False
        st.session_state.submitted = False
        st.session_state.current_step = 0
        st.session_state.user_answers = {}
        st.rerun()