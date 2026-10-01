#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공고 레이더 — 잡코리아·인크루트 검색을 키워드별로 긁어 규칙으로 거른 뒤 data/jobs.json에 누적한다.

표준 라이브러리만 쓴다(GitHub Actions·다른 PC에서 pip 없이 돌게).
    python3 jobs/crawl.py            # jobs/config.json 기준
    python3 jobs/crawl.py --config jobs/config.example.json --out /tmp/x.json
개인 용도로 하루 1회만 돌린다. 요청 사이에 쉬고(SLEEP), 실패한 키워드는 건너뛴다.
"""
import argparse, html, json, os, re, sys, time, urllib.parse, urllib.request
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36'
SLEEP = 1.5
REGION_RE = r'(서울|경기|인천|부산|대구|대전|광주|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주|전국|해외)'


def fetch(url, enc='utf-8'):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ko'})
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read()
    return raw.decode(enc, errors='replace')


def strip(s):
    s = re.sub(r'<[^>]+>', '|', s)
    s = html.unescape(s)
    return [t.strip() for t in s.split('|') if t.strip()]


# ── 잡코리아 ─────────────────────────────────────────────────────────────
def jobkorea(kw):
    url = 'https://www.jobkorea.co.kr/Search/?stext=' + urllib.parse.quote(kw)
    t = fetch(url)
    out = []
    for card in re.split(r'data-sentry-component="CardJob"', t)[1:]:
        m = re.search(r'/Recruit/GI_Read/(\d+)', card)
        if not m:
            continue
        toks = strip(card.split('</div></div></div>')[0] if '</div></div></div>' in card else card[:6000])
        # 토큰 순서: [배지]* 스크랩 제목 회사 지역 직군 지원방법 경력 ...
        try:
            i = toks.index('스크랩')
        except ValueError:
            i = -1
        rest = toks[i + 1:]
        if len(rest) < 4:
            continue
        title, company = rest[0], rest[1]
        region = next((x for x in rest[2:] if re.match(REGION_RE, x)), '')
        group = next((x for x in rest[2:5] if x.endswith('그룹')), '')
        career = next((x for x in rest if re.match(r'(경력|신입)', x)), '')
        badge = ' '.join([x for x in toks[:i] if x in ('믿고보는 대기업', '대기업', '중견기업', '공기업')] + ([group] if group else []))
        deadline = next((x for x in rest if re.match(r'(D-\d+|~\s*\d{1,2}/\d{1,2}|상시|채용시|오늘마감|내일마감)', x)), '')
        out.append(dict(site='jobkorea', id='jk' + m.group(1), title=title, company=company, region=region,
                        career=career, deadline=deadline, badge=badge, tags=' '.join(rest[3:6]),
                        url='https://www.jobkorea.co.kr/Recruit/GI_Read/' + m.group(1)))
    return out


# ── 인크루트 (EUC-KR) ──────────────────────────────────────────────────────
def incruit(kw):
    url = 'https://search.incruit.com/list/search.asp?col=job&kw=' + urllib.parse.quote(kw, encoding='euc-kr')
    t = fetch(url, 'euc-kr')
    out = []
    for m in re.finditer(r'<li[^>]*>(.*?)</li>', t, re.S):
        blk = m.group(1)
        u = re.search(r'href="(https?://job\.incruit\.com/jobdb_info/jobpost\.asp\?job=(\d+))', blk)
        if not u:
            continue
        toks = strip(blk)
        toks = [x for x in toks if x not in ('관심기업', '1000대', '우수기업', '스크랩', '바로지원', '홈페이지 지원')]
        if len(toks) < 3:
            continue
        anchors = [html.unescape(re.sub(r'<[^>]+>', '', a)).strip() for a in re.findall(r'<a[^>]+jobpost\.asp[^>]*>(.*?)</a>', blk, re.S)]
        title = max(anchors, key=len) if anchors else toks[1]
        company = toks[0]
        group = next((x for x in toks[1:3] if x.endswith('그룹')), '')
        career = next((x for x in toks if re.match(r'(경력|신입)', x)), '')
        region = next((x for x in toks if re.match(REGION_RE, x)), '')
        deadline = next((x for x in toks if re.match(r'(~\s*\d{2}\.\d{2}|채용시|상시|\d+시 마감|오늘|내일)', x)), '')
        emp = next((x for x in toks if x in ('정규직', '계약직', '위촉직', '인턴', '파견직')), '')
        out.append(dict(site='incruit', id='ic' + u.group(2), title=title, company=company, region=region,
                        career=career, deadline=deadline, badge=group, tags=emp + ' ' + ' '.join(toks[2:8]),
                        url='https://job.incruit.com/jobdb_info/jobpost.asp?job=' + u.group(2)))
    return out


# ── 잡알리오 (공공기관 채용정보, job.alio.go.kr) ─────────────────────────────
def alio(kw):
    """제목 검색. 잡코리아·인크루트에 잘 안 올라오는 공기업·공공기관·정부기관 공고를 잡는다."""
    url = 'https://job.alio.go.kr/recruit.do?pageNo=1&pageSet=50&search_type=title&keyword=' + urllib.parse.quote(kw)
    t = fetch(url)
    out = []
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        r = m.group(1)
        u = re.search(r'recruitview\.do\?idx=(\d+)', r)
        if not u:
            continue
        tds = [html.unescape(re.sub(r'<[^>]+>', ' ', c)) for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
        tds = [re.sub(r'\s+', ' ', x).strip() for x in tds]
        if len(tds) < 8:
            continue
        title, org, region, emp, reg, due, state = tds[2], tds[3], tds[4], tds[5], tds[6], tds[7], tds[8] if len(tds) > 8 else ''
        if '진행' not in state and 'D-' not in due:  # 마감된 공고는 목록에 남아 있어도 버린다
            continue
        dm = re.search(r'D-(\d+)', due); dd = re.search(r'(\d{2})\.(\d{2})\.(\d{2})', due)
        deadline = ('~ %s.%s' % (dd.group(2), dd.group(3)) if dd else '') + (' D-%s' % dm.group(1) if dm else '')
        out.append(dict(site='alio', id='al' + u.group(1), title=title, company=org, region=region,
                        career='', deadline=deadline, badge='공공기관', tags=' '.join([emp, state]),
                        url='https://job.alio.go.kr/recruitview.do?idx=' + u.group(1)))
    return out


# ── 규칙 채점 ──────────────────────────────────────────────────────────────
def career_min(s):
    """'경력3년↑' '경력 5~14년' '신입·경력' → 최소 연수(신입=0, 미상=None)"""
    if not s:
        return None
    if '신입' in s and '경력' not in s:
        return 0
    m = re.search(r'(\d+)\s*(년|~)', s)
    return int(m.group(1)) if m else (0 if '무관' in s else None)


def score(j, cfg):
    text = ' '.join([j['title'], j['company'], j['tags'], j['region'], j['career']])
    s, why = 0, []
    for k in cfg['exclude_any']:
        if k in text:
            return -999, ['제외어: ' + k]
    yrs = career_min(j['career'])
    if yrs is not None and yrs > cfg['max_career_years']:
        return -999, ['경력 하한 %d년 > 내 %d년' % (yrs, cfg['max_career_years'])]
    if cfg.get('exclude_entry') and yrs == 0 and '경력' not in j['career']:
        return -999, ['신입 전형']
    for k, w in cfg['title_keywords'].items():
        if k in j['title']:
            s += w; why.append('제목:' + k)
    for k, w in cfg['company_tiers'].items():
        if k in j['company'] or k in j['badge']:
            s += w; why.append('회사:' + k)
    if j['badge']:
        s += cfg.get('badge_bonus', 0); why.append('배지:' + j['badge'])
    for k, w in cfg['region_weights'].items():
        if j['region'].startswith(k):
            s += w; why.append('지역:' + k)
            break
    for k, w in cfg.get('tag_keywords', {}).items():
        if k in j['tags']:
            s += w; why.append('태그:' + k)
    return s, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=os.path.join(HERE, 'config.json'))
    ap.add_argument('--out', default=os.path.join(HERE, 'data', 'jobs.json'))
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf-8'))
    store = json.load(open(a.out, encoding='utf-8')) if os.path.exists(a.out) else {'jobs': {}, 'runs': []}
    today = date.today().isoformat()
    seen, fetched, errors = {}, 0, []
    for kw in cfg['keywords'] + [k for k in cfg.get('alio_keywords', []) if k not in cfg['keywords']]:
        for fn in (jobkorea, incruit) + ((alio,) if cfg.get('alio') else ()):
            if fn is alio and kw not in cfg.get('alio_keywords', cfg['keywords']):
                continue
            if fn is not alio and kw not in cfg['keywords']:
                continue
            try:
                rows = fn(kw); fetched += len(rows)
            except Exception as e:  # 한 키워드 실패는 건너뛴다
                errors.append('%s/%s: %s' % (fn.__name__, kw, e)); rows = []
            for j in rows:
                j.setdefault('kw', set())
                if j['id'] in seen:
                    seen[j['id']]['kw'].add(kw)
                else:
                    j['kw'] = {kw}; seen[j['id']] = j
            time.sleep(SLEEP)
    new = 0
    for jid, j in seen.items():
        j['kw'] = sorted(j['kw'])
        sc, why = score(j, cfg)
        j['score'], j['why'] = sc, why
        if sc <= cfg['min_score']:
            continue
        old = store['jobs'].get(jid)
        if old:
            old.update({k: j[k] for k in ('title', 'company', 'region', 'career', 'deadline', 'tags', 'score', 'why', 'kw')})
            old['last_seen'] = today
        else:
            j['first_seen'] = j['last_seen'] = today
            store['jobs'][jid] = j; new += 1
    # 30일 넘게 안 보이면 지운다
    cutoff = datetime.now().timestamp() - 30 * 86400
    for jid in list(store['jobs']):
        if datetime.fromisoformat(store['jobs'][jid]['last_seen']).timestamp() < cutoff:
            del store['jobs'][jid]
    store['runs'] = (store['runs'] + [dict(date=today, fetched=fetched, kept=len(store['jobs']), new=new, errors=errors)])[-60:]
    if a.dry:
        print(json.dumps(store['runs'][-1], ensure_ascii=False)); return
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(store, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('fetched %d · kept %d · new %d · errors %d' % (fetched, len(store['jobs']), new, len(errors)))
    for e in errors:
        print('  !', e)


if __name__ == '__main__':
    main()
