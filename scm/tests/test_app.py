import csv
import io
from unittest.mock import Mock
import pytest
import requests
from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        client.get('/')
        yield client


def csrf(client):
    with client.session_transaction() as session:
        return {'X-CSRF-Token': session['csrf']}


def test_home_and_assets(client):
    res = client.get('/')
    assert res.status_code == 200
    assert '오늘의 흐름'.encode() in res.data
    assert res.headers['X-Frame-Options'] == 'DENY'
    assert client.get('/healthz').json == {'status': 'ok'}
    for path in ['/static/css/style.css','/static/js/app.js','/static/fonts/PretendardVariable.woff2']:
        assert client.get(path).status_code == 200


@pytest.mark.parametrize('days', [7,14,30])
def test_aggregates_and_filters(client,days):
    data = client.get(f'/api/dashboard?days={days}&warehouse=용인 센터&category=디지털').json
    rows = data['orders']
    assert rows and all(r['warehouse']=='용인 센터' and r['category']=='디지털' for r in rows)
    assert data['metrics']['orders'] == len(rows)
    assert data['metrics']['revenue'] == sum(r['amount'] for r in rows)
    assert sum(t['orders'] for t in data['trend']) == sum(r['quantity'] for r in rows)
    assert sum(t['shipped'] for t in data['trend']) == sum(r['quantity'] for r in rows if r['status'] in ('배송 중','배송 완료'))
    done = [r for r in rows if r['status']=='배송 완료']
    assert data['metrics']['otd'] == (round(sum(r['on_time'] for r in done)/len(done)*100,1) if done else None)
    assert all(r['warehouse']=='용인 센터' and r['category']=='디지털' for r in data['inventory'])


def test_inventory_independent_of_period(client):
    assert client.get('/api/dashboard?days=7').json['inventory'] == client.get('/api/dashboard?days=30').json['inventory']


@pytest.mark.parametrize('query', ['days=no','days=0','days=365','warehouse=invalid','category=invalid'])
def test_invalid_filters(client,query):
    assert client.get('/api/dashboard?'+query).status_code == 400
    assert client.get('/api/export?'+query).status_code == 400


def test_csv_matches_filtered_data(client):
    query = 'days=14&category=패션'
    data = client.get('/api/dashboard?'+query).json
    response = client.get('/api/export?'+query)
    assert response.data.startswith(b'\xef\xbb\xbf')
    rows = list(csv.reader(io.StringIO(response.data.decode('utf-8-sig'))))
    assert len(rows)-1 == len(data['orders'])
    assert rows[0][0] == '주문번호'
    assert all(r[2]=='패션' for r in rows[1:])


def test_csrf_and_validation(client):
    assert client.post('/api/chat',json={}).status_code == 403
    for payload in [[],{}, {'message':1}, {'message':'hi','api_key':'test-key-123456','model':'../../evil'}]:
        assert client.post('/api/chat',json=payload,headers=csrf(client)).status_code == 400


def test_chat_success_context_and_no_persistence(client,monkeypatch):
    upstream = Mock(return_value=Mock(status_code=200,json=lambda:{'candidates':[{'content':{'parts':[{'text':'데모 요약입니다.'}]}}]}))
    monkeypatch.setattr('app.requests.post',upstream)
    body={'message':'요약해 줘','api_key':'test-secret-12345','model':'gemini-2.5-flash','history':[]}
    res=client.post('/api/chat?days=14&category=패션',json=body,headers=csrf(client))
    assert res.status_code == 200 and res.json['answer']=='데모 요약입니다.'
    kwargs=upstream.call_args.kwargs
    assert kwargs['headers']['x-goog-api-key']==body['api_key']
    assert '"days": 14' in kwargs['json']['systemInstruction']['parts'][0]['text']
    assert body['api_key'] not in res.data.decode()
    with client.session_transaction() as session:
        assert set(session.keys()) == {'csrf'}


@pytest.mark.parametrize('code',[400,401,403,404,429,500])
def test_chat_provider_error_redacted(client,monkeypatch,code):
    monkeypatch.setattr('app.requests.post',Mock(return_value=Mock(status_code=code,text='SECRET key details')))
    res=client.post('/api/chat',json={'message':'질문','api_key':'test-secret-12345','model':'gemini-2.5-flash'},headers=csrf(client))
    assert res.status_code==502 and 'SECRET' not in res.data.decode()


def test_chat_timeout_and_body_limit(client,monkeypatch):
    monkeypatch.setattr('app.requests.post',Mock(side_effect=requests.Timeout))
    res=client.post('/api/chat',json={'message':'질문','api_key':'test-secret-12345','model':'gemini-2.5-flash'},headers=csrf(client))
    assert res.status_code==502
    assert client.post('/api/chat',data='x'*40000,headers=csrf(client)).status_code==413
