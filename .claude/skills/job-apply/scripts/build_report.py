#!/usr/bin/env python3
"""지원처 분석보고서 HTML 빌더.
사용: python build_report.py applications/{지원처}_{직무} [--out 경로] [--resume 파일] [--materials 파일] [--compare 파일] [--summary 파일]
입력: 00_target.md, 00_materials.md(있으면 재료 절), 02_resume_final.md(없으면 최신 01_resume_draft*.md, 둘 다 없으면 '초안 미작성' 표시), _workspace/review_*.md(review_target이 이 폴더를 가리키는 것),
      문항별_비교.html(build_compare.py 생성물 — 있으면 'ChatGPT 대조' 절), 04_소재정리.md(있으면 '핵심 소재 정리' 절). 둘 다 없으면 보고서는 이전과 같다.
출력: {폴더}/{지원처}_분석보고서.html — 생성물이므로 직접 수정하지 말고 md를 고친 뒤 재빌드."""
import re, sys, os, glob, html, datetime
sys.path.insert(0, os.path.dirname(__file__))
from charcount import sections as resume_sections, measure

def opt_file(args, flag, default):
    """--flag 경로가 있으면 그것, 없으면 기본 경로. 파일이 없으면 None."""
    p = args[args.index(flag) + 1] if flag in args else default
    return p if os.path.exists(p) else None

# ---------- 최소 마크다운 변환 (외부 라이브러리 없음) ----------
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+|[^)]+\.(?:html|md|pdf))\)', r'<a href="\2">\1</a>', s)
    return s

def md_to_html(md, shift=0):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    lines = md.split('\n'); out = []; i = 0
    para = []; lst = None; quote = []; table = []
    def flush_para():
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
    def flush_list():
        nonlocal lst
        if lst: out.append(f"</{lst}>"); lst = None
    def flush_quote():
        if quote: out.append('<blockquote>' + md_to_html('\n'.join(quote), shift) + '</blockquote>'); quote.clear()
    def flush_table():
        if not table: return
        rows = [r for r in table if not re.match(r'^\|?\s*:?-{2,}', r)]
        h = ['<table><thead>']
        for k, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip('|').split('|')]
            tag = 'th' if k == 0 else 'td'
            h.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
            if k == 0: h.append('</thead><tbody>')
        h.append('</tbody></table>'); out.append('\n'.join(h)); table.clear()
    def flush_all(): flush_para(); flush_list(); flush_quote(); flush_table()
    while i < len(lines):
        l = lines[i]
        if l.startswith('```'):
            flush_all(); j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith('```'): buf.append(lines[j]); j += 1
            out.append('<pre>' + html.escape('\n'.join(buf)) + '</pre>'); i = j + 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)', l)
        if m:
            flush_all(); lvl = min(len(m.group(1)) + shift, 6)
            out.append(f'<h{lvl}>{inline(m.group(2))}</h{lvl}>'); i += 1; continue
        if l.strip() in ('---', '***'): flush_all(); out.append('<hr />'); i += 1; continue
        if l.startswith('>'):
            flush_para(); flush_list(); flush_table(); quote.append(l[1:].lstrip()); i += 1; continue
        else: flush_quote()
        if l.lstrip().startswith('|'):
            flush_para(); flush_list(); table.append(l); i += 1; continue
        else: flush_table()
        m = re.match(r'^(\s*)([-*]|\d+[.)])\s+(.*)', l)
        if m:
            flush_para(); kind = 'ol' if m.group(2)[0].isdigit() else 'ul'
            if lst != kind: flush_list(); out.append(f'<{kind}>'); lst = kind
            out.append(f'<li>{inline(m.group(3))}</li>'); i += 1; continue
        if l.strip() == '': flush_para(); flush_list(); i += 1; continue
        if lst and l.startswith('  '): out[-1] = out[-1][:-5] + ' ' + inline(l.strip()) + '</li>'; i += 1; continue
        flush_list(); para.append(l.strip()); i += 1
    flush_all()
    return '\n'.join(out)

# ---------- 자소서 문항 아티클 ----------
def resume_articles(md):
    arts = []
    raw_secs = re.findall(r'^## (\d+)[.．][^\n]*\n(.*?)(?=^## |\Z)', md, flags=re.S | re.M)
    comments = {int(n): re.findall(r'<!--(.*?)-->', b, flags=re.S) for n, b in raw_secs}
    for s in resume_sections(md, keep_placeholders=True):
        m = measure(re.sub(r'【.*?】', '', s['body'])); hi = s['hi'] or 1
        pct = round(m['incl'] / hi * 100)
        paras = []
        for p in [x for x in s['body'].split('\n') if x.strip()]:
            t = html.escape(p); t = t.replace('【', '<mark>【').replace('】', '】</mark>')
            paras.append(f'<p class="subhead">{t}</p>' if p.startswith('[') else f'<p>{t}</p>')
        notes = ' '.join(comments.get(s['num'], []))
        warn = [x.strip() for x in re.findall(r'(\[(?:확인 필요|사용자 확인|마스킹 확인|인터뷰 필요|draft 카드)[^\n]*)', notes)]
        info = [x.strip() for x in notes.split('\n') if x.strip() and not x.strip().startswith('[')]
        rng = f"{s['lo']}~{s['hi']}자" if s['hi'] else ''
        a = [f'<article class="q" id="q{s["num"]}"><header><h3>{s["num"]}. {html.escape(s["title"])}</h3>',
             f'<div class="meta"><span class="chip">공백 포함 {m["incl"]:,}자 <small>(줄바꿈 포함 {m["incl_nl"]:,})</small></span>',
             f'<span class="chip">공백 제외 {m["excl"]:,}자</span>']
        if s['hi']: a.append(f'<span class="chip">상한 {s["hi"]:,}자의 {pct}%</span>')
        if m['over60']: a.append(f'<span class="chip">60자 초과 {m["over60"]}문장</span>')
        a.append(f'<button class="copy" data-n="{s["num"]}">본문 복사</button></div>')
        if s['hi']: a.append(f'<div class="bar"><i style="width:{min(pct,100)}%"></i></div>')
        a.append('</header><div class="body">' + '\n'.join(paras) + '</div>')
        a.append(f'<textarea class="raw" id="raw{s["num"]}" hidden>{html.escape(s["body"])}</textarea>')
        if warn: a.append('<details class="note warn"><summary>제출 전 확인 필요 (%d)</summary><ul>%s</ul></details>' % (len(warn), ''.join(f'<li>{html.escape(w)}</li>' for w in warn)))
        if info: a.append('<details class="note"><summary>근거 카드 · 수치 출처 · 검수 반영 이력</summary><ul>%s</ul></details>' % ''.join(f'<li>{html.escape(x)}</li>' for x in info))
        a.append('</article>'); arts.append('\n'.join(a))
    return '\n'.join(arts)

CSS = """:root{--blue:#1a73e8;--ink:#1f2328;--muted:#5f6b7a;--line:#e3e8ef;--bg:#fff;--soft:#f6f8fb;--warn:#b45309;--warnbg:#fff7ed;--ok:#15803d}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.65;font-size:15px}
.wrap{max-width:1120px;margin:0 auto;padding:24px 20px 80px}
header.top{border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:24px}header.top h1{font-size:26px;margin:0 0 6px}header.top .sub{color:var(--muted);margin:0}
.layout{display:grid;grid-template-columns:220px 1fr;gap:32px}
nav.toc{position:sticky;top:16px;align-self:start;font-size:14px}nav.toc a{display:block;color:var(--muted);text-decoration:none;padding:5px 10px;border-left:2px solid var(--line)}nav.toc a:hover,nav.toc a.active{color:var(--blue);border-color:var(--blue)}nav.toc .grp{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:14px 0 4px 10px}
section.block{margin-bottom:48px;scroll-margin-top:16px}section.block>h2{font-size:22px;border-bottom:2px solid var(--blue);padding-bottom:6px;margin:0 0 6px}
.md h2{font-size:19px;margin:28px 0 8px}.md h3{font-size:16.5px;margin:22px 0 6px;color:var(--blue)}.md h4{font-size:15px;margin:16px 0 4px}
.md table{border-collapse:collapse;width:100%;font-size:13.5px;margin:10px 0 16px;display:block;overflow-x:auto}.md th,.md td{border:1px solid var(--line);padding:7px 10px;vertical-align:top;text-align:left}.md th{background:var(--soft);white-space:nowrap}
.md blockquote{margin:12px 0;padding:10px 16px;border-left:4px solid var(--blue);background:var(--soft);border-radius:0 8px 8px 0}.md blockquote p{margin:4px 0}
.md code{background:var(--soft);padding:1px 5px;border-radius:4px;font-size:.9em}.md pre{background:var(--soft);padding:10px;border-radius:8px;overflow-x:auto;font-size:13px}.md hr{border:0;border-top:1px solid var(--line);margin:24px 0}.md ul,.md ol{padding-left:22px}.md li{margin:3px 0}
article.q{border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:0 0 22px;background:#fff}article.q h3{margin:0 0 8px;font-size:17px}article.q .meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}
.chip{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:12.5px;color:var(--muted)}.chip small{color:#9aa4b2}
.bar{height:6px;background:var(--soft);border-radius:3px;overflow:hidden;margin-bottom:14px}.bar i{display:block;height:100%;background:var(--blue)}
article.q .body p{margin:0 0 12px;font-size:15.5px;line-height:1.85}article.q .body p.subhead{font-weight:700;color:var(--blue);margin:14px 0 4px;font-size:14.5px}
button.copy{margin-left:auto;background:var(--blue);color:#fff;border:0;border-radius:6px;padding:5px 12px;font-size:13px;cursor:pointer}button.copy.done{background:var(--ok)}
details.note{margin-top:10px;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-size:13px;background:var(--soft)}details.note.warn{border-color:#fdba74;background:var(--warnbg)}details.note summary{cursor:pointer;font-weight:600}details.note.warn summary{color:var(--warn)}details.note ul{margin:8px 0 2px;padding-left:18px}details.note li{margin:4px 0}
details.review{border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin:0 0 14px}details.review summary{cursor:pointer;font-weight:700;font-size:16px}
.callout{border:1px solid #fdba74;background:var(--warnbg);border-radius:10px;padding:12px 16px;margin:0 0 18px;font-size:14px}.callout b{color:var(--warn)}
mark{background:#fef3c7;color:#92400e;padding:0 3px;border-radius:3px}
footer{margin-top:40px;border-top:1px solid var(--line);padding-top:14px;color:var(--muted);font-size:12.5px}
@media (max-width:860px){.layout{grid-template-columns:1fr}nav.toc{position:static;display:flex;flex-wrap:wrap;gap:4px}nav.toc .grp{display:none}nav.toc a{border:1px solid var(--line);border-radius:999px;padding:3px 10px}}
@media print{nav.toc,button.copy{display:none}.layout{grid-template-columns:1fr}article.q,section.block{break-inside:avoid}details.note{display:none}body{font-size:12.5px}}"""

JS = """document.querySelectorAll('button.copy').forEach(function(b){b.addEventListener('click',function(){var t=document.getElementById('raw'+b.dataset.n).value;function ok(){b.textContent='복사됨';b.classList.add('done');setTimeout(function(){b.textContent='본문 복사';b.classList.remove('done')},1500)}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(ok)}else{var ta=document.getElementById('raw'+b.dataset.n);ta.hidden=false;ta.select();document.execCommand('copy');ta.hidden=true;ok()}})});
var links=[].slice.call(document.querySelectorAll('nav.toc a'));var secs=links.map(function(a){return document.querySelector(a.getAttribute('href'))});
function spy(){var y=window.scrollY+80;var idx=0;secs.forEach(function(s,i){if(s&&s.offsetTop<=y)idx=i});links.forEach(function(a,i){a.classList.toggle('active',i===idx)})}window.addEventListener('scroll',spy);spy();"""

def main():
    args = sys.argv[1:]
    if not args: print(__doc__); sys.exit(1)
    app = args[0].rstrip('/'); out = None; resume = None
    if '--out' in args: out = args[args.index('--out') + 1]
    if '--resume' in args: resume = args[args.index('--resume') + 1]
    root = os.path.dirname(os.path.dirname(app)) if os.path.basename(os.path.dirname(app)) == 'applications' else os.path.dirname(app)
    name = os.path.basename(app)
    target = open(os.path.join(app, '00_target.md'), encoding='utf-8').read()
    if not resume:
        cands = [os.path.join(app, '02_resume_final.md')] + sorted(glob.glob(os.path.join(app, '01_resume_draft*.md')), reverse=True)
        resume = next((p for p in cands if os.path.exists(p)), None)
    rmd = open(resume, encoding='utf-8').read() if resume else None
    # 재료 추천표(Phase 3.5): 있으면 분석 뒤에 붙인다
    mpath = args[args.index('--materials') + 1] if '--materials' in args else os.path.join(app, '00_materials.md')
    materials = open(mpath, encoding='utf-8').read() if os.path.exists(mpath) else None
    # ChatGPT 대조 비교표(Phase 4.5)·핵심 소재 정리(Phase 7): 파일이 있을 때만 싣는다
    cpath = opt_file(args, '--compare', os.path.join(app, '문항별_비교.html'))
    spath = opt_file(args, '--summary', os.path.join(app, '04_소재정리.md'))
    cmp_html = sum_html = ''; cmp_css = ''
    if cpath:
        m = re.search(r'<!--cmp:begin-->(.*?)<!--cmp:end-->', open(cpath, encoding='utf-8').read(), flags=re.S)
        if m:
            from build_compare import CSS as cmp_css
            inner = m.group(1)
        else:  # 손으로 만든 비교표 등 조각 표식이 없는 파일은 링크만 건다
            inner = f'<p><a href="{html.escape(os.path.basename(cpath))}">{html.escape(os.path.basename(cpath))}</a> (따로 열기)</p>'
        cmp_html = f'<section class="block" id="compare"><h2>ChatGPT 대조 — {html.escape(os.path.basename(cpath))}</h2><div class="callout"><b>대조용.</b> 다른 모델이 같은 재료로 쓴 판을 나란히 놓은 것입니다. 사실의 출처가 아니며, 가져온 문장은 사실 검수를 거칩니다.</div>{inner}</section>'
    if spath:
        sbody = md_to_html(re.sub(r'^# .*\n', '', open(spath, encoding='utf-8').read(), count=1), shift=1)
        sum_html = f'<section class="block" id="summary"><h2>핵심 소재 정리 — {html.escape(os.path.basename(spath))}</h2><div class="md">{sbody}</div></section>'
    title = re.search(r'^# (.*)', target, flags=re.M).group(1).split(' — ')[0]
    # 리뷰: review_target 이 이 폴더를 가리키는 파일
    reviews = []
    for p in sorted(glob.glob(os.path.join(root, '_workspace', 'review_*.md'))):
        t = open(p, encoding='utf-8').read()
        if name in t[:600] or name.split('_')[0] in os.path.basename(p): reviews.append((os.path.basename(p), t))
    # 목차: 00_target H2
    secs = re.split(r'^## ', target, flags=re.M)[1:]
    nav = ['<div class="grp">분석</div>']; body = []
    for k, s in enumerate(secs, 1):
        head, rest = s.split('\n', 1)
        nav.append(f'<a href="#t{k}">{inline(head[:28])}</a>')
        body.append(f'<section class="block" id="t{k}"><h2>{inline(head)}</h2><div class="md">{md_to_html(rest, shift=0)}</div></section>')
    mat_html = ''
    if materials:
        nav.append('<div class="grp">재료</div><a href="#materials">경험 추천표</a>')
        mbody = md_to_html(re.sub(r'^# .*\n', '', materials, count=1), shift=1)
        mat_html = f'<section class="block" id="materials"><h2>문항별 경험 추천표 — 00_materials.md</h2><div class="callout"><b>선택 대기.</b> 초안은 이 표에서 고른 조합으로만 씁니다. 문항마다 [내 선택]에 후보 번호와 하고 싶은 말을 적어 주세요.</div><div class="md">{mbody}</div></section>'
    if cmp_html: nav.append('<div class="grp">대조</div><a href="#compare">ChatGPT 대조</a>')
    nav.append('<div class="grp">자기소개서</div><a href="#resume">자소서 본문</a>')
    if reviews: nav.append('<div class="grp">검수</div><a href="#reviews">검수 리포트</a>')
    if sum_html: nav.append('<div class="grp">정리</div><a href="#summary">핵심 소재 정리</a>')
    if rmd is not None:
        res_html = f'<section class="block" id="resume"><h2>자기소개서 — {html.escape(os.path.basename(resume))}</h2><div class="callout"><b>제출 전 필독.</b> 글자수는 공백 포함 기준이며 공고 원문의 기준(공백 포함/제외, 줄바꿈 산입)을 확인해야 합니다. <mark>【 】</mark>는 사용자 입력이 필요한 자리이며 채우기 전에는 제출할 수 없습니다.</div>{resume_articles(rmd)}</section>'
    else:
        res_html = '<section class="block" id="resume"><h2>자기소개서</h2><div class="callout"><b>초안 미작성.</b> 채용분야·문항·재료 선택이 확정되면 초안을 쓰고 이 자리에 붙입니다.</div></section>'
    rev_html = ''
    if reviews:
        rev_html = '<section class="block" id="reviews"><h2>검수 리포트</h2>' + ''.join(
            f'<details class="review"{" open" if "심사관" in fn else ""}><summary>{html.escape(fn)}</summary><div class="md">{md_to_html(re.sub(r"^---.*?---", "", t, count=1, flags=re.S), shift=1)}</div></details>' for fn, t in reviews) + '</section>'
    today = datetime.date.today().isoformat()
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)} 분석 보고서</title><style>{CSS}{cmp_css}</style></head><body><div class="wrap">
<header class="top"><h1>{html.escape(title)} 지원 분석 보고서</h1><p class="sub">생성 {today} · 원천: 00_target.md · {html.escape(os.path.basename(resume)) if resume else '자소서 초안 없음'} · 검수 {len(reviews)}건 — 이 HTML은 생성물입니다. 수정은 md에서.</p></header>
<div class="layout"><nav class="toc">{''.join(nav)}</nav><main>{''.join(body)}{mat_html}{cmp_html}{res_html}{rev_html}{sum_html}</main></div>
<footer><p>build_report.py · {html.escape(app)}</p></footer></div><script>{JS}</script></body></html>'''
    out = out or os.path.join(app, f'{name.split("_")[0]}_분석보고서.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('written', out, f'({len(page)//1024} KB, 분석 절 {len(secs)}, 문항 {len(resume_sections(rmd)) if rmd else 0}, 재료표 {"있음" if materials else "없음"}, 검수 {len(reviews)}' + (', 비교표 있음' if cmp_html else '') + (', 소재정리 있음' if sum_html else '') + ')')

if __name__ == '__main__':
    main()
