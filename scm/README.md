# Flow SCM

Flask로 만든 한국어 SCM 대시보드입니다. 주문, 재고, 배송, 거래처를 쉽게 살펴보고 보고서를 내보낼 수 있습니다.

## 바로 실행

Windows PowerShell에서 이 `scm` 폴더로 이동한 뒤 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

브라우저에서 **http://127.0.0.1:5000** 을 엽니다. 이미 가상환경과 패키지가 설치되어 있으면 마지막 명령만 실행하면 됩니다.

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

## 구현된 기능

- 한눈에 보기: 주문·현재고·정시 배송률·주문금액, 주문/출고 차트, 배송 상태, 먼저 확인할 일.
- 주문·재고·배송·거래처: 검색, 상태 필터, 페이지 이동, 상세 모달.
- 조회 조건: 최근 7/14/30일, 물류센터, 상품 카테고리. 차트·목록·CSV·챗봇 요약에 같은 조건 적용.
- 보고서: UTF-8 BOM CSV(한글 Excel 대응), 브라우저 인쇄/PDF 저장.
- 쉬운 용어: 마우스 올리기, 키보드 포커스, 터치로 OTD·SKU·안전재고 등의 뜻 확인.
- 이미지 보관함: PNG/JPG/WebP 선택·드래그, 미리보기, 삭제, 첫 화면 배경 적용. 파일당 5MB, 4,000만 화소 이하.
- 세이지·오션·샌드 테마, 모바일 메뉴, 반응형 표, 애니메이션 감소 설정 대응.
- 사용자가 자기 Gemini API 키를 입력하는 대화형 AI 도우미.
- 한국어 Pretendard 가변 글꼴을 로컬 제공. Windows·macOS 한글 시스템 글꼴 대체 목록 포함.

## 데이터와 저장 범위

**현재는 동작하는 데모이며 ERP/WMS 또는 실제 기업 DB와 연결되어 있지 않습니다.** 매번 동일한 규칙으로 생성하는 180건의 최근 주문, 8종 상품, 3개 물류센터, 4개 거래처를 사용합니다. 날짜는 실행 서버의 오늘 날짜에 맞춥니다.

현재고와 안전재고는 현재 시점의 데모 스냅샷이므로 조회 기간을 바꾸어도 수량은 그대로입니다. 센터·카테고리 필터는 적용됩니다. 정시 배송률은 완료 주문 중 정시 도착 비율이며, 완료 주문이 없으면 `—`로 표시합니다. 주문금액은 모든 상태의 주문을 포함하므로 확정 매출이 아닙니다.

이미지는 **이 브라우저의 IndexedDB에만 저장**됩니다. 서버로 전송하거나 팀원과 공유하지 않습니다. 브라우저 데이터를 지우면 이미지도 지워집니다. 테마와 배경 이미지 ID만 localStorage에 저장합니다.

macOS 느낌의 폴더·카드·화면 구성은 CSS/SVG로 직접 구현했습니다. Apple 시스템 이미지나 SF Symbols 원본을 번들에 포함하지 않았습니다. 사용 권한이 있는 이미지 파일은 보관함에서 선택할 수 있습니다. `.icns`, HEIC는 PNG/JPG/WebP로 변환 후 사용하세요.

## AI 도우미

1. 왼쪽 아래 **화면 · API 설정**, 또는 챗봇의 **연결 설정**을 엽니다.
2. 본인의 Gemini API 키와 해당 키로 사용 가능한 모델 ID를 입력합니다.
3. 적용 후 오른쪽 아래 **무엇이든 물어보세요**를 누릅니다.

기본 모델 문자열은 `gemini-2.5-flash`이며, 이용 가능 여부에 따라 설정에서 변경할 수 있습니다. 키 입력 자체는 연결 성공을 뜻하지 않으며 첫 질문에서 확인됩니다.

키는 현재 페이지 메모리와 비밀번호 입력칸에만 존재하며, 질문할 때 HTTPS 배포 서버를 거쳐 Google Gemini API의 `x-goog-api-key` 헤더로 전달합니다. 키를 서버 DB·세션·브라우저 저장소에 저장하거나 URL에 넣지 않습니다. 새로고침 또는 ‘키 지우기’로 삭제됩니다. 대화는 최근 최대 6개 메시지와 현재 필터의 데모 집계를 포함합니다. **API 비용은 입력한 키의 소유자에게 적용됩니다.** 실제 키로 유료 요청을 수행하는 테스트는 실행하지 않았습니다.

## Render 배포

[Render Flask 배포 문서](https://render.com/docs/deploy-flask)의 Gunicorn 방식으로 구성했습니다.

현재 저장소 구조는 상위 `AX_Master_2` 저장소 안에 `scm/` 폴더가 있는 형태입니다.

### 직접 Web Service 만들기

| 항목 | 값 |
| --- | --- |
| Runtime | Python |
| Root Directory | `scm` |
| Build Command | `python -m pip install -r requirements.txt && python -m pip check && python -c "from app import app; print('Flask app import OK')" && python -m gunicorn --check-config app:app` |
| Start Command | `python -m gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 60 --access-logfile - --error-logfile -` |
| Health Check Path | `/healthz` |
| Environment | `SECRET_KEY`: 무작위의 충분히 긴 비밀 문자열, `PYTHON_VERSION`: `3.13.5` |

`scm` 내용만 별도 저장소의 루트에 올리면 **Root Directory를 비워 두세요**.

### `gunicorn: command not found` 오류 해결

이 로그가 보이면 현재 Flask 배포 파일이 아닌 다른 `requirements.txt`를 설치했을 가능성이 큽니다. 특히 설치 로그에 `streamlit`, `numpy`, `pandas`, `matplotlib`, `plotly`, `python-pptx`가 보이고 `Flask`, `gunicorn`이 없다면 `legacy/requirements.txt` 또는 예전 커밋을 보고 있는 상태입니다.


이 폴더의 `requirements.txt`에는 Flask와 Linux용 Gunicorn이 포함되어 있습니다. 설치 로그에 Streamlit만 있고 Flask/Gunicorn이 없다면 연결된 브랜치·커밋과 Root Directory를 확인하세요. `legacy/requirements.txt`는 현재 웹사이트의 배포용 파일이 아닙니다.

1. 최신 `scm/app.py`, `scm/requirements.txt`, `scm/render.yaml`을 연결된 저장소에 반영합니다.
2. 기존 Render 서비스의 Settings → Build & Deploy에서 위 표의 Root Directory와 Start Command를 적용합니다. 수동 생성 서비스는 로컬 `render.yaml` 수정만으로 설정이 바뀌지 않습니다.
3. Build Command를 `python -m pip install -r requirements.txt && python -m pip check && python -c "from app import app; print('Flask app import OK')" && python -m gunicorn --check-config app:app`으로 설정합니다. 의존성 설치, Flask 앱 import, Gunicorn 설정을 배포 전에 검사합니다.
4. 최신 커밋을 다시 배포하고 `/healthz` 응답이 `{"status":"ok"}`인지 확인합니다.

기존 `gunicorn "app:create_app()"`도 앱 구조상 호환되지만, 현재 배포 설정은 `python -m gunicorn app:app ...`을 권장합니다. `python -m` 형식을 사용하면 실행 파일 PATH 문제를 줄일 수 있습니다.

### Blueprint

`render.yaml`도 포함했습니다. 현재 상위 저장소를 연결할 때 Blueprint 파일 경로는 `scm/render.yaml`, 설정의 `rootDir`는 `scm`입니다. `scm`을 독립 저장소로 만들면 `render.yaml`의 `rootDir: scm` 줄을 삭제하세요. Blueprint는 `SECRET_KEY`를 자동 생성합니다. 모든 Gunicorn worker는 동일한 키를 사용해야 합니다.

배포 설정만 준비했으며 Render 계정 연결·실제 공개 배포는 수행하지 않았습니다. 무료 인스턴스는 유휴 후 첫 접근이 느릴 수 있습니다. 이미지가 서버 디스크에 저장되지 않으므로 서버 재시작에 따른 업로드 유실 문제는 없지만, 다른 기기에서 공유되지는 않습니다.

실제 회사 데이터를 연결해 운영하려면 인증·팀 권한, 영구 DB, 접근 기록, 서버 측 사용량 제한, 이미지 공유용 저장소를 별도 연결해야 합니다. 현재 공개 데모에는 로그인 기능이 없습니다.

## 파일 구조

```text
app.py                    Flask 라우트, 데모 집계, CSV, Gemini 중계
templates/index.html      한국어 화면 및 모달
static/css/style.css      반응형 디자인, 테마, 인쇄 스타일
static/js/app.js           화면 전환, 차트, 필터, 이미지 저장, 챗봇
static/fonts/             Pretendard 글꼴 및 OFL 라이선스
static/images/mark.svg    직접 제작한 Flow 마크
render.yaml               Render 배포 설정
tests/                    서버·브라우저 검증
docs/GEMINI_REVIEW.txt     Gemini에 그대로 전달할 검수 요청서
legacy/                   기존 Streamlit app.py와 requirements.txt 보관본
```

기존 Streamlit 파일은 변경 전 내용을 `legacy/streamlit_app.py`에 보관했습니다. 신규 Flask 앱의 실행 경로에서는 사용하지 않습니다. 기존의 모든 고급 시뮬레이션·PPTX 기능을 1:1로 이식한 것은 아닙니다.

## 검증

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
# 앱을 별도 터미널에서 실행한 뒤, Windows에 설치된 Edge로 검증
.\.venv\Scripts\python.exe tests/browser_check.py
```

서버 테스트 20개 및 실제 Chromium(Edge)에서 PC·모바일 기능 검증 통과. 360/390/768/1024px에서 페이지 가로 넘침, 검색·필터·차트·상세·빈 결과·CSV 다운로드·이미지 유지·배경·테마·모의 AI 응답·API 키 새로고침 후 제거를 확인했습니다. 화면 기록은 `test-results/`에 생성되며 Git에서 제외됩니다. 브라우저 테스트의 Gemini 응답은 모의 응답입니다. Safari와 실제 iPhone 기기에서는 별도 검수가 필요합니다.

## 참고와 라이선스

- 사용자 지정 참고: [Godly / Taito](https://godly.design/website/taito/), [Taito](https://taito.ai/). 구성과 여백의 방향을 참고하고 새 SCM UI로 구현했습니다.
- 글꼴: [Pretendard](https://github.com/orioncactus/pretendard), SIL Open Font License 1.1. 전체 라이선스는 `static/fonts/OFL.txt`.
- Gemini REST: [공식 API 문서](https://ai.google.dev/api/generate-content).
