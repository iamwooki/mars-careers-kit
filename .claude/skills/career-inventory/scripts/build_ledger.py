# -*- coding: utf-8 -*-
"""inventory/P*.md 카드를 파싱해 비공개 원장 뷰어(inventory/ledger.html)를 생성한다.

사용:  python build_ledger.py <inventory_dir>
원칙:  ledger.html은 생성물이다 — 직접 수정 금지, 카드 수정 후 재생성.
       site/ 밖에 있으므로 github.io 배포 대상이 아니다.
"""
import sys, os, re, html, glob, datetime

def parse_card(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.S)
    if not m:
        return None
    fm, body = m.groups()
    meta = {}
    for line in fm.splitlines():
        mm = re.match(r'^([\w가-힣]+):\s*(.*)$', line)
        if mm:
            meta[mm.group(1)] = mm.group(2).strip()
    return meta, body

def md2html(md):
    # 원칙: 카드는 "한 항목 = 한 줄"로 쓴다. 그래도 줄바꿈 이어쓰기가 있으면
    # 마크다운 표준처럼 앞 항목(li/p)에 공백 하나로 이어 붙인다 (문단 분리 금지).
    out, in_list = [], False
    for line in md.splitlines():
        if line.startswith('## '):
            if in_list: out.append('</ul>'); in_list = False
            out.append('<h4>%s</h4>' % html.escape(line[3:]))
        elif re.match(r'^\s*-\s+', line):
            if not in_list: out.append('<ul>'); in_list = True
            out.append('<li>%s</li>' % html.escape(re.sub(r'^\s*-\s+', '', line)))
        elif line.strip():
            # 이어쓰기 줄: 직전 li 또는 p에 연결
            if out and out[-1].endswith('</li>'):
                out[-1] = out[-1][:-5] + ' ' + html.escape(line.strip()) + '</li>'
            elif out and out[-1].endswith('</p>'):
                out[-1] = out[-1][:-4] + ' ' + html.escape(line.strip()) + '</p>'
            else:
                if in_list: out.append('</ul>'); in_list = False
                out.append('<p>%s</p>' % html.escape(line.strip()))
    if in_list: out.append('</ul>')
    # [인터뷰 필요]/[확인 필요]/[마스킹 확인] 강조
    joined = '\n'.join(out)
    joined = re.sub(r'(\[(?:인터뷰|확인|마스킹)[^\]]*\])', r'<mark>\1</mark>', joined)
    return joined

def main(inv_dir):
    cards = []
    for p in sorted(glob.glob(os.path.join(inv_dir, 'P*.md'))):
        r = parse_card(p)
        if r:
            meta, body = r
            meta['_file'] = os.path.basename(p)
            cards.append((meta, body))
    pending = sum(1 for m, b in cards if m.get('status') != 'confirmed')
    today = datetime.date.today().isoformat()

    rows, sections = [], []
    for meta, body in cards:
        cid = meta.get('id', '?')
        status = meta.get('status', 'draft')
        badge = '<span class="badge %s">%s</span>' % (status, status)
        rows.append(
            '<tr><td><a href="#%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (cid, cid, html.escape(meta.get('title', '')), html.escape(meta.get('period', '')),
               html.escape(meta.get('category', '')), badge))
        sections.append(
            '<article id="%s"><h3>%s. %s %s</h3>'
            '<div class="meta">%s · %s · <code>%s</code></div>%s</article>'
            % (cid, cid, html.escape(meta.get('title', '')), badge,
               html.escape(meta.get('period', '')), html.escape(meta.get('org', '')),
               html.escape(meta.get('_file', '')), md2html(body)))

    page = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex,nofollow">
<title>경력 원장 (비공개)</title>
<style>
:root {{ --text:#222; --muted:#767676; --link:#0b5394; --line:#ddd; --bg:#fff; --mark:#fff3bf; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --text:#d9dde3; --muted:#8f97a3; --link:#7badde; --line:#333a45; --bg:#14171c; --mark:#4a4020; }} }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:"Pretendard","Malgun Gothic","맑은 고딕",sans-serif; background:var(--bg);
       color:var(--text); line-height:1.7; font-size:15px; }}
.wrap {{ max-width:900px; margin:0 auto; padding:40px 24px 60px; }}
a {{ color:var(--link); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
.private {{ border:1px solid var(--line); border-left:3px solid #b3261e; padding:8px 14px;
           font-size:.85rem; color:var(--muted); margin-bottom:28px; }}
h1 {{ font-size:1.5rem; margin-bottom:4px; }}
.sub {{ color:var(--muted); font-size:.9rem; margin-bottom:24px; }}
table {{ width:100%; border-collapse:collapse; font-size:.9rem; margin-bottom:40px; }}
th {{ text-align:left; padding:6px 8px; border-bottom:2px solid var(--text); }}
td {{ padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
.badge {{ font-size:.75rem; padding:1px 8px; border-radius:8px; }}
.badge.draft {{ background:var(--mark); }}
.badge.confirmed {{ background:#d3f0d8; }}
@media (prefers-color-scheme: dark) {{ .badge.confirmed {{ background:#1f4025; }} }}
article {{ margin-bottom:36px; padding-bottom:20px; border-bottom:1px solid var(--line); }}
article h3 {{ font-size:1.1rem; margin-bottom:2px; }}
article h4 {{ font-size:.95rem; margin:12px 0 4px; color:var(--link); }}
article .meta {{ color:var(--muted); font-size:.85rem; margin-bottom:6px; }}
article ul {{ margin-left:18px; }}
article p, article li {{ font-size:.93rem; }}
mark {{ background:var(--mark); padding:0 3px; border-radius:2px; }}
code {{ font-size:.8rem; color:var(--muted); }}
</style></head><body><div class="wrap">
<div class="private">비공개 원장 — 내부 열람 전용. 이 파일은 생성물입니다 (직접 수정 금지, 카드 수정 후 build_ledger.py 재실행). 공개 페이지는 site/index.html.</div>
<h1>경력 원장</h1>
<div class="sub">카드 {n}장 · 미확정(draft) {pending}장 · 생성 {today}</div>
<table><tr><th>ID</th><th>프로젝트</th><th>기간</th><th>분류</th><th>상태</th></tr>
{rows}
</table>
{sections}
</div></body></html>""".format(n=len(cards), pending=pending, today=today,
                               rows='\n'.join(rows), sections='\n'.join(sections))

    out = os.path.join(inv_dir, 'ledger.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    print('OK: %s (cards=%d, draft=%d)' % (out, len(cards), pending))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'inventory')
