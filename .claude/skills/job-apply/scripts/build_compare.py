#!/usr/bin/env python3
"""두 초안(또는 그 이상)을 문항별로 나란히 놓는 비교표 HTML 빌더.
사용: python build_compare.py 01_resume_draft.md 03_chatgpt_원본출력.md [--labels Claude,ChatGPT]
                              [--out 문항별_비교.html] [--title 제목] [--limit 500]
문항 헤딩은 '## 1. 제목 (450~485자)'와 '## 문항 1' 두 형식을 모두 읽는다. 글자수는 직접 센다
(공백 포함, 줄바꿈 제외). '## 작성 메모'에 큰따옴표로 신고된 문장은 본문에서 노란색으로 표시한다.
출력 기본값: 첫 파일과 같은 폴더의 문항별_비교.html — 생성물이므로 직접 수정하지 않는다."""
import argparse, datetime, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from charcount import measure

HEAD = re.compile(r'^##\s+(?:문항\s*)?(\d+)\s*[.．)]?\s*(.*?)\s*$')
RANGE = re.compile(r'\((\d[\d,]*)\s*[~～-]\s*(\d[\d,]*)\s*자')
SELF = re.compile(r'^\(?\s*글자\s*수\s*[:：]?\s*(?:공백\s*포함\s*)?(\d[\d,]*)\s*자?\s*\)?$')
QUOTE = re.compile(r'[“"]([^”"\n]{8,})[”"]')
SUBHEAD = re.compile(r'^["“\[]')
BULLET = re.compile(r'^[-*]\s+')
SUB_ATTR = ' class="sub"'

def parse(md):
    """→ (문항 dict {num: {title, lo, hi, paras, self}}, 메모 줄 목록)"""
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    qs, memo, cur, in_memo = {}, [], None, False
    for line in md.split('\n'):
        if line.strip().startswith('```'): continue
        if line.startswith('## ') or line.startswith('# '):
            m = HEAD.match(line)
            in_memo = (not m) and line.startswith('## ') and '메모' in line
            cur = None
            if m:
                title = m.group(2); r = RANGE.search(title)
                cur = dict(title=RANGE.sub('', title).strip(' ()'), paras=[], self=None,
                           lo=int(r.group(1).replace(',', '')) if r else None,
                           hi=int(r.group(2).replace(',', '')) if r else None)
                qs[int(m.group(1))] = cur
            continue
        s = line.strip()
        if in_memo:
            if s: memo.append(s)
            continue
        if cur is None or not s or s == '---' or s.startswith('>'): continue
        sm = SELF.match(s)
        if sm: cur['self'] = int(sm.group(1).replace(',', '')); continue
        cur['paras'].append(line.rstrip('\r'))   # 줄 끝 공백도 글자수에 든다(charcount.py와 같은 기준)
    return qs, memo

def mark(text, quotes):
    t = html.escape(text, quote=False)
    for q in quotes:
        e = html.escape(q, quote=False)
        if e in t: t = t.replace(e, f'<mark>{e}</mark>')
    return t.replace('【', '<mark>【').replace('】', '】</mark>')

def status(n, lo, hi):
    if hi and n > hi: return 'over', f'상한 {hi:,}자 초과 +{n - hi}'
    if lo and n < lo: return 'under', f'하한 {lo:,}자 미달 -{lo - n}'
    return ('ok', '범위 안') if hi else ('', '')

CSS = """.cmp{--cb:#1a73e8;--ci:#1f2328;--cm:#5f6b7a;--cl:#e3e8ef;--cs:#f6f8fb;font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",system-ui,sans-serif;color:var(--ci);line-height:1.7;word-break:keep-all}
.cmp *{box-sizing:border-box}.cmp .cmp-note{color:var(--cm);font-size:13px;margin:4px 0 14px}
.cmp table.cmp-sum{border-collapse:collapse;font-size:13.5px;margin:0 0 8px;width:100%}.cmp .cmp-scroll{overflow-x:auto}
.cmp table.cmp-sum th,.cmp table.cmp-sum td{border:1px solid var(--cl);padding:6px 10px;text-align:left;vertical-align:top}.cmp table.cmp-sum th{background:var(--cs);white-space:nowrap}
.cmp table.cmp-sum td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.cmp h3.cmp-q{font-size:17px;margin:30px 0 10px;padding-top:18px;border-top:1px solid var(--cl)}.cmp h3.cmp-q small{font-weight:400;color:var(--cm);font-size:13px;margin-left:6px}
.cmp .cmp-row{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start}
.cmp .cmp-c{flex:1 1 340px;min-width:0;border:1px solid var(--cl);border-radius:10px;padding:14px 16px;background:#fff}
.cmp .cmp-h{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;font-size:12.5px;color:var(--cm);margin-bottom:8px}.cmp .cmp-h b{color:var(--cb);font-size:14px;margin-right:auto}
.cmp .cmp-chip{background:var(--cs);border:1px solid var(--cl);border-radius:999px;padding:1px 9px;white-space:nowrap}
.cmp .cmp-chip.over,.cmp .cmp-chip.under,.cmp td.over,.cmp td.under{color:#b42318;border-color:#f3b4ae;background:#fef3f2;font-weight:600}.cmp .cmp-chip.ok{color:#15803d}
.cmp .cmp-c p{margin:0 0 10px;font-size:14.5px;line-height:1.85;overflow-wrap:anywhere}.cmp .cmp-c p.sub{font-weight:700}.cmp .cmp-c p.none{color:var(--cm)}
.cmp mark{background:#fef3c7;color:#92400e;padding:0 2px;border-radius:3px}
.cmp button.cmp-copy{background:#fff;color:var(--cb);border:1px solid var(--cb);border-radius:6px;padding:2px 10px;font-size:12.5px;cursor:pointer}.cmp button.cmp-copy.done{background:#15803d;border-color:#15803d;color:#fff}
.cmp details.cmp-memo{border:1px solid var(--cl);border-radius:10px;padding:10px 16px;margin:14px 0 0;font-size:13.5px;background:var(--cs)}.cmp details.cmp-memo summary{cursor:pointer;font-weight:700}.cmp details.cmp-memo p{margin:6px 0}
@media print{.cmp button.cmp-copy{display:none}.cmp .cmp-c{break-inside:avoid}}"""

JS = """document.querySelectorAll('button.cmp-copy').forEach(function(b){b.addEventListener('click',function(){var ta=b.parentNode.parentNode.querySelector('textarea');function ok(){var o=b.textContent;b.textContent='복사됨';b.classList.add('done');setTimeout(function(){b.textContent=o;b.classList.remove('done')},1500)}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(ta.value).then(ok)}else{ta.hidden=false;ta.select();document.execCommand('copy');ta.hidden=true;ok()}})});"""

def fragment(paths, labels, limit=None):
    """비교표 본문(HTML 조각)과 요약 dict를 돌려준다. build_report.py가 같은 조각을 그대로 싣는다."""
    docs = [parse(open(p, encoding='utf-8').read()) for p in paths]
    nums = sorted({n for qs, _ in docs for n in qs})
    if not nums: sys.exit('문항 헤딩(## 1. … 또는 ## 문항 1)을 찾지 못했습니다: ' + ', '.join(paths))
    quotes = [[q for line in memo for q in QUOTE.findall(line)] for _, memo in docs]
    rows, blocks, flagged = [], [], 0
    for n in nums:
        found = [qs.get(n) for qs, _ in docs]
        title = next((q['title'] for q in found if q and q['title']), '') or f'문항 {n}'
        lo = next((q['lo'] for q in found if q and q['lo']), None)
        hi = next((q['hi'] for q in found if q and q['hi']), None) or limit
        rng = (f'{lo:,}~{hi:,}자' if lo else f'{hi:,}자 이내') if hi else ''
        cells, cards = [], []
        for k, q in enumerate(found):
            if not q or not q['paras']:
                cells.append('<td class="num">—</td>')
                cards.append(f'<div class="cmp-c"><div class="cmp-h"><b>{html.escape(labels[k])}</b></div><p class="none">이 판에는 이 문항이 없습니다.</p></div>')
                continue
            body = '\n'.join(q['paras']).strip(); m = measure(re.sub(r'【.*?】', '', body))
            cls, msg = status(m['incl'], lo, hi)
            if cls in ('over', 'under'): flagged += 1
            cells.append(f'<td class="num {cls}">{m["incl"]:,}자{" · " + msg if cls in ("over", "under") else ""}</td>')
            chips = [f'<span class="cmp-chip {cls}">공백 포함 {m["incl"]:,}자{" · " + msg if msg else ""}</span>',
                     f'<span class="cmp-chip">줄바꿈 포함 {m["incl_nl"]:,}</span>']
            if q['self'] is not None and q['self'] != m['incl']:
                chips.append(f'<span class="cmp-chip under">스스로 적은 글자수 {q["self"]:,}자와 다름</span>')
            ps = ''.join(f'<p{SUB_ATTR if SUBHEAD.match(p) else ""}>{mark(p, quotes[k])}</p>' for p in q['paras'])
            cards.append(f'<div class="cmp-c"><div class="cmp-h"><b>{html.escape(labels[k])}</b>{"".join(chips)}'
                         f'<button class="cmp-copy" type="button">본문 복사</button></div>{ps}'
                         f'<textarea hidden>{html.escape(body)}</textarea></div>')
        rows.append(f'<tr><td>{n}. {html.escape(title)}</td><td class="num">{rng or "—"}</td>{"".join(cells)}</tr>')
        blocks.append(f'<h3 class="cmp-q" id="cmp-q{n}">{n}. {html.escape(title)}{"<small>" + rng + "</small>" if rng else ""}</h3>'
                      f'<div class="cmp-row">{"".join(cards)}</div>')
    memos = ''.join(
        f'<details class="cmp-memo" open><summary>{html.escape(labels[k])} 작성 메모 (덧붙였다고 스스로 밝힌 문장 {len(quotes[k])}개)</summary>'
        + ''.join(f'<p>{mark(BULLET.sub("", l), quotes[k])}</p>' for l in memo) + '</details>'
        for k, (_, memo) in enumerate(docs) if memo)
    head = ''.join(f'<th>{html.escape(l)}</th>' for l in labels)
    frag = ('<div class="cmp"><p class="cmp-note">글자수는 스크립트가 센 값(공백 포함, 줄바꿈 제외)입니다. '
            '<mark>노란 표시</mark>는 작성 메모에서 재료에 없이 덧붙였다고 밝힌 문장 — 사실인지 확인한 뒤에만 씁니다.</p>'
            f'<div class="cmp-scroll"><table class="cmp-sum"><thead><tr><th>문항</th><th>범위</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'{"".join(blocks)}{memos}</div><script>{JS}</script>')
    return frag, dict(questions=len(nums), flagged=flagged, marked=sum(len(q) for q in quotes))

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('files', nargs='+', help='비교할 초안 md (둘 이상)')
    ap.add_argument('--labels', help='쉼표로 구분한 판 이름 (파일 순서대로)')
    ap.add_argument('--out'); ap.add_argument('--title')
    ap.add_argument('--limit', type=int, help='헤딩에 글자수 범위가 없을 때 쓸 상한')
    a = ap.parse_args()
    if len(a.files) < 2: ap.error('비교할 파일이 둘 이상 필요합니다')
    labels = [s.strip() for s in a.labels.split(',')] if a.labels else [
        'ChatGPT' if 'chatgpt' in os.path.basename(p).lower() else os.path.splitext(os.path.basename(p))[0] for p in a.files]
    if len(labels) != len(a.files): ap.error('--labels 개수가 파일 개수와 다릅니다')
    frag, info = fragment(a.files, labels, a.limit)
    folder = os.path.basename(os.path.dirname(os.path.abspath(a.files[0])))
    title = a.title or f'{folder} 문항별 비교'
    src = ' / '.join(f'{html.escape(l)} = {html.escape(os.path.basename(p))}' for l, p in zip(labels, a.files))
    page = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="robots" content="noindex"><title>{html.escape(title)}</title><style>body{{margin:0;background:#fff}}'
            f'.wrap{{max-width:1500px;margin:0 auto;padding:24px 20px 60px}}h1{{font:700 22px/1.4 system-ui,sans-serif;margin:0 0 4px}}\n{CSS}</style></head><body><div class="wrap">'
            f'<h1>{html.escape(title)}</h1><div class="cmp"><p class="cmp-note">생성 {datetime.date.today().isoformat()} · {src} · 내부 확인용 생성물 — 수정은 md에서.</p></div>\n'
            f'<!--cmp:begin-->{frag}<!--cmp:end-->\n</div></body></html>')
    out = a.out or os.path.join(os.path.dirname(a.files[0]), '문항별_비교.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('written', out, f'(문항 {info["questions"]}, 판 {len(labels)}, 범위 밖 {info["flagged"]}, 신고 문장 {info["marked"]})')

if __name__ == '__main__':
    main()
