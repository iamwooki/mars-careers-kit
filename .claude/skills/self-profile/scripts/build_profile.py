#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""self-profile.yaml + inventory 카드 → self-profile.html ("사용 설명서": 나는 어떤 사람이고 무엇을 할 수 있는가)

사용:  python build_profile.py [프로젝트 루트]
원칙:  self-profile.html은 생성물이다 — 직접 수정 금지. 내용은 self-profile.yaml에서 고친다.
       성적·재직 정보·내부 업무가 들어가는 비공개 문서다. site/에 넣지 않는다.

글 안에서 쓸 수 있는 가벼운 표기:
  [P07]            카드 번호 칩
  {사실} {해석} {빈칸} {내부} {주의}     배지.  {사실:내 것}처럼 쓰면 색은 '사실', 글자는 '내 것'
  **굵게**
"""
import sys, os, re, html, glob, datetime
import yaml

CSS = '''
  :root {
    --bg:#fafbfc; --panel:#ffffff; --text:#1f2328; --muted:#656d76; --line:#e3e6ea;
    --accent:#1a73e8; --accent-soft:#e8f0fe; --good:#1a7f4b; --good-soft:#e6f4ec;
    --warn:#9a6700; --warn-soft:#fff5d6; --bad:#b3261e; --bad-soft:#fdecea; --chip:#f1f3f5;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#0f1216; --panel:#171b21; --text:#dde2e8; --muted:#8e98a4; --line:#2a313a;
      --accent:#8ab4f8; --accent-soft:#1c2a41; --good:#6fd39b; --good-soft:#15291f;
      --warn:#e3b341; --warn-soft:#2e2611; --bad:#ff8a80; --bad-soft:#2f1a19; --chip:#222831; }
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  html { scroll-behavior:smooth; }
  body { font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic","맑은 고딕",system-ui,sans-serif;
    background:var(--bg); color:var(--text); line-height:1.75; font-size:15.5px;
    word-break:keep-all; overflow-wrap:break-word; -webkit-font-smoothing:antialiased; }
  a { color:var(--accent); text-decoration:none; } a:hover { text-decoration:underline; }
  .layout { display:grid; grid-template-columns:230px minmax(0,1fr); max-width:1240px; margin:0 auto; }
  nav { position:sticky; top:0; align-self:start; height:100vh; overflow-y:auto; padding:28px 14px 28px 22px;
    border-right:1px solid var(--line); font-size:0.88rem; }
  nav .who { font-weight:700; font-size:1rem; margin-bottom:2px; }
  nav .sub { color:var(--muted); font-size:0.8rem; margin-bottom:18px; }
  nav a { display:block; color:var(--muted); padding:5px 8px; border-radius:6px; }
  nav a:hover { background:var(--chip); color:var(--text); text-decoration:none; }
  nav .grp { margin:14px 0 4px 8px; font-size:0.72rem; letter-spacing:0.06em; color:var(--muted); text-transform:uppercase; }
  main { padding:40px 40px 80px; min-width:0; }
  section { margin-bottom:56px; scroll-margin-top:20px; }
  h1 { font-size:1.9rem; line-height:1.3; letter-spacing:-0.5px; }
  h2 { font-size:1.3rem; margin-bottom:6px; padding-bottom:8px; border-bottom:1px solid var(--line); letter-spacing:-0.3px; }
  h2 .no { color:var(--accent); margin-right:8px; font-variant-numeric:tabular-nums; }
  h3 { font-size:1.02rem; margin:22px 0 8px; }
  p { margin-bottom:12px; }
  .lead { color:var(--muted); margin:6px 0 18px; font-size:0.95rem; }
  .hero { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:30px 32px; margin-bottom:24px; }
  .hero .tag { color:var(--accent); font-weight:600; font-size:0.85rem; margin-bottom:8px; }
  .hero p.big { font-size:1.08rem; line-height:1.85; margin-top:14px; }
  .legend { display:flex; flex-wrap:wrap; gap:8px 16px; font-size:0.82rem; color:var(--muted); margin-top:14px; }
  .badge { display:inline-block; font-size:0.72rem; font-weight:600; padding:1px 8px; border-radius:999px; vertical-align:middle; white-space:nowrap; }
  .b-fact { background:var(--good-soft); color:var(--good); }
  .b-view { background:var(--accent-soft); color:var(--accent); }
  .b-gap { background:var(--warn-soft); color:var(--warn); }
  .b-int { background:var(--chip); color:var(--muted); }
  .tiles { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:18px 0 6px; }
  .tile { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px 16px; }
  .tile .n { font-size:1.55rem; font-weight:700; letter-spacing:-0.5px; line-height:1.2; font-variant-numeric:tabular-nums; }
  .tile .l { font-size:0.82rem; color:var(--muted); line-height:1.45; margin-top:4px; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px 20px; margin-bottom:14px; }
  .card h3 { margin-top:0; }
  .card .ev { font-size:0.88rem; color:var(--muted); margin-top:8px; }
  .card ul, .plain { padding-left:18px; margin:6px 0 4px; }
  .card li, .plain li { margin-bottom:4px; }
  .pid { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:0.78rem; background:var(--chip); color:var(--muted);
    padding:1px 6px; border-radius:4px; margin-right:3px; white-space:nowrap; }
  .grid2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:14px; }
  .strength { display:flex; align-items:center; gap:8px; font-size:0.82rem; color:var(--muted); margin-bottom:8px; }
  .dots { display:inline-flex; gap:3px; }
  .dots i { width:9px; height:9px; border-radius:50%; background:var(--line); display:inline-block; }
  .dots i.on { background:var(--accent); }
  .scroll { overflow-x:auto; border:1px solid var(--line); border-radius:10px; background:var(--panel); }
  table { border-collapse:collapse; width:100%; font-size:0.88rem; }
  .scroll table { min-width:680px; }
  th, td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
  th { font-weight:600; color:var(--muted); font-size:0.8rem; white-space:nowrap; background:var(--panel); }
  tr:last-child td { border-bottom:none; }
  td.nowrap { white-space:nowrap; }
  .era td { background:var(--chip); font-weight:600; font-size:0.82rem; color:var(--muted); }
  .bars { margin-top:10px; }
  .bar { display:grid; grid-template-columns:190px minmax(0,1fr) 78px; align-items:center; gap:10px; margin-bottom:7px; font-size:0.88rem; }
  .bar .track { height:12px; background:var(--chip); border-radius:6px; overflow:hidden; }
  .bar .fill { height:100%; background:var(--accent); border-radius:6px; }
  .bar .v { color:var(--muted); font-variant-numeric:tabular-nums; text-align:right; font-size:0.82rem; }
  .callout { border-left:3px solid var(--accent); background:var(--accent-soft); padding:12px 16px; border-radius:0 8px 8px 0; margin:14px 0; font-size:0.93rem; }
  .callout.warn { border-color:var(--warn); background:var(--warn-soft); }
  .tl-wrap { overflow-x:auto; background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:10px 8px 4px; }
  svg text { font-family:inherit; fill:var(--text); }
  .fit { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }
  .fit .card.yes { border-top:3px solid var(--good); } .fit .card.no { border-top:3px solid var(--warn); }
  .q { counter-reset:q; list-style:none; padding:0; }
  .q li { counter-increment:q; position:relative; padding:10px 14px 10px 44px; border:1px solid var(--line); border-radius:8px; background:var(--panel); margin-bottom:8px; }
  .q li::before { content:counter(q); position:absolute; left:14px; top:10px; width:20px; height:20px; border-radius:50%;
    background:var(--accent-soft); color:var(--accent); font-size:0.75rem; font-weight:700; display:flex; align-items:center; justify-content:center; }
  .q .why { display:block; color:var(--muted); font-size:0.85rem; }
  footer { color:var(--muted); font-size:0.82rem; border-top:1px solid var(--line); padding-top:16px; }
  @media (max-width:860px) {
    .layout { grid-template-columns:1fr; }
    nav { position:static; height:auto; border-right:none; border-bottom:1px solid var(--line); padding:16px; display:flex; flex-wrap:wrap; gap:2px 4px; }
    nav .who, nav .sub, nav .grp { width:100%; } nav .grp { margin:6px 0 0; }
    main { padding:24px 16px 60px; } .hero { padding:22px 18px; }
    .bar { grid-template-columns:120px minmax(0,1fr) 64px; }
    .tiles { grid-template-columns:repeat(2,minmax(0,1fr)); }
  }
  @media print { nav { display:none; } .layout { display:block; } body { background:#fff; font-size:11pt; } .card, .tile, .hero { break-inside:avoid; } }
'''

BADGE = {'사실': 'b-fact', '해석': 'b-view', '빈칸': 'b-gap', '주의': 'b-gap', '내부': 'b-int'}


def rich(t):
    t = html.escape(str(t if t is not None else ''))
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\[(P\d{2}(?:[·,]P\d{2})*)\]', lambda m: ''.join('<span class="pid">%s</span>' % p for p in re.split('[·,]', m.group(1))), t)
    def badge(m):
        kind, _, label = m.group(1).partition(':')
        return '<span class="badge %s">%s</span>' % (BADGE[kind], label or kind) if kind in BADGE else m.group(0)
    return re.sub(r'\{([^{}]+)\}', badge, t)


def dots(n):
    return '<span class="dots" aria-label="5점 중 %d점">%s</span>' % (n, ''.join('<i%s></i>' % (' class="on"' if i <= n else '') for i in range(1, 6)))


def pids(a):
    return ''.join('<span class="pid">%s</span>' % html.escape(str(p)) for p in (a or []))


def ul(items):
    return '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(i) for i in items)


def read_cards(root):
    cards = {}
    for f in sorted(glob.glob(os.path.join(root, 'inventory', 'P*.md'))):
        s = open(f, encoding='utf-8').read()
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', s, re.S)
        if not m:
            continue
        fm = dict((k, v.strip().strip('"')) for k, v in re.findall(r'^([\w가-힣]+):\s*(.*)$', m.group(1), re.M))
        one = re.search(r'^## 한 줄 요약\s*\n(.*?)(?=^## |\Z)', m.group(2), re.S | re.M)
        cards[fm.get('id', os.path.basename(f)[:3])] = {
            'title': fm.get('title', ''), 'period': fm.get('period', ''), 'status': fm.get('status', 'draft'),
            'gaps': len(re.findall(r'\[(?:인터뷰 필요|확인 필요|마스킹 확인|자료 대기)', s)),
            'one': (one.group(1).strip() if one else '')}
    return cards


def timeline_svg(tl):
    y0, y1 = float(tl.get('start', 2015)), float(tl.get('end', datetime.date.today().year + 1)) + 0.6
    W, L, R = 1040, 120, 20
    px = (W - L - R) / (y1 - y0)
    x = lambda y: L + (float(y) - y0) * px
    rows, marks = tl.get('rows', []), tl.get('marks', [])
    rowH, top = 34, 34
    H = top + len(rows) * rowH + 60
    s = []
    for y in range(int(y0), int(y1) + 1):
        s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--line)" stroke-width="1"/>' % (x(y), top - 8, x(y), H - 54))
        s.append('<text x="%.1f" y="%d" font-size="11" style="fill:var(--muted)">%d</text>' % (x(y) + 3, top - 14, y))
    for i, r in enumerate(rows):
        yy = top + i * rowH
        strong = bool(r.get('strong'))
        s.append('<text x="8" y="%d" font-size="12.5" font-weight="600">%s</text>' % (yy + 19, html.escape(r['label'])))
        for a, b, label in r.get('items', []):
            w = max(6, x(b) - x(a) - 2)
            s.append('<rect x="%.1f" y="%d" width="%.1f" height="21" rx="4" style="fill:var(%s)"/>' % (x(a), yy + 5, w, '--accent' if strong else '--accent-soft'))
            if w > len(label) * 11:
                s.append('<text x="%.1f" y="%d" font-size="11.5" style="fill:%s">%s</text>' % (x(a) + 6, yy + 20, '#fff' if strong else 'var(--accent)', html.escape(label)))
    for i, (yr, label) in enumerate(marks):
        yy = H - 48
        s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--warn)" stroke-width="1.2" stroke-dasharray="3 3"/>' % (x(yr), top - 4, x(yr), yy))
        s.append('<circle cx="%.1f" cy="%d" r="3.5" style="fill:var(--warn)"/>' % (x(yr), yy))
        s.append('<text x="%.1f" y="%d" font-size="11" text-anchor="middle" style="fill:var(--warn)">%s</text>' % (x(yr), yy + 17 + (15 if i % 2 else 0), html.escape(label)))
    return '<svg role="img" aria-label="이력 타임라인" viewBox="0 0 %d %d" width="%d" height="%d" style="min-width:860px;max-width:100%%;height:auto">%s</svg>' % (W, H, W, H, ''.join(s))


def build(root):
    d = yaml.safe_load(open(os.path.join(root, 'self-profile.yaml'), encoding='utf-8'))
    cards = read_cards(root)
    name = d['meta']['name']
    secs, nav = [], []          # (id, nav group, nav label, html)
    no = [0]

    def add(sid, group, label, body, badge=''):
        no[0] += 1
        secs.append('<section id="%s">\n  <h2><span class="no">%02d</span>%s%s</h2>\n%s\n</section>' % (sid, no[0], html.escape(label), (' ' + rich(badge)) if badge else '', body))
        nav.append((group, sid, label))

    lead = lambda x: ('<p class="lead">%s</p>' % rich(x.get('lead'))) if isinstance(x, dict) and x.get('lead') else ''

    # 머리
    tiles = ''.join('<div class="tile"><div class="n">%s</div><div class="l">%s</div></div>' % (rich(t['n']), rich(t['l'])) for t in d.get('tiles', []))
    n_conf = sum(1 for c in cards.values() if c['status'] == 'confirmed')
    tiles += '<div class="tile"><div class="n">%d장</div><div class="l">경력 카드 (확정 %d장)</div></div>' % (len(cards), n_conf) if cards and d.get('auto_card_tile', True) else ''
    top = ('<section id="top">\n  <div class="hero">\n    <div class="tag">내부 문서 · 공개 금지</div>\n    <h1>%s</h1>\n    <p class="big">%s</p>\n'
           '    <div class="legend"><span><span class="badge b-fact">사실</span> 카드·증빙으로 확인된 것</span><span><span class="badge b-view">해석</span> 자료를 읽고 내린 판단</span>'
           '<span><span class="badge b-gap">빈칸</span> 아직 확인되지 않은 것</span><span><span class="badge b-int">내부</span> 공개 CV에 넣지 않는 자료</span></div>\n  </div>\n'
           '  <div class="tiles">%s</div>\n</section>') % ('<br>'.join(rich(h) for h in d['headline']), rich(d['summary']), tiles)

    if d.get('timeline'):
        tl = d['timeline']
        rows = ''.join('<tr><td class="nowrap">%s</td><td>%s</td><td>%s</td></tr>' % (rich(r['period']), rich(r['where']), rich(r['what'])) for r in tl.get('table', []))
        body = lead(tl) + ('<div class="tl-wrap">%s</div>' % timeline_svg(tl) if tl.get('rows') else '')
        if rows:
            body += '<div class="scroll" style="margin-top:14px"><table><tr><th>시기</th><th>어디서</th><th>무엇을</th></tr>%s</table></div>' % rows
        add('timeline', '나는 누구인가', '지나온 길', body)
    if d.get('patterns'):
        p = d['patterns']
        body = lead(p) + ''.join('<div class="card"><h3>%s</h3><p>%s</p>%s</div>' % (rich(i['title']), rich(i.get('desc', '')), ul(i.get('evidence', []))) for i in p['items'])
        add('patterns', '나는 누구인가', '반복되는 패턴', body, '{해석}')
    if d.get('workmix'):
        w = d['workmix']; bars = w.get('bars', []); mx = max([b[1] for b in bars] or [1]); tot = sum(b[1] for b in bars) or 1
        bh = ''.join('<div class="bar"><div>%s</div><div class="track"><div class="fill" style="width:%.1f%%"></div></div><div class="v">%s건 · %.1f%%</div></div>' % (rich(b[0]), b[1] / mx * 100, b[1], b[1] / tot * 100) for b in bars)
        body = lead(w) + '<div class="card"><div class="bars">%s</div>%s</div>' % (bh, ('<p class="ev">%s</p>' % rich(w['note'])) if w.get('note') else '')
        if w.get('callout'):
            body += '<div class="callout">%s</div>' % rich(w['callout'])
        add('workmix', '나는 누구인가', '실제로 시간을 쓴 곳', body, '{사실}')
    if d.get('can_do'):
        c = d['can_do']
        body = lead(c) + '<div class="grid2">%s</div>' % ''.join(
            '<div class="card"><h3>%d. %s</h3><div class="strength">%s%s</div><p>%s</p><div class="ev"><b>맡을 수 있는 역할</b> %s</div><div class="ev"><span class="badge b-gap">주의</span> %s</div></div>'
            % (i + 1, rich(x['title']), dots(int(x.get('score', 3))), pids(x.get('cards')), rich(x.get('desc', '')), rich(x.get('role', '')), rich(x.get('caution', ''))) for i, x in enumerate(c['items']))
        add('can', '무엇을 할 수 있는가', '맡을 수 있는 프로젝트', body, '{해석}')
    if d.get('skills'):
        s = d['skills']; prev = ''; rows = ''
        for area, skill, lv, cs in s['rows']:
            rows += '<tr><td class="nowrap">%s</td><td>%s</td><td class="nowrap">%s</td><td>%s</td></tr>' % ('<b>%s</b>' % rich(area) if area != prev else '', rich(skill), dots(int(lv)), pids(cs)); prev = area
        add('skills', '무엇을 할 수 있는가', '역량 지도', lead(s) + '<div class="scroll"><table><tr><th>영역</th><th>역량</th><th>수준</th><th>근거</th></tr>%s</table></div>' % rows)
    if d.get('fit'):
        f = d['fit']
        add('fit', '무엇을 할 수 있는가', '맞는 자리, 조심할 자리', '<div class="fit"><div class="card yes"><h3>잘 맞는 자리</h3>%s</div><div class="card no"><h3>조심할 자리</h3>%s</div></div>' % (ul(f.get('yes', [])), ul(f.get('no', []))), '{해석}')
    if cards:
        pj = d.get('projects') or {}
        groups = pj.get('groups') or [{'title': '전체', 'cards': sorted(cards)}]
        listed = set(c for g in groups for c in g['cards'])
        rest = [c for c in sorted(cards) if c not in listed]
        if rest:
            groups = groups + [{'title': '그 밖의 카드', 'cards': rest}]
        rows = ''; gaps = 0
        for g in groups:
            rows += '<tr class="era"><td colspan="6">%s</td></tr>' % rich(g['title'])
            for cid in g['cards']:
                c = cards.get(cid)
                if not c:
                    continue
                gaps += 0 if c['status'] == 'confirmed' else c['gaps']
                st = '<span class="badge b-fact">확정</span>' if c['status'] == 'confirmed' else ('<span class="badge b-gap">%d</span>' % c['gaps'] if c['gaps'] else '<span class="badge b-fact">0</span>')
                rows += '<tr><td class="nowrap"><span class="pid">%s</span></td><td><b>%s</b></td><td class="nowrap">%s</td><td>%s</td><td>%s</td><td class="nowrap">%s</td></tr>' % (
                    cid, rich((pj.get('title') or {}).get(cid, c['title'])), rich((pj.get('period') or {}).get(cid, c['period'])), rich((pj.get('did') or {}).get(cid, c['one'])), rich((pj.get('result') or {}).get(cid, '')), st)
        body = '<p class="lead">%s</p>' % rich(pj.get('lead') or '원장(inventory/)의 카드 %d장이다. 확정된 카드는 %d장이고, 숫자는 카드에 남아 있는 확인 필요·자료 대기 표시의 개수다(합계 %d).' % (len(cards), n_conf, gaps))
        body += '<div class="scroll"><table><tr><th>ID</th><th>프로젝트</th><th>기간</th><th>내가 한 일</th><th>결과</th><th>빈칸</th></tr>%s</table></div>' % rows
        add('projects', '근거', '프로젝트 전체 목록', body, '{사실}')
    if d.get('numbers'):
        n = d['numbers']
        rows = ''.join('<tr><td class="nowrap">%s</td><td>%s</td><td>%s</td></tr>' % (rich(r['num']), rich(r['what']), rich(r['mine'])) for r in n['rows'])
        add('numbers', '근거', '숫자와 그 주인', lead(n) + '<div class="scroll"><table><tr><th>숫자</th><th>무엇의 숫자인가</th><th>내 몫</th></tr>%s</table></div>' % rows)
    if d.get('edu'):
        e = d['edu']
        add('edu', '근거', '학력·자격·포상', '<div class="grid2">%s</div>' % ''.join('<div class="card"><h3>%s</h3>%s</div>' % (rich(b['title']), ul(b['items'])) for b in e.get('blocks', [])), '{사실}')
    if d.get('voice'):
        v = d['voice']
        add('voice', '근거', '나의 글쓰기', lead(v) + '<div class="card">%s%s</div>' % (ul(v['items']), ('<p class="ev">%s</p>' % rich(v['ref'])) if v.get('ref') else ''))
    if d.get('gaps'):
        add('gaps', '다음', '약점과 빈칸', ''.join('<div class="card"><h3>%s</h3>%s</div>' % (rich(g['title']), ul(g['items'])) for g in d['gaps']))
    if d.get('todo'):
        t = d['todo']; tone = {'답함': '사실', '절반': '해석', '남음': '빈칸'}
        items = ''.join('<li>%s%s<span class="why">%s</span></li>' % (('<span class="badge %s">%s</span> ' % (BADGE[tone[i['status']]], i['status'])) if i.get('status') in tone else '', rich(i['q']), rich(i.get('why', ''))) for i in t['items'])
        add('todo', '다음', '먼저 답할 질문', lead(t) + '<ol class="q">%s</ol>' % items)
    if d.get('sources'):
        add('sources', '다음', '출처', '<div class="card">%s</div><footer>이 문서는 성적, 재직 정보, 내부 업무 내용을 담고 있다. 공개 저장소나 사이트에 올리지 않는다. 카드가 바뀌면 다시 만든다.</footer>' % ul(d['sources']))

    navh = '<div class="who">%s 사용 설명서</div><div class="sub">내부용 · %s</div><div class="grp">나는 누구인가</div><a href="#top">한 문단 요약</a>' % (html.escape(name), html.escape(str(d['meta'].get('updated', ''))))
    cur = '나는 누구인가'
    for g, sid, label in nav:
        if g != cur:
            navh += '<div class="grp">%s</div>' % g; cur = g
        navh += '<a href="#%s">%s</a>' % (sid, html.escape(label))
    page = ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<meta name="robots" content="noindex,nofollow">\n<title>%s 사용 설명서 (내부용)</title>\n<style>%s</style>\n</head>\n<body>\n<div class="layout">\n<nav>%s</nav>\n<main>\n%s\n%s\n</main>\n</div>\n</body>\n</html>\n'
            ) % (html.escape(name), CSS, navh, top, '\n\n'.join(secs))
    out = os.path.join(root, 'self-profile.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('OK: %s (%d bytes, 섹션 %d개, 카드 %d장)' % (out, len(page.encode('utf-8')), len(secs) + 1, len(cards)))


if __name__ == '__main__':
    try:
        build(sys.argv[1] if len(sys.argv) > 1 else '.')
    except yaml.YAMLError as ex:
        sys.exit('self-profile.yaml 형식 오류: %s\n→ 문장이 든 값은 큰따옴표로 감싸고, 한 줄짜리 {key: value} 안의 물음표·쉼표·배지를 확인하세요.' % ex)
