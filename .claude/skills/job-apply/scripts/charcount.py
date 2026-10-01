#!/usr/bin/env python3
"""자소서 md의 문항별 글자수 실측.
사용: python charcount.py 02_resume_final.md [--json]
문항 = '## ' 헤딩이 숫자로 시작하는 절. 헤딩의 '(300~750자)' 범위를 자동 인식.
HTML 주석·인용문(>)·구분선·【 】자리표시는 제외."""
import re, sys, json

def sections(md, keep_placeholders=False):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    out = []
    for m in re.finditer(r'^## (\d+)[.．]\s*(.*?)$\n(.*?)(?=^## |\Z)', md, flags=re.S | re.M):
        num, title, body = m.group(1), m.group(2), m.group(3)
        body = '\n'.join(l for l in body.split('\n') if not l.startswith('>') and l.strip() != '---')
        if not keep_placeholders: body = re.sub(r'【.*?】', '', body)
        body = body.strip()
        rng = re.search(r'\((\d[\d,]*)\s*[~～-]\s*(\d[\d,]*)\s*자', title)
        lo, hi = (int(rng.group(1).replace(',', '')), int(rng.group(2).replace(',', ''))) if rng else (None, None)
        out.append(dict(num=int(num), title=title, lo=lo, hi=hi, body=body))
    return out

def measure(body):
    incl_nl = len(body)
    incl = len(body.replace('\n', ''))
    excl = len(re.sub(r'\s', '', body))
    sents = [s.strip() for s in re.split(r'(?<=[.다요]\.)\s+|(?<=[다요])\.\s+|\n', body) if s.strip()]
    sents = [s for s in sents if not s.startswith('[')]
    long = [s for s in sents if len(s) > 60]
    return dict(incl_nl=incl_nl, incl=incl, excl=excl, sentences=len(sents), over60=len(long), over60_list=long)

def main():
    path = sys.argv[1]; as_json = '--json' in sys.argv
    md = open(path, encoding='utf-8').read()
    rows = []
    for s in sections(md):
        m = measure(s['body'])
        pct = round(m['incl'] / s['hi'] * 100) if s['hi'] else None
        ok = (s['lo'] is None) or (s['lo'] <= m['incl'] <= s['hi'])
        rows.append(dict(num=s['num'], title=s['title'], lo=s['lo'], hi=s['hi'], pct=pct, ok=ok, **m))
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1)); return
    print(f"{'문항':<4}{'범위':<12}{'공백포함':>8}{'줄바꿈포함':>10}{'공백제외':>8}{'상한%':>6}{'60자+':>6}  판정")
    for r in rows:
        rng = f"{r['lo']}~{r['hi']}" if r['hi'] else '-'
        print(f"{r['num']:<4}{rng:<12}{r['incl']:>8}{r['incl_nl']:>10}{r['excl']:>8}{str(r['pct'])+'%' if r['pct'] else '-':>6}{r['over60']:>6}  {'통과' if r['ok'] else '범위 밖'}")
        for s in r['over60_list']:
            print(f"      [{len(s)}자] {s[:70]}…")

if __name__ == '__main__':
    main()
