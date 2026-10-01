#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/jobs.json → public/jobs/index.html + public/jobs/data.json (공고 레이더 대시보드).

    python3 jobs/build_page.py                      # 기본 경로
    python3 jobs/build_page.py --data X --out DIR --title "..." [--analytics]
정적 한 페이지. 필터·정렬은 브라우저에서. 검색 노출 안 되게 noindex.
"""
import argparse, html, json, os
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYTICS = ('<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments);};</script>'
             '<script defer src="/_vercel/insights/script.js"></script>')

PAGE = r'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>%(title)s</title>%(analytics)s
<style>
:root{--page:#f8f6f4;--surface:#fff;--surface-2:#f4f1ee;--ink:#1f1a17;--ink2:#4a403a;--muted:#8a7d75;--line:#e6dfda;--accent:#d9481c;--accent-soft:#fde6d8;--new:#0f766e}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--page:#14100e;--surface:#1d1815;--surface-2:#27201c;--ink:#f1ebe6;--ink2:#cdbfb5;--muted:#9a8b81;--line:#3a302a;--accent:#ff7a45;--accent-soft:#3a2418;--new:#5eead4}}
:root[data-theme="dark"]{--page:#14100e;--surface:#1d1815;--surface-2:#27201c;--ink:#f1ebe6;--ink2:#cdbfb5;--muted:#9a8b81;--line:#3a302a;--accent:#ff7a45;--accent-soft:#3a2418;--new:#5eead4}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:15px/1.6 -apple-system,"Pretendard","Apple SD Gothic Neo","Noto Sans KR",sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:36px 16px 80px}
h1{font-size:1.6rem;margin:0 0 4px}.sub{color:var(--muted);font-size:.9rem;margin-bottom:18px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 18px}.stat{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 14px;min-width:120px}
.stat b{display:block;font-size:1.3rem}.stat span{color:var(--muted);font-size:.8rem}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.bar input,.bar select{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink)}
.chip{border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:.82rem;cursor:pointer;background:var(--surface);color:var(--ink2)}.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.job{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:8px;display:grid;grid-template-columns:52px 1fr auto;gap:10px;align-items:start}
.sc{font-weight:700;font-size:1.15rem;color:var(--accent);text-align:center;padding-top:2px}
.job .t{font-weight:600}.job .t a{color:inherit;text-decoration:none}.job .t a:hover{text-decoration:underline}
.job .m{color:var(--ink2);font-size:.88rem;margin-top:2px}.job .w{color:var(--muted);font-size:.78rem;margin-top:4px}
.job .r{text-align:right;font-size:.8rem;color:var(--muted);white-space:nowrap}
.tag{display:inline-block;background:var(--surface-2);border-radius:6px;padding:1px 7px;font-size:.76rem;margin-right:4px;color:var(--ink2)}
.tag.new{background:var(--new);color:#fff}.tag.due{background:var(--accent-soft);color:var(--accent)}
.empty{color:var(--muted);padding:30px;text-align:center}
footer{margin-top:40px;color:var(--muted);font-size:.8rem}
@media(max-width:600px){.job{grid-template-columns:44px 1fr}.job .r{grid-column:2;text-align:left}}
</style></head><body><div class="wrap">
<h1>%(title)s</h1>
<div class="sub">%(subtitle)s · 마지막 수집 %(last)s · 최근 30일 안에 보인 공고만 · 점수는 <b>규칙</b>(제목 키워드·회사·지역)으로 매긴 것이고 적합 판정이 아니에요</div>
<div class="stats"><div class="stat"><b id="n-all">0</b><span>공고</span></div><div class="stat"><b id="n-new">0</b><span>3일 안에 새로 뜸</span></div><div class="stat"><b id="n-due">0</b><span>마감 7일 이내</span></div><div class="stat"><b>%(runs)s</b><span>수집 횟수</span></div></div>
<div class="bar"><input id="q" placeholder="회사·제목 검색" style="flex:1;min-width:160px"><select id="sort"><option value="score">점수순</option><option value="new">새로 뜬 순</option><option value="due">마감 임박순</option></select><span class="chip on" data-f="all">전체</span><span class="chip" data-f="new">신규</span><span class="chip" data-f="due">마감 임박</span><span class="chip" data-f="jobkorea">잡코리아</span><span class="chip" data-f="incruit">인크루트</span><span class="chip" data-f="alio">공공기관(잡알리오)</span></div>
<div id="list"></div>
<footer>키워드 %(kws)s · 하루 1회 수집 · 개인 참고용 페이지</footer>
</div>
<script>
const J=%(data)s,TODAY="%(today)s";
const day=s=>Math.round((new Date(TODAY)-new Date(s))/864e5);
function dueDays(d){if(!d)return null;let m=d.match(/~\s*(\d{1,2})[.\/](\d{1,2})/);if(m){let y=new Date(TODAY).getFullYear();let t=new Date(y,+m[1]-1,+m[2]);if(t<new Date(TODAY)-864e5*3)t.setFullYear(y+1);return Math.round((t-new Date(TODAY))/864e5)}m=d.match(/D-(\d+)/);if(m)return +m[1];if(/오늘/.test(d))return 0;if(/내일/.test(d))return 1;return null}
let f='all';const q=document.getElementById('q'),sort=document.getElementById('sort'),list=document.getElementById('list');
function render(){const s=q.value.trim().toLowerCase();let rows=J.filter(j=>{const dd=dueDays(j.deadline),nw=day(j.first_seen)<=3;if(f==='new'&&!nw)return false;if(f==='due'&&!(dd!==null&&dd<=7))return false;if((f==='jobkorea'||f==='incruit'||f==='alio')&&j.site!==f)return false;return !s||(j.title+j.company).toLowerCase().includes(s)});
rows.sort((a,b)=>sort.value==='score'?b.score-a.score||day(a.first_seen)-day(b.first_seen):sort.value==='new'?day(a.first_seen)-day(b.first_seen)||b.score-a.score:((dueDays(a.deadline)??999)-(dueDays(b.deadline)??999))||b.score-a.score);
document.getElementById('n-all').textContent=J.length;document.getElementById('n-new').textContent=J.filter(j=>day(j.first_seen)<=3).length;document.getElementById('n-due').textContent=J.filter(j=>{const d=dueDays(j.deadline);return d!==null&&d<=7}).length;
list.innerHTML=rows.length?rows.map(j=>{const dd=dueDays(j.deadline),nw=day(j.first_seen)<=3;return `<div class="job"><div class="sc">${j.score}</div><div><div class="t"><a href="${j.url}" target="_blank" rel="noopener">${esc(j.title)}</a></div><div class="m">${esc(j.company)} · ${esc(j.region||'-')} · ${esc(j.career||'경력 미표기')}${j.badge?' · '+esc(j.badge):''}</div><div class="w">${nw?'<span class="tag new">NEW</span>':''}${dd!==null&&dd<=7?'<span class="tag due">마감 D-'+dd+'</span>':''}${j.why.map(w=>'<span class="tag">'+esc(w)+'</span>').join('')}</div></div><div class="r">${esc(j.deadline||'')}<br>${({jobkorea:'잡코리아',incruit:'인크루트',alio:'잡알리오'})[j.site]||j.site} · ${day(j.first_seen)===0?'오늘':day(j.first_seen)+'일 전'} 발견</div></div>`}).join(''):'<div class="empty">조건에 맞는 공고가 없어요</div>'}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));c.classList.add('on');f=c.dataset.f;render()});q.oninput=render;sort.onchange=render;render();
</script></body></html>'''


def build(data_path, out_dir, title, subtitle, analytics):
    store = json.load(open(data_path, encoding='utf-8')) if os.path.exists(data_path) else {'jobs': {}, 'runs': []}  # 아직 수집 전이면 빈 페이지
    jobs = [j for j in store['jobs'].values()]
    cfg_kws = sorted({k for j in jobs for k in j.get('kw', [])})
    last = store['runs'][-1]['date'] if store['runs'] else '-'
    os.makedirs(out_dir, exist_ok=True)
    json.dump(jobs, open(os.path.join(out_dir, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    page = PAGE % dict(title=html.escape(title), subtitle=html.escape(subtitle), last=last, runs=len(store['runs']),
                       kws=html.escape(' · '.join(cfg_kws)), data=json.dumps(jobs, ensure_ascii=False).replace('</', '<\\/'),
                       today=date.today().isoformat(), analytics=ANALYTICS if analytics else '')
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(page)
    print('OK', os.path.join(out_dir, 'index.html'), len(jobs), 'jobs')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=os.path.join(HERE, 'data', 'jobs.json'))
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'public', 'jobs'))
    ap.add_argument('--title', default='공고 레이더')
    ap.add_argument('--subtitle', default='잡코리아·인크루트·잡알리오(공공기관)에서 내 기준으로 거른 공고')
    ap.add_argument('--analytics', action='store_true')
    a = ap.parse_args()
    build(a.data, a.out, a.title, a.subtitle, a.analytics)
