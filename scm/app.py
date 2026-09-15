
"""Flow SCM: deterministic demo dashboard and user-key Gemini assistant."""
from datetime import date, datetime, timedelta, timezone
import csv
import io
import json
import os
import re
import secrets
import requests
from flask import Flask, Response, jsonify, render_template, request, session

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                  MAX_CONTENT_LENGTH=32768, SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=bool(os.environ.get('RENDER')))
app.json.ensure_ascii = False
PRODUCTS = [
    ('무선 키보드', '디지털', '한빛테크', 420, 150, 39000),
    ('데스크 오거나이저', '리빙', '모노리빙', 85, 120, 18000),
    ('텀블러 500ml', '리빙', '그린웍스', 680, 200, 24000),
    ('노트북 파우치', '패션', '오브젝트', 64, 100, 29000),
    ('USB-C 허브', '디지털', '한빛테크', 310, 120, 45000),
    ('코튼 에코백', '패션', '오브젝트', 920, 180, 12000),
    ('LED 데스크 램프', '리빙', '모노리빙', 180, 90, 36000),
    ('블루투스 마우스', '디지털', '한빛테크', 250, 100, 27000),
]
WAREHOUSES = ['용인 센터', '이천 센터', '부산 센터']


def today():
    return datetime.now(timezone(timedelta(hours=9))).date()


def orders():
    result = []
    for i in range(180):
        p = PRODUCTS[i % len(PRODUCTS)]
        status = ['배송 완료', '배송 중', '출고 준비', '배송 완료', '지연', '배송 완료'][(i+i//6) % 6]
        quantity = 8 + (i * 13 % 92)
        result.append(dict(id=f'FL-{26001+i}', product=p[0], category=p[1], supplier=p[2],
                           warehouse=WAREHOUSES[(i+i//10) % 3], quantity=quantity, amount=quantity*p[5],
                           date=(today()-timedelta(days=i % 30)).isoformat(), status=status,
                           on_time=status == '배송 완료' and i % 13 != 0,
                           destination=['서울 성동구', '경기 수원시', '부산 해운대구', '대전 유성구'][i % 4]))
    return sorted(result, key=lambda r: (r['date'], r['id']), reverse=True)


def filtered_orders():
    try:
        days = int(request.args.get('days', '7'))
    except ValueError:
        raise ValueError('조회 기간을 확인해 주세요.')
    if days not in (7, 14, 30):
        raise ValueError('조회 기간은 7일, 14일, 30일 중 선택해 주세요.')
    warehouse, category = request.args.get('warehouse', ''), request.args.get('category', '')
    if warehouse and warehouse not in WAREHOUSES:
        raise ValueError('올바른 물류센터를 선택해 주세요.')
    if category and category not in ('디지털', '리빙', '패션'):
        raise ValueError('올바른 카테고리를 선택해 주세요.')
    cutoff = (today()-timedelta(days=days-1)).isoformat()
    return [r for r in orders() if r['date'] >= cutoff and (not warehouse or r['warehouse'] == warehouse)
            and (not category or r['category'] == category)], days, warehouse, category


def dashboard():
    rows, days, warehouse, category = filtered_orders()
    inventory = []
    for i, p in enumerate(PRODUCTS):
        if category and p[1] != category:
            continue
        for j, wh in enumerate(WAREHOUSES):
            if warehouse and wh != warehouse:
                continue
            stock, safety = round(p[3]*(1+j*.2)), round(p[4]*(1+j*.2))
            inventory.append(dict(id=f'SKU-{100+i}-{j}', product=p[0], category=p[1], supplier=p[2],
                                  warehouse=wh, stock=stock, safety=safety, price=p[5],
                                  status='재고 부족' if stock < safety else '여유 재고' if stock > safety*4 else '적정'))
    delivered = [r for r in rows if r['status'] == '배송 완료']
    trend = []
    for age in reversed(range(days)):
        day = (today()-timedelta(days=age)).isoformat()
        daily = [r for r in rows if r['date'] == day]
        trend.append(dict(date=day, orders=sum(r['quantity'] for r in daily),
                          shipped=sum(r['quantity'] for r in daily if r['status'] in ('배송 완료','배송 중'))))
    suppliers = []
    for name in sorted({p['supplier'] for p in inventory}):
        related = [r for r in rows if r['supplier'] == name]
        completed = [r for r in related if r['status'] == '배송 완료']
        suppliers.append(dict(name=name, orders=len(related), amount=sum(r['amount'] for r in related),
                              rate=round(100*sum(r['on_time'] for r in completed)/len(completed),1) if completed else None,
                              products=len({r['product'] for r in inventory if r['supplier'] == name})))
    return dict(demo=True, date=today().isoformat(), days=days, orders=rows, inventory=inventory,
                suppliers=suppliers, trend=trend, metrics=dict(orders=len(rows),
                stock=sum(r['stock'] for r in inventory), low_stock=sum(r['stock']<r['safety'] for r in inventory),
                delayed=sum(r['status']=='지연' for r in rows), revenue=sum(r['amount'] for r in rows),
                otd=round(100*sum(r['on_time'] for r in delivered)/len(delivered),1) if delivered else None))


def analytics(period='month'):
    """Aggregate the full demo history by day/month/quarter/year."""
    if period not in ('day', 'month', 'quarter', 'year'):
        raise ValueError('분석 단위는 일·월·분기·연도 중 선택해 주세요.')
    warehouse, category = request.args.get('warehouse', ''), request.args.get('category', '')
    if warehouse and warehouse not in WAREHOUSES:
        raise ValueError('올바른 물류센터를 선택해 주세요.')
    if category and category not in ('디지털', '리빙', '패션'):
        raise ValueError('올바른 카테고리를 선택해 주세요.')
    rows = [r for r in orders() if (not warehouse or r['warehouse'] == warehouse)
            and (not category or r['category'] == category)]
    def bucket(value):
        year, month = value.year, value.month
        if period == 'day': return value.isoformat()
        if period == 'month': return f'{year:04d}-{month:02d}'
        if period == 'quarter': return f'{year:04d}년 {((month-1)//3)+1}분기'
        return f'{year:04d}년'
    groups = {}
    for row in rows:
        key = bucket(date.fromisoformat(row['date']))
        groups.setdefault(key, []).append(row)
    result = []
    for key, grouped in sorted(groups.items()):
        done = [r for r in grouped if r['status'] == '배송 완료']
        result.append(dict(period=key, orders=len(grouped), quantity=sum(r['quantity'] for r in grouped),
                           amount=sum(r['amount'] for r in grouped), delayed=sum(r['status'] == '지연' for r in grouped),
                           otd=round(100*sum(r['on_time'] for r in done)/len(done), 1) if done else None))
    recent = result[-3:]
    avg = lambda key: round(sum(r[key] for r in recent)/len(recent)) if recent else 0
    current = dashboard()['metrics'] if request.args.get('days') else None
    return dict(demo=True, period=period, warehouse=warehouse, category=category, rows=result,
                forecast=dict(orders=avg('orders'), quantity=avg('quantity'), amount=avg('amount'),
                              otd=round(sum(r['otd'] for r in recent if r['otd'] is not None)/len([r for r in recent if r['otd'] is not None]),1)
                              if any(r['otd'] is not None for r in recent) else None,
                              basis='최근 3개 구간 평균을 이용한 단순 예상치'),
                kpi=dict(target_orders=120, target_otd=95.0, target_delay_rate=5.0,
                         actual_orders=current['orders'] if current else len(rows),
                         actual_otd=current['otd'] if current else (result[-1]['otd'] if result else None),
                         actual_delay_rate=round(100*sum(r['status'] == '지연' for r in rows)/len(rows),1) if rows else None))


@app.get('/')
def index():
    session.setdefault('csrf', secrets.token_urlsafe(32))
    return render_template('index.html', csrf=session['csrf'])


@app.get('/healthz')
def health():
    return {'status': 'ok'}


@app.get('/api/dashboard')
def data():
    try:
        return jsonify(dashboard())
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@app.get('/api/analytics')
def analytics_data():
    try:
        return jsonify(analytics(request.args.get('period', 'month')))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@app.get('/api/export')
def export():
    try:
        rows, *_ = filtered_orders()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['주문번호','상품','카테고리','거래처','물류센터','수량','주문금액','주문일','상태'])
    writer.writerows([r[k] for k in ('id','product','category','supplier','warehouse','quantity','amount','date','status')] for r in rows)
    return Response('\ufeff'+output.getvalue(), content_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition': 'attachment; filename="flow-scm-report.csv"'})


@app.post('/api/chat')
def chat():
    if request.content_length and request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return jsonify(error='요청 크기가 너무 큽니다. 새 대화를 시작해 주세요.'),413
    if not session.get('csrf') or not secrets.compare_digest(request.headers.get('X-CSRF-Token','').encode(),session['csrf'].encode()):
        return jsonify(error='페이지를 새로고침하고 다시 시도해 주세요.'), 403
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error='올바른 메시지를 보내 주세요.'), 400
    message, key, model = (body.get(k, '') for k in ('message','api_key','model'))
    if not isinstance(message,str) or not 1 <= len(message.strip()) <= 2000:
        return jsonify(error='질문은 1~2,000자로 입력해 주세요.'), 400
    if not isinstance(key,str) or not 10 <= len(key) <= 256 or not key.isascii() or any(c.isspace() for c in key):
        return jsonify(error='본인의 Gemini API 키를 입력해 주세요.'), 400
    if not isinstance(model,str) or not re.fullmatch(r'gemini-[a-zA-Z0-9.\-]{1,70}',model):
        return jsonify(error='Gemini 모델 ID를 확인해 주세요.'), 400
    history = body.get('history',[])
    if not isinstance(history,list) or len(history)>10 or any(not isinstance(x,dict) or x.get('role') not in ('user','model') or not isinstance(x.get('text'),str) or len(x['text'])>4000 for x in history):
        return jsonify(error='대화가 너무 길거나 형식이 올바르지 않습니다. 새 대화를 시작해 주세요.'),400
    try:
        context = dashboard()
    except ValueError as exc:
        return jsonify(error=str(exc)),400
    instruction = ('당신은 친절한 한국어 SCM 도우미입니다. 어려운 용어를 풀어서 간결하게 답하세요. '
                   '다음은 실제 기업 자료가 아닌 데모 데이터입니다. 숫자를 지어내지 마세요. '
                   '주문 금액은 모든 상태의 주문 합계이며 확정 매출이 아닙니다. '
                   'OTD는 배송 완료 주문 중 정시 도착 주문의 비율입니다. '
                   '데이터에 없는 예측은 가정이라고 밝혀 주세요. 작업을 실행할 권한은 없습니다. '
                   +json.dumps({'days':context['days'],'metrics':context['metrics'], 'suppliers':context['suppliers']},ensure_ascii=False))
    contents = [{'role':h['role'],'parts':[{'text':h['text']}]} for h in history]
    contents.append({'role':'user','parts':[{'text':message.strip()}]})
    try:
        upstream = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
            headers={'x-goog-api-key':key}, json={'systemInstruction':{'parts':[{'text':instruction}]},
            'contents':contents,'generationConfig':{'maxOutputTokens':1600}},timeout=(3.05,15))
        if upstream.status_code != 200:
            errors = {400:'API 키, 모델 ID 또는 질문을 확인해 주세요.',401:'API 키 인증에 실패했습니다.',
                      403:'API 키의 권한을 확인해 주세요.',404:'사용 가능한 모델 ID를 입력해 주세요.',
                      429:'사용 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.'}
            return jsonify(error=errors.get(upstream.status_code,'AI 서비스가 응답하지 않습니다. 잠시 후 다시 시도해 주세요.')),502
        payload = upstream.json()
        answer = '\n'.join(p.get('text','') for c in payload.get('candidates',[])[:1]
                           for p in c.get('content',{}).get('parts',[]) if not p.get('thought'))
        if not answer.strip():
            return jsonify(error='답변을 받지 못했습니다. 질문을 바꾸어 다시 시도해 주세요.'),502
        return jsonify(answer=answer)
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        return jsonify(error='AI 연결이 지연되거나 응답이 올바르지 않습니다. 다시 시도해 주세요.'),502


@app.errorhandler(413)
def too_large(_):
    return jsonify(error='요청 크기가 너무 큽니다. 새 대화를 시작해 주세요.'),413


@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    if request.path.startswith('/api/') or request.path == '/':
        response.headers['Cache-Control']='no-store'
    return response


def create_app():
    """Support hosts configured with the app:create_app() entry point."""
    return app


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT',5000)), debug=False)
