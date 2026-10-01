# -*- coding: utf-8 -*-
"""cv.yaml -> site/assets/og-card.png (링크 미리보기용 명함 이미지, 1200x630).

카카오톡·슬랙·링크드인 등이 og:image로 가져가는 썸네일이다. 프로필 사진만 크게 잘려
보이는 대신, CV 상단 프로필 블록(사진·이름·직함·소속)을 명함처럼 보여준다.
미리보기는 작게 표시되므로 글자를 크게, 중앙 안전영역 안에 둔다.

프로필(이름·직함·소속·사진)이 바뀌면 다시 실행한다. Edge 또는 Chrome 필요.

사용:  python build_og.py [프로젝트 루트]
"""
import sys, os, html, shutil, subprocess, tempfile, yaml

BROWSERS = [
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'msedge', 'google-chrome', 'chromium',
]

CARD = '''<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1200px; height:630px; overflow:hidden; }
  body { background:#ffffff; color:#222;
    font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic","맑은 고딕","Helvetica Neue",Arial,sans-serif;
    -webkit-font-smoothing:antialiased; word-break:keep-all;
    display:flex; align-items:center; justify-content:center; }
  .card { display:flex; align-items:center; gap:56px; padding:0 70px; width:100%%; }
  .photo { width:280px; height:280px; border-radius:50%%; flex-shrink:0;
    object-fit:cover; object-position:top; background:#e9edf2; }
  .name { font-size:76px; font-weight:700; line-height:1.15; letter-spacing:-1px; }
  .name span { font-size:42px; font-weight:400; color:#767676; margin-left:14px; letter-spacing:0; }
  .tagline { font-size:33px; line-height:1.35; margin-top:22px; white-space:nowrap; }
  .affil { font-size:28px; line-height:1.45; color:#767676; margin-top:14px; }
  .url { font-size:28px; color:#1a73e8; margin-top:30px; }
  .bar { position:fixed; left:0; right:0; bottom:0; height:10px; background:#1a73e8; }
</style></head>
<body>
  <div class="card">
    <img class="photo" src="%(photo)s" alt="">
    <div>
      <div class="name">%(name)s<span>%(name_en)s</span></div>
      <div class="tagline">%(tagline)s</div>
      <div class="affil">%(affil)s</div>
      <div class="url">%(host)s</div>
    </div>
  </div>
  <div class="bar"></div>
</body></html>
'''

def esc(s):
    return html.escape(str(s), quote=False) if s is not None else ''

def find_browser():
    for b in BROWSERS:
        if os.path.isfile(b) or shutil.which(b):
            return b
    sys.exit('ERR: Edge/Chrome을 찾지 못했습니다.')

def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    with open(os.path.join(root, 'cv.yaml'), encoding='utf-8-sig') as f:
        d = yaml.safe_load(f)
    p, meta = d['profile'], d['meta']
    out = os.path.join(root, 'site', meta.get('og_image', 'assets/og-card.png'))
    photo = 'file://' + os.path.join(root, 'site', p['photo']).replace('\\', '/')
    host = meta.get('url', '').replace('https://', '').replace('http://', '').strip('/')
    # 소속은 ' · ' 기준으로 줄바꿈해 작은 썸네일에서도 읽히게 한다
    affil = '<br>'.join(esc(a.strip()) for a in p['affil'].split('·'))
    page = CARD % {'photo': photo, 'name': esc(p['name']), 'name_en': esc(p['name_en']),
                   'tagline': esc(p['tagline']), 'affil': affil, 'host': esc(host)}
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'og.html')
        with open(src, 'w', encoding='utf-8') as f:
            f.write(page)
        subprocess.run([find_browser(), '--headless=new', '--hide-scrollbars',
                        '--force-device-scale-factor=1', '--window-size=1200,630',
                        '--screenshot=' + out, 'file://' + src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('OK: %s (%d bytes)' % (out, os.path.getsize(out)))

if __name__ == '__main__':
    main()
