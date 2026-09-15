'use strict';
const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];
const icons = {
 grid:'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
 bag:'<path d="M5 7h14l1 14H4L5 7Z"/><path d="M8 8V6a4 4 0 0 1 8 0v2"/>',
 box:'<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Z"/><path d="m3 8 9 5 9-5M12 13v9M7.5 5.5l9 5V15"/>',
 truck:'<path d="M3 6h11v12H7M14 10h4l3 4v4h-3M14 18h-3M3 10H1M3 14H1"/><circle cx="8" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
 building:'<path d="M4 21V4h12v17M16 11h4v10M2 21h20M8 8h1M12 8h1M8 12h1M12 12h1M8 16h1M12 16h1"/>',
 chart:'<path d="M4 3v18h17M8 16v-4M13 16V7M18 16v-7"/>',
 folder:'<path d="M3 7V5h6l2 2h10v13H3V7Z"/>',
 spark:'<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3ZM20 2v4M18 4h4"/>',
 settings:'<path d="m10 3-1 3-3 1-3 3 2 2-1 3 3 3 3-1 2 4 3-1 1-3 3-1 2-3-2-2 1-3-3-3-3 1-2-3Z"/><circle cx="12" cy="12" r="3"/>',
 menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
 bell:'<path d="M6 9a6 6 0 0 1 12 0c0 7 3 7 3 8H3c0-1 3-1 3-8ZM10 21h4"/>',
 refresh:'<path d="M20 7v5h-5M4 17v-5h5M19 8a8 8 0 0 0-14-2M5 16a8 8 0 0 0 14 2"/>',
 download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
 filter:'<path d="M3 5h18l-7 8v6l-4 2v-8L3 5Z"/>',
 calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18M7 14h3M14 14h3"/>',
 arrow:'<path d="M6 18 18 6M6 6h12v12"/>',
 search:'<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
 plus:'<path d="M12 4v16M4 12h16"/>',
 close:'<path d="m6 6 12 12M6 18 18 6"/>',
 'arrow-up':'<path d="M12 20V4m-6 6 6-6 6 6"/>',
 check:'<path d="m5 12 4 4L19 6"/>',
 wallet:'<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M16 11h5v5h-5zM3 8h18"/>',
};
const icon = name => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.box}</svg>`;
function hydrateIcons(root=document) { $$('i[data-icon]',root).forEach(el => {el.innerHTML=icon(el.dataset.icon);}); }
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num = value => new Intl.NumberFormat('ko-KR').format(value);
const money = value => `₩${num(value)}`;
const glossary = {
 SCM:'공급망 관리(Supply Chain Management). 상품을 만들고, 보관하고, 고객에게 전달하는 전체 흐름을 관리하는 일이에요.',
 안전재고:'예상보다 주문이 많아지거나 입고가 늦어질 때를 대비해 남겨 두는 최소 여유 수량이에요. 이 데모에서는 상품·센터별로 설정한 기준을 사용해요.',
 OTD:'정시 배송률(On-Time Delivery). 배송이 끝난 주문 중 약속한 날짜 안에 도착한 주문의 비율이에요. 아직 배송 중인 주문은 계산에서 제외해요.',
 출고:'창고에서 고객에게 보낼 상품을 내보내는 일이에요. 이 화면의 출고 수량은 배송 중·배송 완료 주문의 상품 수량을 더한 값이에요.',
 SKU:'재고를 구별하기 위한 상품 코드예요. 이 데모에서는 같은 상품도 보관 센터가 다르면 별도 코드로 관리해요.',
 리드타임:'주문하거나 발주한 시점부터 상품을 받을 때까지 걸리는 시간이에요.',
 주문금액:'선택한 기간에 접수된 모든 주문의 수량 × 상품 단가를 더한 금액이에요. 배송 전 주문도 포함하므로 확정 매출과는 달라요.',
 현재고:'지금 물류센터에 보관 중인 상품 수량이에요. 기간 필터와 관계없이 현재 시점의 재고를 보여 줘요.',
};
const titles = {
 overview:['한눈에 보기','오늘의 흐름을 한눈에','복잡한 숫자는 가볍게, 중요한 일은 선명하게 확인하세요.'],
 orders:['주문 관리','새로운 주문, 차근차근','접수부터 배송까지, 주문의 모든 과정을 살펴보세요.'],
 inventory:['재고 관리','필요한 만큼, 알맞게','부족한 상품은 채우고, 남는 재고는 한 번 더 살펴보세요.'],
 shipments:['배송 현황','고객에게 닿는 순간까지','준비 중인 상품부터 도착한 주문까지, 배송의 흐름을 확인하세요.'],
 suppliers:['거래처','좋은 파트너와 함께','함께 일하는 거래처의 주문과 배송 약속을 살펴보세요.'],
 reports:['보고서','오늘의 흐름을 기록하세요','필요한 숫자를 담아, 함께 보기 좋은 보고서로 정리하세요.'],
 files:['이미지 보관함','영감을 모아 두는 공간','상품 사진부터 나만의 배경까지, 손쉽게 보관하고 꺼내 보세요.'],
};
const state={data:null,view:'overview',page:1,chart:'line',history:[],key:'',model:'gemini-2.5-flash',busy:false,requestId:0,images:[]};
const filters=()=>new URLSearchParams({days:$('#days').value,warehouse:$('#warehouse').value,category:$('#category').value});
let toastTimer;
function toast(message){$('#toast').textContent=message;$('#toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').hidden=true,4000);}
function statusBadge(status){const kind=['지연','재고 부족'].includes(status)?'warning':status==='배송 중'?'shipping':['출고 준비','여유 재고'].includes(status)?'preparing':'';return `<span class="badge ${kind}">${esc(status)}</span>`;}
function closeMenu(){$('#sidebar').classList.remove('open');$('#shade').hidden=true;$('#menu-toggle').setAttribute('aria-expanded','false');$('#sidebar').inert=window.innerWidth<=700;}
function switchView(view,status=''){
 if(!titles[view])return;state.view=view;state.page=1;$('#search').value='';
 const [crumb,title,description]=titles[view];$('#breadcrumb').textContent=crumb;$('#page-title').innerHTML=`${title}<span class="title-dot">.</span>`;$('#page-description').textContent=description;
 $$('.view').forEach(el=>el.hidden=true);$(`#${['orders','inventory','shipments','suppliers'].includes(view)?'list':view}-view`).hidden=false;
 $$('.nav-item[data-view]').forEach(el=>{el.classList.toggle('active',el.dataset.view===view);if(el.dataset.view===view)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
 const options=view==='inventory'?['적정','재고 부족','여유 재고']:['출고 준비','배송 중','배송 완료','지연'];
 $('#status-filter').innerHTML='<option value="">모든 상태</option>'+options.map(x=>`<option>${x}</option>`).join('');$('#status-filter').value=status;$('#status-filter').hidden=view==='suppliers';
 $('#list-title').textContent=crumb+' 목록';$('#search').placeholder=view==='suppliers'?'거래처 이름 검색':'상품명, 코드, 거래처 검색';
 $('#list-description').textContent=view==='inventory'?'현재 시점의 재고입니다. 기간 필터는 재고 수량에 영향을 주지 않습니다.':'선택한 조회 조건의 데모 데이터입니다. 항목을 누르면 상세 내용을 볼 수 있어요.';
 if(state.data)renderList();if(view==='files')renderFiles();if(view==='reports')loadAnalytics();closeMenu();window.scrollTo({top:0,behavior:'auto'});
}
async function loadAnalytics(){const period=$('#analysis-period .selected')?.dataset.period||'month';try{const res=await fetch('/api/analytics?period='+period+'&'+new URLSearchParams({warehouse:$('#warehouse').value,category:$('#category').value}));const data=await res.json();if(!res.ok)throw new Error(data.error);renderAnalytics(data);}catch(e){$('#analysis-cards').innerHTML=`<div class="error-banner">${esc(e.message||'분석을 불러오지 못했어요.')}</div>`;}}
function renderAnalytics(data){const f=data.forecast,k=data.kpi;$('#analysis-cards').innerHTML=[['예상 주문',num(f.orders)+'건','최근 3개 구간 평균'],['예상 수량',num(f.quantity)+'개','다음 구간 참고치'],['예상 주문금액',money(f.amount),'확정 매출 아님'],['예상 정시배송률',f.otd===null?'—':f.otd+'%','단순 추정']].map(x=>`<div class="analysis-card"><small>${x[0]}</small><strong>${x[1]}</strong><span>${x[2]}</span></div>`).join('');$('#analysis-table').innerHTML=`<div class="table-scroll"><table><thead><tr><th>구간</th><th>주문 건수</th><th>수량</th><th>주문금액</th><th>지연</th><th>OTD</th></tr></thead><tbody>${data.rows.map(r=>`<tr><td><strong>${esc(r.period)}</strong></td><td>${num(r.orders)}건</td><td>${num(r.quantity)}개</td><td>${money(r.amount)}</td><td>${r.delayed}건</td><td>${r.otd===null?'—':r.otd+'%'}</td></tr>`).join('')}</tbody></table></div>`;const achieve=(actual,target,inverse=false)=>actual===null?'—':Math.round((inverse?target/Math.max(actual,.1):actual/target)*100)+'%';$('#kpi-grid').innerHTML=[['주문 처리 목표',num(k.actual_orders)+' / '+num(k.target_orders)+'건',achieve(k.actual_orders,k.target_orders)],['정시 배송 목표',k.actual_otd===null?'—':k.actual_otd+'% / '+k.target_otd+'%',achieve(k.actual_otd,k.target_otd)],['지연률 목표',k.actual_delay_rate===null?'—':k.actual_delay_rate+'% / '+k.target_delay_rate+'%',achieve(k.actual_delay_rate,k.target_delay_rate,true)]].map(x=>`<div class="kpi-item"><span>${x[0]}</span><strong>${x[1]}</strong><b>${x[2]}</b></div>`).join('');hydrateIcons();}
async function loadData(){
 const id=++state.requestId;$('#refresh').disabled=true;$('#updated').textContent='데이터를 불러오는 중…';$('#error-banner').hidden=true;
 try{const res=await fetch('/api/dashboard?'+filters());const data=await res.json();if(!res.ok)throw new Error(data.error||'데이터를 불러오지 못했어요.');if(id!==state.requestId)return;state.data=data;state.page=1;renderDashboard();renderList();$('#updated').textContent=`${data.date.replaceAll('-','.')} 기준 · 방금 업데이트`;}
 catch(error){if(id===state.requestId){$('#error-banner').textContent=error.message+' 새로고침으로 다시 시도해 주세요.';$('#error-banner').hidden=false;$('#updated').textContent='업데이트 실패 · 이전 데이터가 표시될 수 있어요';}}
 finally{if(id===state.requestId)$('#refresh').disabled=false;}
}
function renderDashboard(){
 const d=state.data,m=d.metrics;$('#order-count').textContent=m.orders;$('#low-count').textContent=m.low_stock;$('#delay-count').textContent=m.delayed;
 $('#hero-summary').textContent=`최근 ${d.days}일, ${num(m.orders)}건의 주문이 들어왔어요. ${m.low_stock?`재고 ${m.low_stock}개 항목을 먼저 확인해 볼까요?`:'선택한 상품의 재고는 모두 기준 이상이에요.'}`;
 const cards=[
 {title:'접수된 주문',value:num(m.orders),unit:'건',icon:'bag',note:`최근 ${d.days}일`,sub:'선택한 조건 기준'},
 {title:'현재고',value:num(m.stock),unit:'개',icon:'box',note:`부족 ${m.low_stock}개 항목`,sub:'현재 시점',term:'현재고',warn:m.low_stock>0},
 {title:'정시 배송률',value:m.otd===null?'—':m.otd,unit:'%',icon:'truck',note:'OTD',sub:'배송 완료 주문 기준',term:'OTD'},
 {title:'주문금액',value:(m.revenue/10000).toLocaleString('ko-KR',{maximumFractionDigits:1}),unit:'만원',icon:'wallet',note:`최근 ${d.days}일`,sub:'확정 매출과 다름',term:'주문금액'},
 ];
 $('#metrics').innerHTML=cards.map(c=>`<article class="metric"><div class="metric-top"><span>${c.term?`<button class="term" data-term="${c.term}">${c.title}</button>`:c.title}</span><i data-icon="${c.icon}"></i></div><div class="metric-value">${c.value}<small>${c.unit}</small></div><div class="metric-bottom"><span class="metric-note ${c.warn?'warn':''}">${c.note}</span><span>${c.sub}</span></div></article>`).join('');
 renderChart();renderDonut();$('#recent-table').innerHTML=orderTable(d.orders.slice(0,5));hydrateIcons();
}
function renderChart(){
 if(!state.data)return;const trend=state.data.trend;const total=trend.reduce((s,r)=>s+r.orders,0);$('#chart-total').innerHTML=`${num(total)}<small>개 주문</small>`;
 const W=Math.max(300,$('#trend-chart').clientWidth),H=180,L=35,R=16,T=12,B=27;const max=Math.max(100,...trend.map(r=>r.orders));const top=Math.ceil(max/100)*100;const x=i=>L+(W-L-R)*(i/Math.max(1,trend.length-1));const y=v=>T+(H-T-B)*(1-v/top);
 let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="최근 ${trend.length}일 주문 수량 ${num(total)}개. 날짜별 상세는 그래프에서 확인할 수 있습니다."><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#b4cb93" stop-opacity=".3"/><stop offset="100%" stop-color="#b4cb93" stop-opacity="0"/></linearGradient></defs>`;
 for(let i=0;i<=3;i++){const value=top*i/3;svg+=`<line x1="${L}" y1="${y(value)}" x2="${W-R}" y2="${y(value)}" stroke="#edf0e7" stroke-dasharray="3 4"/><text x="${L-8}" y="${y(value)+3}" text-anchor="end">${Math.round(value)}</text>`;}
 if(state.chart==='line'){
 const points=key=>trend.map((r,i)=>`${x(i)},${y(r[key])}`).join(' ');
 svg+=`<polygon points="${L},${H-B} ${points('orders')} ${W-R},${H-B}" fill="url(#area)"/><polyline points="${points('shipped')}" fill="none" stroke="#c3d799" stroke-width="2.5" stroke-dasharray="5 4" stroke-linejoin="round"/><polyline points="${points('orders')}" fill="none" stroke="#567c48" stroke-width="2.6" stroke-linejoin="round"/>`;
 }else{const bw=Math.min(18,(W-L-R)/trend.length*.35);trend.forEach((r,i)=>{const cx=L+(W-L-R)*(i+.5)/trend.length;svg+=`<rect x="${cx-bw}" y="${y(r.orders)}" width="${bw}" height="${H-B-y(r.orders)}" rx="2" fill="#60844e"/><rect x="${cx+2}" y="${y(r.shipped)}" width="${bw}" height="${H-B-y(r.shipped)}" rx="2" fill="#c3d799"/>`;});}
 trend.forEach((r,i)=>{const cx=state.chart==='line'?x(i):L+(W-L-R)*(i+.5)/trend.length;const label=`${r.date.slice(5).replace('-','/')} · 주문 ${num(r.orders)}개 · 출고 ${num(r.shipped)}개`;const hit=Math.max(10,(W-L-R)/trend.length);svg+=`<g class="chart-point" tabindex="0" role="button" aria-label="${label}" data-chart-detail="${esc(label)}"><line class="hit-line" x1="${cx}" y1="${T}" x2="${cx}" y2="${H-B}" stroke="transparent"/><rect x="${cx-hit/2}" y="${T}" width="${hit}" height="${H-T-B}" fill="transparent"/><title>${label}</title></g>`;if(i%Math.ceil(trend.length/7)===0||i===trend.length-1)svg+=`<text x="${cx}" y="${H-6}" text-anchor="middle">${r.date.slice(5).replace('-','/')}</text>`;});
 $('#trend-chart').innerHTML=svg+'</svg>';
}
function renderDonut(){const rows=state.data.orders,total=rows.length;const statuses=['배송 완료','배송 중','출고 준비','지연'];const colors=['#50764d','#a3b88a','#dee7cd','#d9c49a'];let from=0;const segments=[];$('#status-legend').innerHTML=statuses.map((s,i)=>{const count=rows.filter(r=>r.status===s).length;const to=from+(total?count/total*100:0);segments.push(`${colors[i]} ${from}% ${to}%`);from=to;return `<button data-shipment-status="${s}"><b class="legend-dot" style="background:${colors[i]}"></b>${s}<strong>${count}<small> 건</small></strong></button>`;}).join('');$('#donut').style.background=total?`conic-gradient(${segments.join(',')})`:'#edf0e7';$('#donut-total').textContent=total;}
function orderTable(rows){if(!rows.length)return '<div class="empty-state"><strong>조건에 맞는 주문이 없어요.</strong>검색어나 조회 조건을 바꾸어 보세요.</div>';return `<table><thead><tr><th>주문번호</th><th>상품명</th><th>물류센터</th><th>수량</th><th>주문일</th><th>배송 상태</th><th aria-label="상세"></th></tr></thead><tbody>${rows.map(r=>`<tr><td><button class="row-link" data-order="${r.id}">${r.id}</button></td><td><span class="product-cell"><span class="product-tile">${icon(r.category==='디지털'?'box':r.category==='리빙'?'bag':'folder')}</span><strong>${esc(r.product)}</strong></span></td><td>${r.warehouse}</td><td>${num(r.quantity)}개</td><td>${r.date.slice(2).replaceAll('-','.')}</td><td>${statusBadge(r.status)}</td><td><button class="icon-button" data-order="${r.id}" aria-label="${r.id} 상세">${icon('arrow')}</button></td></tr>`).join('')}</tbody></table>`;}
function renderList(){
 if(!state.data)return;const view=state.view;if(!['orders','inventory','shipments','suppliers'].includes(view))return;
 const q=$('#search').value.trim().toLowerCase(),status=$('#status-filter').value;let rows=view==='inventory'?state.data.inventory:view==='suppliers'?state.data.suppliers:state.data.orders;
 rows=rows.filter(r=>Object.values(r).some(v=>String(v).toLowerCase().includes(q))&&(!status||view==='suppliers'||r.status===status));const total=rows.length,pages=Math.max(1,Math.ceil(total/10));state.page=Math.min(state.page,pages);rows=rows.slice((state.page-1)*10,state.page*10);
 let table;
 if(view==='inventory')table=`<table><thead><tr><th><button class="term" data-term="SKU">SKU</button></th><th>상품명</th><th>물류센터</th><th>현재고</th><th><button class="term" data-term="안전재고">안전재고</button></th><th>상태</th></tr></thead><tbody>${rows.map(r=>`<tr><td><button class="row-link" data-inventory="${r.id}">${r.id}</button></td><td><strong>${r.product}</strong></td><td>${r.warehouse}</td><td>${num(r.stock)}개</td><td>${num(r.safety)}개</td><td>${statusBadge(r.status)}</td></tr>`).join('')}</tbody></table>`;
 else if(view==='suppliers')table=`<table><thead><tr><th>거래처</th><th>취급 상품</th><th>접수 주문</th><th>주문금액</th><th><button class="term" data-term="OTD">정시 배송률</button></th></tr></thead><tbody>${rows.map(r=>`<tr><td><button class="row-link" data-supplier="${r.name}">${r.name}</button></td><td>${r.products}종</td><td>${r.orders}건</td><td>${money(r.amount)}</td><td>${r.rate===null?'완료 주문 없음':r.rate+'%'}</td></tr>`).join('')}</tbody></table>`;
 else table=orderTable(rows);
 $('#list-table').innerHTML=rows.length?table:'<div class="empty-state"><strong>조건에 맞는 항목이 없어요.</strong>검색어나 상태 필터를 바꾸어 보세요.</div>';$('#result-count').textContent=`전체 ${num(total)}개 항목`;$('#page-number').textContent=`${state.page} / ${pages}`;$('#prev-page').disabled=state.page===1;$('#next-page').disabled=state.page>=pages;
}
function detail(title,html){$('#detail-title').textContent=title;$('#detail-content').innerHTML=html;document.body.style.overflow='hidden';$('#detail-dialog').showModal();}
function detailsGrid(pairs){return `<dl class="detail-grid">${pairs.map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>`;}
function showOrder(id){const r=state.data?.orders.find(r=>r.id===id);if(!r)return;detail('주문 '+r.id,statusBadge(r.status)+detailsGrid([['상품',r.product],['카테고리',r.category],['주문일',r.date],['물류센터',r.warehouse],['수량',num(r.quantity)+'개'],['주문금액',money(r.amount)],['거래처',r.supplier],['배송지',r.destination]])+`<p class="detail-note">${r.status==='지연'?'배송이 예정일보다 늦어졌어요. 담당 거래처에 출고·배송 일정을 확인해 보세요.':r.status==='배송 완료'?(r.on_time?'약속한 날짜 안에 배송을 완료한 주문이에요.':'배송은 완료되었지만 약속한 날짜보다 늦게 도착했어요.'):'상품이 고객에게 전달되는 과정을 확인 중이에요.'} 이 내역은 데모 데이터입니다.</p>`);}
function showInventory(id){const r=state.data?.inventory.find(r=>r.id===id);if(!r)return;detail(r.product,statusBadge(r.status)+detailsGrid([['상품 코드',r.id],['물류센터',r.warehouse],['현재고',num(r.stock)+'개'],['안전재고',num(r.safety)+'개'],['거래처',r.supplier],['상품 단가',money(r.price)]])+`<p class="detail-note">${r.stock<r.safety?`설정된 안전재고보다 ${r.safety-r.stock}개 부족해요. 판매 속도와 입고 일정을 확인한 뒤 보충 수량을 결정하세요.`:'설정된 안전재고 이상을 보유하고 있어요.'} 데모 기준이며 실제 발주를 실행하지 않습니다.</p>`);}
function showSupplier(name){const r=state.data?.suppliers.find(r=>r.name===name);if(!r)return;detail(name,detailsGrid([['취급 상품',r.products+'종'],['접수 주문',r.orders+'건'],['주문금액',money(r.amount)],['정시 배송률',r.rate===null?'완료 주문 없음':r.rate+'%']])+'<p class="detail-note">선택한 기간·센터·카테고리의 주문을 집계한 데모 거래처 정보입니다.</p>');}
function showPriorities(){if(!state.data)return;detail('먼저 확인하면 좋은 일',`<p class="muted">선택한 조회 조건 기준입니다.</p><button class="priority-row" data-priority="inventory"><span class="priority-icon amber">${icon('box')}</span><span><strong>보충이 필요한 재고</strong><small>안전재고보다 부족한 항목</small></span><b>${state.data.metrics.low_stock}개</b><span>↗</span></button><button class="priority-row" data-priority="shipments"><span class="priority-icon coral">${icon('truck')}</span><span><strong>지연된 배송</strong><small>거래처와 일정을 확인해 보세요</small></span><b>${state.data.metrics.delayed}건</b><span>↗</span></button>`);}
function exportReport(){window.location.assign('/api/export?'+filters());toast('선택한 조회 조건의 CSV 보고서를 다운로드합니다.');}
function showGlossary(){detail('쉽게 읽는 SCM 용어 사전',`<div class="glossary-grid">${Object.entries(glossary).map(([k,v])=>`<div class="glossary-entry"><strong>${k}</strong><p>${v}</p></div>`).join('')}</div>`);}
let tipOwner=null;
function showTip(el){const text=glossary[el.dataset.term]||el.dataset.chartDetail;if(!text)return;tipOwner=el;const tip=$('#tooltip');tip.textContent=text;tip.hidden=false;el.setAttribute('aria-describedby','tooltip');const rect=el.getBoundingClientRect();const x=Math.max(12,Math.min(rect.left,window.innerWidth-tip.offsetWidth-12));let y=rect.bottom+9;if(y+tip.offsetHeight>window.innerHeight-12)y=Math.max(12,rect.top-tip.offsetHeight-9);tip.style.left=x+'px';tip.style.top=y+'px';}
function hideTip(){if(tipOwner)tipOwner.removeAttribute('aria-describedby');tipOwner=null;$('#tooltip').hidden=true;}

// Images stay in IndexedDB on this browser. No image bytes go to the Flask server.
let database;
async function db(){if(database)return database;database=await new Promise((resolve,reject)=>{const r=indexedDB.open('flow-scm-images',1);r.onupgradeneeded=()=>r.result.createObjectStore('images',{keyPath:'id'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});return database;}
async function imageOp(mode,callback){const database=await db();return new Promise((resolve,reject)=>{const tx=database.transaction('images',mode),r=callback(tx.objectStore('images'));tx.oncomplete=()=>resolve(r?.result);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);});}
const urls=new Map();
async function renderFiles(){try{state.images=await imageOp('readonly',s=>s.getAll());for(const url of urls.values())URL.revokeObjectURL(url);urls.clear();$('#files-grid').innerHTML=state.images.length?state.images.map(r=>{const url=URL.createObjectURL(r.blob);urls.set(r.id,url);return `<article class="image-card"><img src="${url}" alt="${esc(r.name)}"><div><strong>${esc(r.name)}</strong><div class="image-actions"><button data-image-preview="${r.id}">크게 보기</button><button data-image-background="${r.id}">배경으로</button><button data-image-delete="${r.id}">삭제</button></div></div></article>`;}).join(''):'<div class="empty-state"><strong>아직 보관한 이미지가 없어요.</strong>첫 번째 이미지를 추가해 보세요.</div>';}catch{toast('브라우저 저장소를 사용할 수 없어요. 브라우저 설정을 확인해 주세요.');}}
async function addImages(files){let added=0;for(const file of files){if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size>5*1024*1024){toast('PNG, JPG, WebP 형식의 5MB 이하 이미지만 추가할 수 있어요.');continue;}try{const bitmap=await createImageBitmap(file);const tooBig=bitmap.width*bitmap.height>40_000_000;bitmap.close();if(tooBig){toast('이미지는 4,000만 화소 이하로 선택해 주세요.');continue;}await imageOp('readwrite',s=>s.put({id:crypto.randomUUID(),name:file.name,blob:file,created:Date.now()}));added++;}catch(error){toast(error?.name==='QuotaExceededError'?'브라우저 저장 공간이 부족합니다. 불필요한 이미지를 먼저 삭제해 주세요.':'이미지를 읽거나 저장하지 못했어요. 파일과 저장 공간을 확인해 주세요.');}}await renderFiles();if(added)toast(`${added}개의 이미지를 이 브라우저에 보관했어요.`);$('#file-input').value='';}
let bgUrl;
function clearBackground(){if(bgUrl)URL.revokeObjectURL(bgUrl);bgUrl=null;document.body.classList.remove('has-background');document.body.style.removeProperty('--user-background');try{localStorage.removeItem('flow-background');}catch{}}
async function setBackground(id){try{const image=await imageOp('readonly',s=>s.get(id));if(!image)return;clearBackground();bgUrl=URL.createObjectURL(image.blob);document.body.style.setProperty('--user-background',`url("${bgUrl}")`);document.body.classList.add('has-background');localStorage.setItem('flow-background',id);}catch{toast('배경 설정을 저장하지 못했어요.');}}
function applyTheme(theme){if(!['sage','ocean','sand'].includes(theme))theme='sage';document.body.dataset.theme=theme;$$('[data-theme]').filter(el=>el!==document.body).forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.theme===theme)));try{localStorage.setItem('flow-theme',theme);}catch{}}
function settings(){if($('#chat-dialog').open)$('#chat-dialog').close();document.body.style.overflow='hidden';$('#settings-dialog').showModal();}
function chat(){if(!$('#chat-dialog').open){document.body.style.overflow='hidden';$('#chat-dialog').showModal();}$('#chat-input').focus();}
function chatMessage(text,kind){const el=document.createElement('div');el.className='message '+kind;el.textContent=text;$('#chat-messages').append(el);el.scrollIntoView({block:'nearest'});return el;}
async function sendChat(event){
 event.preventDefault();if(state.busy)return;const input=$('#chat-input'),message=input.value.trim();if(!message)return;if(!state.key){toast('연결 설정에서 본인의 Gemini API 키를 입력해 주세요.');return;}
 state.busy=true;$('#chat-send').disabled=true;$('#new-chat').disabled=true;input.value='';chatMessage(message,'user');const pending=chatMessage('현재 흐름을 살펴보고 있어요…','assistant');const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),50000);
 try{const response=await fetch('/api/chat?'+filters(),{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':$('meta[name="csrf-token"]').content},body:JSON.stringify({message,api_key:state.key,model:state.model,history:state.history.slice(-6)}),signal:controller.signal});const data=await response.json();if(!response.ok)throw new Error(data.error||'답변을 받지 못했어요.');pending.textContent=data.answer;state.history.push({role:'user',text:message},{role:'model',text:data.answer.slice(0,4000)});state.history=state.history.slice(-6);}
 catch(error){pending.textContent=error.name==='AbortError'?'응답 시간이 길어지고 있어요. 잠시 후 다시 시도해 주세요.':error.message;pending.classList.add('error');input.value=message;}
 finally{clearTimeout(timer);state.busy=false;$('#chat-send').disabled=false;$('#new-chat').disabled=false;pending.scrollIntoView({block:'nearest'});}
}
document.addEventListener('click',async event=>{
 const el=event.target.closest('button,[data-chart-detail]');if(!el){if(!event.target.closest('#tooltip'))hideTip();return;}
 if(el.dataset.view)switchView(el.dataset.view);
 if(el.dataset.action){({chat,settings,glossary:showGlossary,notifications:showPriorities,export:exportReport}[el.dataset.action])?.();}
 if(el.hasAttribute('data-close'))el.closest('dialog').close();
 if(el.dataset.order)showOrder(el.dataset.order);
 if(el.dataset.inventory)showInventory(el.dataset.inventory);
 if(el.dataset.supplier)showSupplier(el.dataset.supplier);
 if(el.dataset.shipmentStatus)switchView('shipments',el.dataset.shipmentStatus);
 if(el.dataset.priority){$('#detail-dialog').close();switchView(el.dataset.priority,el.dataset.priority==='inventory'?'재고 부족':'지연');}
 if(el.dataset.chart){state.chart=el.dataset.chart;$$('[data-chart]').forEach(b=>{b.classList.toggle('selected',b===el);b.setAttribute('aria-pressed',String(b===el));});renderChart();}
 if(el.dataset.term||el.dataset.chartDetail)showTip(el);else hideTip();
 if(el.dataset.theme)applyTheme(el.dataset.theme);
 if(el.dataset.prompt){$('#chat-input').value=el.dataset.prompt;$('#chat-input').focus();}
 if(el.dataset.imagePreview){const r=state.images.find(x=>x.id===el.dataset.imagePreview);if(r)detail(r.name,`<img class="detail-image" src="${urls.get(r.id)}" alt="${esc(r.name)}">`);}
 if(el.dataset.imageBackground){await setBackground(el.dataset.imageBackground);toast('첫 화면의 배경으로 적용했어요.');}
 if(el.dataset.imageDelete){try{await imageOp('readwrite',s=>s.delete(el.dataset.imageDelete));if(localStorage.getItem('flow-background')===el.dataset.imageDelete)clearBackground();await renderFiles();toast('이미지를 보관함에서 삭제했어요.');}catch{toast('이미지를 삭제하지 못했어요.');}}
});
document.addEventListener('pointerover',e=>{const el=e.target.closest('[data-term],[data-chart-detail]');if(el)showTip(el);});
document.addEventListener('pointerout',e=>{if(e.target.closest('[data-term],[data-chart-detail]')&&!e.target.closest('[data-term],[data-chart-detail]').contains(e.relatedTarget))hideTip();});
document.addEventListener('focusin',e=>{if(e.target.matches('[data-term],[data-chart-detail]'))showTip(e.target);});
document.addEventListener('focusout',hideTip);document.addEventListener('scroll',hideTip,true);
document.addEventListener('keydown',e=>{if(e.key==='Escape'){hideTip();closeMenu();}if((e.key==='Enter'||e.key===' ')&&e.target.matches('[data-chart-detail]')){e.preventDefault();showTip(e.target);}});
$('#menu-toggle').addEventListener('click',()=>{const open=$('#sidebar').classList.toggle('open');$('#sidebar').inert=!open;$('#shade').hidden=!open;$('#menu-toggle').setAttribute('aria-expanded',String(open));if(open)$('.nav-item.active').focus();});$('#shade').addEventListener('click',closeMenu);
$('#refresh').addEventListener('click',loadData);$('#export').addEventListener('click',exportReport);['days','warehouse','category'].forEach(id=>$('#'+id).addEventListener('change',loadData));
$('#view-priorities').addEventListener('click',showPriorities);$('#priority-stock').addEventListener('click',()=>switchView('inventory','재고 부족'));$('#priority-delivery').addEventListener('click',()=>switchView('shipments','지연'));
$('#search').addEventListener('input',()=>{state.page=1;renderList();});$('#status-filter').addEventListener('change',()=>{state.page=1;renderList();});$('#prev-page').addEventListener('click',()=>{state.page--;renderList();});$('#next-page').addEventListener('click',()=>{state.page++;renderList();});
$('#print-report').addEventListener('click',()=>{switchView('overview');requestAnimationFrame(()=>window.print());});
$('#analysis-period').addEventListener('click',e=>{const b=e.target.closest('[data-period]');if(!b)return;$$('[data-period]').forEach(x=>x.classList.toggle('selected',x===b));loadAnalytics();});
$('#file-input').addEventListener('change',e=>addImages(e.target.files));$('#drop-zone').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('#file-input').click();}});$('#drop-zone').addEventListener('dragover',e=>{e.preventDefault();e.currentTarget.classList.add('dragging');});$('#drop-zone').addEventListener('dragleave',e=>e.currentTarget.classList.remove('dragging'));$('#drop-zone').addEventListener('drop',e=>{e.preventDefault();e.currentTarget.classList.remove('dragging');addImages(e.dataTransfer.files);});
$('#clear-background').addEventListener('click',()=>{clearBackground();toast('기본 배경으로 돌아왔어요.');});
$('#save-settings').addEventListener('click',()=>{const key=$('#api-key').value.trim(),model=$('#model-id').value.trim();if(key&&(!/^\S{10,256}$/.test(key)||!/^gemini-[a-zA-Z0-9.\-]{1,70}$/.test(model))){toast('API 키와 Gemini 모델 ID를 확인해 주세요.');return;}state.key=key;state.model=model;$('#key-status').textContent=key?'API 키 입력됨 · 전송 시 연결 확인':'Gemini API 키를 연결해 주세요';$('#settings-dialog').close();toast('설정을 적용했어요.');});
$('#forget-key').addEventListener('click',()=>{state.key='';$('#api-key').value='';$('#key-status').textContent='Gemini API 키를 연결해 주세요';toast('API 키를 지웠어요.');});$('#chat-settings').addEventListener('click',settings);$('#chat-form').addEventListener('submit',sendChat);
$('#chat-input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('#chat-form').requestSubmit();}});$('#new-chat').addEventListener('click',()=>{if(state.busy)return;state.history=[];$('#chat-messages').replaceChildren();chatMessage('새로운 대화를 시작했어요. 무엇이 궁금하세요?','assistant');});
const modalFocusables='button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
$$('dialog').forEach(d=>{d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}});d.addEventListener('close',()=>{if(!$$('dialog[open]').length)document.body.style.overflow='';});d.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const els=$$(modalFocusables,d);if(!els.length)return;const first=els[0],last=els[els.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});d.addEventListener('cancel',()=>{if(!$$('dialog[open]').length)document.body.style.overflow='';});});
$('#report-glossary').innerHTML=['SCM','안전재고','OTD','주문금액'].map(k=>`<div class="glossary-entry"><strong>${k}</strong><p>${glossary[k]}</p></div>`).join('');
try{applyTheme(localStorage.getItem('flow-theme')||'sage');const bg=localStorage.getItem('flow-background');if(bg)setBackground(bg);}catch{applyTheme('sage');}
let resizeTimer;
window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{closeMenu();if(state.data)renderChart();},150);});
closeMenu();hydrateIcons();loadData();
