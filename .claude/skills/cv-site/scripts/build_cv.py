# -*- coding: utf-8 -*-
"""cv.yaml -> site/index.html 빌더.

원칙: site/index.html은 생성물 — 직접 수정 금지. 내용 변경은 cv.yaml에서,
디자인 변경은 이 스크립트의 템플릿에서 한다. cv.yaml의 card: 필드는
inventory/ 카드 참조(사실 추적용)이며 출력에는 포함되지 않는다.

사용:  python build_cv.py [프로젝트 루트]   (기본: 현재 디렉토리에 cv.yaml이 있는 위치)
"""
import sys, os, html, yaml

def esc(s):
    return html.escape(str(s), quote=False) if s is not None else ''

def render(d):
    p = d['profile']
    links = ' ·\n        '.join(
        '<a href="%s">%s</a>' % (l['url'], esc(l['label'])) for l in p['links'])
    contact = links
    if p.get('contact_prefix'):
        contact = esc(p['contact_prefix']) + ' ' + contact
    if p.get('location'):
        contact += ' ·\n        <span>%s</span>' % esc(p['location'])

    exp = []
    for e in d['experience']:
        bullets = ''
        if e.get('bullets'):
            # bullet이 {html: ...} 형태면 링크 등 HTML 그대로 사용, 문자열이면 이스케이프
            bullets = '\n        <ul>\n%s\n        </ul>' % '\n'.join(
                '          <li>%s</li>' % (b['html'] if isinstance(b, dict) else esc(b))
                for b in e['bullets'])
        exp.append('''    <div class="entry">
      <div class="date">%s</div>
      <div class="body"><img src="%s" class="orglogo" alt=""><b>%s</b> · %s
        <div class="sub">%s</div>%s
      </div>
    </div>''' % (esc(e['date']), e['logo'], esc(e['org']), esc(e['role']),
                 esc(e.get('sub', '')), bullets))

    projs = []
    for pr in d['projects']:
        result = ''
        if pr.get('result'):
            # result는 문자열 또는 목록 (여러 성과 줄)
            items = pr['result'] if isinstance(pr['result'], list) else [pr['result']]
            result = ''.join('\n        <div class="result">%s</div>' % esc(r) for r in items)
        # url이 있으면 펼친 본문 안에 홈페이지 링크 (제목 링크는 펼침 클릭과 충돌하므로 금지)
        link = ''
        if pr.get('url'):
            link = '\n        <div class="plink"><a href="%s" target="_blank" rel="noopener">홈페이지 바로가기 ↗</a></div>' % pr['url']
        # links 목록이 있으면 항목별 링크 (보고서·산출물 등)
        if pr.get('links'):
            link += ''.join(
                '\n        <div class="plink"><a href="%s" target="_blank" rel="noopener">%s ↗</a></div>'
                % (l['url'], esc(l['label'])) for l in pr['links'])
        # role(선택): 접힘 상태 둘째 줄의 '역할 · 핵심 성과' 중 역할 
        role = '<span class="role">%s</span>' % esc(pr['role']) if pr.get('role') else ''
        projs.append('''    <details class="proj">
      <summary><span class="name">%s</span> <span class="date">%s</span> <span class="meta">%s<span class="gist">%s</span></span></summary>
      <div class="pbody">
        <div class="desc">%s</div>%s%s
      </div>
    </details>''' % (esc(pr['name']), esc(pr['date']), role, esc(pr['gist']), esc(pr['desc']), result, link))

    # Outside Work (선택 섹션 — 사이드 프로젝트·취미 등 업무 밖 활동. cv.yaml에 outside_work가
    # 있을 때만 렌더, 구 키 side_projects도 허용). Education 아래 맨 끝에 배치
    side = ''
    outside = d.get('outside_work') or d.get('side_projects')
    if outside:
        rows = '\n'.join('''    <div class="proj" style="margin-bottom: 14px;">
      <div class="name"><a href="%s" target="_blank" rel="noopener">%s</a> <span class="date">%s</span></div>
      <div class="desc">%s</div>
    </div>''' % (s['url'], esc(s['name']), esc(s.get('date', '')), esc(s['desc']))
                         for s in outside)
        side = '''
  <section>
    <h2>Outside Work</h2>
%s
  </section>
''' % rows

    # 인쇄 페이지 그룹: Projects 다음 그룹은 Skills에서 시작(새 페이지)
    skills_pb = ' class="pb"'

    skills = '\n'.join('      <li>%s</li>' % esc(s) for s in d['skills'])

    talks = '\n'.join('''    <div class="entry">
      <div class="date">%s</div>
      <div class="body"><b>%s</b>
        <div class="sub">%s</div>
      </div>
    </div>''' % (esc(t['date']), esc(t['title']), esc(t['sub'])) for t in d['talks'])

    awards = '\n'.join('''    <div class="entry">
      <div class="date">%s</div>
      <div class="body">%s<b>%s</b><span class="aside">%s</span></div>
    </div>''' % (esc(a['date']),
                 '<img src="%s" class="orglogo" alt="">' % a['logo'] if a.get('logo') else '',
                 esc(a['title']), esc(a['desc'])) for a in d['awards'])

    edu = []
    for e in d['education']:
        if e.get('org'):
            edu.append('''    <div class="entry">
      <div class="date">%s</div>
      <div class="body"><img src="%s" class="orglogo" alt=""><b>%s</b> · %s
        <div class="sub">%s</div>
      </div>
    </div>''' % (esc(e['date']), e['logo'], esc(e['org']), esc(e['role']), esc(e.get('sub', ''))))
        else:
            issuer = ''
            if e.get('issuer'):
                issuer = ' <span class="sub" style="display:inline; color:var(--muted); font-size:0.93rem; margin-left:8px;">%s</span>' % esc(e['issuer'])
            edu.append('''    <div class="entry">
      <div class="date">%s</div>
      <div class="body">%s%s</div>
    </div>''' % (esc(e['date']), esc(e['body']), issuer))

    # 링크 미리보기(카카오톡·슬랙 등) — meta.url + meta.og_image가 있을 때만 출력
    og = ''
    m = d['meta']
    if m.get('url') and m.get('og_image'):
        base = m['url'].rstrip('/') + '/'
        og = '''<meta property="og:type" content="profile">
<meta property="og:url" content="%s">
<meta property="og:site_name" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="%s">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="%s">
''' % (base, esc(m['title']), esc(m['title']), esc(m['description']),
       base + m['og_image'] + '?v=' + str(m['updated']), base)

    # 방문 통계(선택): meta.goatcounter에 GoatCounter 코드(예: myname)가 있으면 집계 스크립트를 넣는다.
    # 쿠키 없음·화면 표시 없음. 숫자는 https://{코드}.goatcounter.com 에 로그인한 본인만 본다. 없으면 아무것도 넣지 않는다.
    stats = ''
    if m.get('goatcounter'):
        stats = ('<script data-goatcounter="https://%s.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>\n'
                 % esc(str(m['goatcounter'])))

    return TEMPLATE % {
        'title': esc(d['meta']['title']), 'description': esc(d['meta']['description']),
        'name': esc(p['name']), 'name_en': esc(p['name_en']), 'tagline': esc(p['tagline']),
        'affil': esc(p['affil']), 'photo': p['photo'],
        'contact': contact, 'about': esc(d['about']),
        'experience': '\n'.join(exp), 'projects': '\n'.join(projs),
        'side_projects': side, 'skills': skills, 'skills_pb': skills_pb,
        'talks': talks, 'awards': awards, 'education': '\n'.join(edu),
        'updated': esc(d['meta']['updated']), 'og': og, 'stats': stats,
    }

TEMPLATE = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(description)s">
%(og)s<style>
  :root {
    /* 주요색 #1a73e8 */
    --text: #222; --muted: #767676; --link: #1a73e8;
    --line: #dddddd; --bg: #ffffff;
  }
  @media (prefers-color-scheme: dark) {
    :root { --text: #d9dde3; --muted: #8f97a3; --link: #8ab4f8; --line: #333a45; --bg: #14171c; }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: "Pretendard", "Malgun Gothic", "맑은 고딕", "Helvetica Neue", Arial, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15.5px;
    -webkit-font-smoothing: antialiased;
    /* 어절 보존 + 줄글 문단은 양쪽 정렬 — 단어 안 잘리고 오른쪽도 반듯 */
    word-break: keep-all; overflow-wrap: break-word;
  }
  /* 폭 820→900, 타이포 위계·섹션 여백 강화 */
  .wrap { max-width: 900px; margin: 0 auto; padding: 64px 28px 72px; }
  a { color: var(--link); text-decoration: none; }
  a:hover { text-decoration: underline; }

  .profile { display: flex; gap: 32px; align-items: center; margin-bottom: 20px; }
  .photo {
    width: 136px; height: 136px; border-radius: 50%%; flex-shrink: 0;
    object-fit: cover; object-position: top;
    background: #e9edf2; color: #9aa4b0; display: flex; align-items: center;
    justify-content: center; font-size: 2rem; font-weight: 600; letter-spacing: 1px;
  }
  @media (prefers-color-scheme: dark) { .photo { background: #232933; color: #5d6673; } }
  .profile h1 { font-size: 2.25rem; font-weight: 700; letter-spacing: -0.8px; line-height: 1.25; }
  .profile h1 .en { font-weight: 400; color: var(--muted); font-size: 1.15rem; margin-left: 10px; letter-spacing: 0; }
  .profile .title { margin-top: 8px; font-size: 1.02rem; font-weight: 500; }
  .profile .affil { color: var(--muted); font-size: 0.95rem; margin-top: 2px; }
  .profile .contact { margin-top: 14px; font-size: 0.92rem; color: var(--muted); }

  section { margin-top: 54px; }
  h2 {
    font-size: 1.35rem; font-weight: 700; letter-spacing: -0.2px;
    padding-bottom: 9px; border-bottom: 1px solid var(--line); margin-bottom: 20px;
  }
  .bio { text-align: justify; font-size: 1rem; }

  .entry { display: grid; grid-template-columns: 140px 1fr; gap: 8px 22px; margin-bottom: 20px; }
  .entry .date { color: var(--muted); font-size: 0.9rem; padding-top: 2px; white-space: nowrap; font-variant-numeric: tabular-nums; }
  .entry .body b { font-weight: 600; }
  .orglogo { width: 20px; height: 20px; vertical-align: -4px; margin-right: 7px; }
  .entry .body .sub { color: var(--muted); font-size: 0.93rem; }
  .entry .body ul { margin: 6px 0 0 0; list-style: none; }
  .entry .body ul li { font-size: 0.93rem; color: var(--muted); padding-left: 12px; text-indent: -12px; }
  .entry .body ul li::before { content: "–"; margin-right: 7px; }

  /* Projects — 접힘 상태: 1행 이름+기간(오른쪽), 2행 역할 · 핵심 성과. 한눈에 스캔하고 관심 있는 것만 펼친다 */
  details.proj { border-bottom: 1px solid var(--line); }
  h2.tight { margin-bottom: 6px; }
  details.proj summary {
    cursor: pointer; list-style: none; display: grid; grid-template-columns: 18px 1fr auto;
    gap: 2px 8px; padding: 13px 0; align-items: baseline;
  }
  details.proj summary::-webkit-details-marker { display: none; }
  details.proj summary::before { content: "▸"; color: var(--muted); font-size: 0.8rem; grid-row: 1; grid-column: 1; }
  details.proj[open] summary::before { content: "▾"; }
  details.proj summary:hover .name { color: var(--link); }
  .proj .name { font-weight: 600; }
  details.proj summary .name { grid-row: 1; grid-column: 2; font-size: 1.02rem; }
  .proj .date { color: var(--muted); font-size: 0.9rem; font-weight: 400; margin-left: 6px; font-variant-numeric: tabular-nums; }
  details.proj summary .date { grid-row: 1; grid-column: 3; margin-left: 0; white-space: nowrap; }
  /* 구분은 대시(—) 대신 간격+회색으로 한다 (대시 반복이 AI 생성물처럼 보인다는 피드백) */
  .proj .meta { grid-row: 2; grid-column: 2 / 4; color: var(--muted); font-size: 0.92rem; }
  .proj .meta .role { color: var(--text); opacity: 0.78; }
  .proj .meta .role::after { content: "·"; margin: 0 7px; color: var(--muted); }
  .proj .gist { color: var(--muted); font-size: 0.92rem; }
  .aside { color: var(--muted); margin-left: 10px; }
  .proj .pbody { padding: 0 0 16px 26px; }
  .proj .desc { font-size: 0.95rem; text-align: justify; margin-bottom: 6px; }
  .proj .result { font-size: 0.95rem; }
  .proj .result::before { content: "· "; color: var(--muted); }
  .proj .plink { font-size: 0.9rem; margin-top: 4px; }

  ul.plain { list-style: none; }
  ul.plain li { margin-bottom: 8px; padding-left: 14px; text-indent: -14px; }
  ul.plain li::before { content: "·"; margin-right: 8px; color: var(--muted); }

  footer { margin-top: 64px; padding-top: 16px; border-top: 1px solid var(--line);
           font-size: 0.85rem; color: var(--muted); }

  /* PDF 내보내기 버튼 — 화면 전용, 인쇄물에는 미출력 */
  .pdf-btn {
    position: fixed; right: 24px; bottom: 24px;
    background: var(--link); color: #fff; border: none; border-radius: 24px;
    padding: 10px 18px; font-size: 0.9rem; font-family: inherit; cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18);
  }
  .pdf-btn:hover { opacity: 0.88; }
  /* ===== 인쇄 규칙: 섹션 단위 페이지 구성 + 하단 페이지 번호 ===== */
  @page {
    size: A4;
    margin: 16mm 14mm 18mm;
    @bottom-center { content: "- " counter(page) " -"; font-size: 9pt; color: #888888; }
  }
  @media print {
    .pdf-btn { display: none; }
    .proj .plink { display: none; }  /* 종이에서는 클릭 불가 */
    a { color: inherit; text-decoration: none; }  /* 인쇄물에서 링크 파랑 제거 */
    body { font-size: 13.5px; }
    .wrap { max-width: none; padding: 0; }
    section { margin-top: 30px; }
    .profile h1 { font-size: 1.9rem; }
    h2 { font-size: 1.2rem; margin-bottom: 12px; }
    .entry { margin-bottom: 12px; }
    details.proj summary { padding: 8px 0; }
    /* 주요 섹션(.pb)은 새 페이지에서 시작 — 1p 프로필+About / 2p Experience /
       3p~ Projects / 이후 Side+Skills+Talks / Awards+Education */
    .pb { break-before: page; }
    /* 항목이 페이지 경계에서 잘리지 않도록 */
    .entry, details.proj, .proj { break-inside: avoid; }
    section h2 { break-after: avoid; }  /* 섹션 제목만 남고 내용이 넘어가는 것 방지 */
  }

  /* ===== 모바일 재배치 (600px 이하) ===== */
  @media (max-width: 600px) {
    .wrap { padding: 32px 18px 52px; }
    section { margin-top: 40px; }
    h2 { font-size: 1.2rem; margin-bottom: 14px; }

    /* 프로필: 세로 배치, 사진 축소, 영문 이름은 둘째 줄 */
    .profile { flex-direction: column; align-items: flex-start; gap: 16px; margin-bottom: 8px; }
    .photo { width: 96px; height: 96px; }
    .profile h1 { font-size: 1.75rem; letter-spacing: -0.5px; }
    .profile h1 .en { display: block; margin-left: 0; font-size: 0.98rem; margin-top: 2px; }

    /* 날짜 컬럼 제거 → 날짜가 내용 위에 작게 */
    .entry { grid-template-columns: 1fr; gap: 2px; margin-bottom: 20px; }
    .entry .date { padding-top: 0; font-size: 0.83rem; }

    /* 프로젝트: 이름 → 기간 → 역할·성과 순으로 세 줄, 탭 타깃 확대 */
    details.proj summary { grid-template-columns: 16px 1fr; padding: 12px 0; }
    details.proj summary .date { grid-row: 2; grid-column: 2; font-size: 0.83rem; }
    .proj .meta { grid-row: 3; grid-column: 2; }
    .proj .pbody { padding-left: 24px; }

    /* PDF 버튼: 축소 + 가장자리 여백 축소 */
    .pdf-btn { right: 14px; bottom: 14px; padding: 9px 14px; font-size: 0.85rem; }
  }
</style>
</head>
<body>
<div class="wrap">

  <header class="profile">
    <img src="%(photo)s" class="photo" alt="%(name)s 증명사진">
    <div>
      <h1>%(name)s<span class="en">%(name_en)s</span></h1>
      <div class="title">%(tagline)s</div>
      <div class="affil">%(affil)s</div>
      <div class="contact">
        %(contact)s
      </div>
    </div>
  </header>

  <section>
    <h2>About</h2>
    <p class="bio">%(about)s</p>
  </section>

  <section>
    <h2>Experience</h2>
%(experience)s
  </section>

  <section class="pb">
    <h2 class="tight">Projects</h2>
%(projects)s
  </section>

  <section%(skills_pb)s>
    <h2>Skills</h2>
    <ul class="plain">
%(skills)s
    </ul>
  </section>

  <section>
    <h2>Talks</h2>
%(talks)s
  </section>

  <section class="pb">
    <h2>Honors &amp; Awards</h2>
%(awards)s
  </section>

  <section>
    <h2>Education &amp; Certifications</h2>
%(education)s
  </section>
%(side_projects)s
  <footer>Last updated %(updated)s</footer>

</div>
<button class="pdf-btn" onclick="window.print()" title="브라우저 인쇄 대화상자에서 'PDF로 저장'을 선택하세요">PDF로 저장</button>
<script>
  // 인쇄 시 접힌 프로젝트를 전부 펼치고, 인쇄 후 원상 복구
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('details').forEach(function (d) {
      d.dataset.wasOpen = d.open ? '1' : '';
      d.open = true;
    });
  });
  window.addEventListener('afterprint', function () {
    document.querySelectorAll('details').forEach(function (d) {
      d.open = d.dataset.wasOpen === '1';
    });
  });
</script>
%(stats)s</body>
</html>
'''

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    src = os.path.join(root, 'cv.yaml')
    out = os.path.join(root, 'site', 'index.html')
    with open(src, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    page = render(data)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    print('OK: %s (%d bytes) <- %s' % (out, len(page), src))

if __name__ == '__main__':
    main()
