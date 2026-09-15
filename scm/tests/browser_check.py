"""Real Chromium checks. Run after starting python app.py on port 5000."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results'
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:5000/',wait_until='networkidle')
    page.wait_for_selector('.metric-value')
    page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
    assert page.locator('.metric').count()==4
    page.locator('[data-chart="bar"]').click()
    assert page.locator('#trend-chart rect').count()>7
    page.locator('[data-chart="line"]').click()
    page.locator('[data-term="OTD"]').first.hover()
    assert page.locator('#tooltip').is_visible()
    page.locator('[data-view="orders"]').first.click()
    page.locator('#search').fill('무선 키보드')
    assert '무선 키보드' in page.locator('#list-table').inner_text()
    page.locator('#list-table .row-link').first.click()
    assert page.locator('#detail-dialog').is_visible()
    page.locator('#detail-dialog [data-close]').click()
    page.locator('#search').fill('없는상품123')
    assert '조건에 맞는 항목이 없어요' in page.locator('#list-table').inner_text()
    page.locator('[data-view="inventory"]').first.click()
    page.locator('#status-filter').select_option('재고 부족')
    assert page.locator('#list-table tbody tr').count()==6
    page.locator('#warehouse').select_option('용인 센터')
    page.wait_for_timeout(300)
    assert page.locator('#list-table tbody tr').count()==2
    page.locator('#warehouse').select_option('')
    page.locator('[data-view="overview"]').first.click()
    with page.expect_download() as download:
        page.locator('#export').click()
    assert download.value.suggested_filename.endswith('.csv')
    page.locator('[data-view="files"]').first.click()
    page.locator('#file-input').set_input_files(str(OUT/'desktop.png'))
    page.wait_for_selector('.image-card')
    page.locator('[data-image-background]').first.click()
    expect(page.locator('body')).to_have_class('has-background')
    page.reload(wait_until='networkidle')
    expect(page.locator('body')).to_have_class('has-background')
    page.locator('[data-view="files"]').first.click()
    page.locator('[data-image-delete]').first.click()
    expect(page.locator('body')).not_to_have_class('has-background')
    page.locator('[data-action="settings"]').first.click()
    page.locator('[data-theme="ocean"]').click()
    assert page.locator('body').get_attribute('data-theme')=='ocean'
    page.locator('[data-theme="sage"]').click()
    page.locator('#api-key').fill('browser-test-key-123')
    page.locator('#save-settings').click()
    page.locator('.chat-fab').click()
    page.route('**/api/chat?*',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({'answer':'테스트 답변: 데모 데이터입니다.'})))
    page.locator('#chat-input').fill('요약해 줘')
    page.locator('#chat-send').click()
    expect(page.locator('#chat-messages')).to_contain_text('테스트 답변')
    assert 'browser-test-key-123' not in page.evaluate('JSON.stringify(localStorage)')
    page.locator('#chat-dialog [data-close]').click()
    page.reload(wait_until='networkidle')
    page.locator('[data-action="settings"]').first.click()
    assert page.locator('#api-key').input_value()==''
    page.locator('#settings-dialog [data-close]').click()
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.locator('#menu-toggle').click()
    page.locator('.nav-item[data-view="inventory"]').click()
    assert not page.locator('#shade').is_visible()
    assert page.locator('#list-view').is_visible()
    page.locator('[data-term="SKU"]').click()
    assert page.locator('#tooltip').is_visible()
    page.locator('.chat-fab').click()
    assert page.locator('#chat-dialog').is_visible()
    assert page.locator('#chat-dialog').bounding_box()['width']<=390
    page.locator('#chat-dialog [data-close]').click()
    for width in [360,768,1024]:
        page.set_viewport_size({'width':width,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
    assert not errors,errors
    print('PASS: desktop, mobile, filters, chart, details, empty state, CSV, images, theme, mock chat, API-key isolation; no JavaScript errors.')
    browser.close()
