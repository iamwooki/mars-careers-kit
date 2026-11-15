#!/usr/bin/env python3
"""ChatGPT(codex exec) 의뢰 래퍼 — 빈 임시 폴더에서 읽기 전용으로 돌리고 출력 파일만 회수한다.
사용: python ask_chatgpt.py 03_chatgpt_의뢰서.md --out 03_chatgpt_원본출력.md [--dry-run]
                           [--effort high] [--codex 실행파일] [--deny 금지어,금지어] [--deny-file 파일]
                           [--timeout 900] [--force]
--dry-run: 의뢰서 점검과 임시 폴더 준비까지만 하고, 실행될 명령을 그대로 출력한다(외부로 아무것도 보내지 않는다).
보내기 전 점검(하나라도 걸리면 중단): 남은 {자리표시}·HTML 주석, 주민번호·전화·이메일 꼴, 금지어.
금지어 목록은 --deny/--deny-file, 그리고 있으면 applications/_reference/chatgpt_금지어.txt(한 줄에 하나)를 읽는다.
의뢰서 본문은 표준입력으로만 넘기고 폴더는 넘기지 않는다. 원본출력은 --force 없이는 덮어쓰지 않는다."""
import argparse, os, re, shlex, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))   # career 폴더 (스크립트 위치 기준)
DENY_DEFAULT = os.path.join(ROOT, 'applications', '_reference', 'chatgpt_금지어.txt')
APP_CODEX = os.path.join(os.sep, 'Applications', 'ChatGPT.app', 'Contents', 'Resources', 'codex')  # macOS ChatGPT 앱에 든 codex
PATTERNS = [('주민등록번호 꼴', r'\b\d{6}\s*-\s*[1-4]\d{6}\b'), ('전화번호 꼴', r'\b01[016-9][-.\s]?\d{3,4}[-.\s]?\d{4}\b'),
            ('이메일 주소', r'[\w.+-]+@[\w-]+\.[\w.-]+')]

def find_codex(explicit=None):
    """--codex를 주면 그것만 본다. 없으면 환경변수 CODEX_BIN → PATH의 codex → ChatGPT 앱 번들 순."""
    for c in ((explicit,) if explicit else (os.environ.get('CODEX_BIN'), shutil.which('codex'), APP_CODEX)):
        if c and os.path.isfile(c) and os.access(c, os.X_OK): return c
    return None

def load_deny(terms, path):
    out = [t.strip() for t in (terms or '').split(',') if t.strip()]
    for p in (path, DENY_DEFAULT):
        if p and os.path.exists(p):
            out += [l.strip() for l in open(p, encoding='utf-8') if l.strip() and not l.startswith('#')]
    return sorted(set(out))

def lint(text, deny):
    """의뢰서에 보내면 안 되는 것이 남았는지 본다. 문제 목록(빈 목록이면 통과)."""
    errs = []
    ph = re.findall(r'\{[^{}\n]+\}', text)
    if ph: errs.append(f'채우지 않은 자리표시 {len(ph)}개: ' + ', '.join(x[:30] for x in ph[:5]))
    if '<!--' in text: errs.append('HTML 주석이 남아 있음(템플릿의 점검표 주석을 지우지 않았거나 내부 메모가 섞임)')
    for name, pat in PATTERNS:
        hit = re.findall(pat, text)
        if hit: errs.append(f'{name} {len(hit)}건')
    for t in deny:
        if t in text: errs.append(f'금지어 포함: {t}')
    return errs

def build_cmd(codex, tmp_out, effort):
    return [codex, 'exec', '--skip-git-repo-check', '-s', 'read-only',
            '-c', f'model_reasoning_effort="{effort}"', '-o', tmp_out, '-']

def collect(tmp, tmp_out, dest):
    """임시 폴더의 출력 파일을 dest로 옮기고 임시 폴더를 지운다. 출력 말고 다른 파일이 생겼으면 이름을 돌려준다."""
    if not os.path.exists(tmp_out) or os.path.getsize(tmp_out) == 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError('출력 파일이 없거나 비어 있습니다')
    extra = sorted(f for f in os.listdir(tmp) if os.path.join(tmp, f) != tmp_out)
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    shutil.copyfile(tmp_out, dest)
    shutil.rmtree(tmp, ignore_errors=True)
    return extra

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('brief'); ap.add_argument('--out', required=True)
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--force', action='store_true')
    ap.add_argument('--effort', default='high', choices=['low', 'medium', 'high'])
    ap.add_argument('--codex'); ap.add_argument('--deny'); ap.add_argument('--deny-file')
    ap.add_argument('--timeout', type=int, default=900)
    a = ap.parse_args()

    brief = os.path.abspath(a.brief); dest = os.path.abspath(a.out)
    if not os.path.isfile(brief): sys.exit(f'의뢰서가 없습니다: {a.brief}')
    text = open(brief, encoding='utf-8').read()
    deny = load_deny(a.deny, a.deny_file)
    errs = lint(text, deny)
    print(f'의뢰서 {os.path.basename(brief)} · {len(text):,}자 · 금지어 {len(deny)}개 대조')
    if errs:
        print('점검 실패 — 보내지 않았습니다:'); [print('  -', e) for e in errs]; sys.exit(2)
    print('점검 통과 (자리표시·주석·식별 정보 꼴·금지어). 사실·수위는 메인 세션이 점검표로 따로 확인한다.')
    if os.path.exists(dest) and not a.force:
        sys.exit(f'원본출력이 이미 있습니다(덮어쓰지 않음): {a.out} — 다른 이름을 주거나 --force')

    codex = find_codex(a.codex)
    tmp = tempfile.mkdtemp(prefix='jobapply_codex_')            # 빈 임시 폴더: codex가 읽을 파일이 없다
    tmp_out = os.path.join(tmp, 'output.md')
    cmd = build_cmd(codex or 'codex', tmp_out, a.effort)
    shown = f'cd {shlex.quote(tmp)} && {" ".join(shlex.quote(c) for c in cmd)} < {shlex.quote(brief)}'
    if a.dry_run:
        print(f'[dry-run] 빈 임시 폴더 준비 확인: {tmp} (파일 {len(os.listdir(tmp))}개)')
        if not codex: print('[dry-run] 경고: codex 실행파일을 찾지 못했습니다 — --codex 또는 CODEX_BIN으로 지정하세요')
        print('[dry-run] 실행될 명령:'); print('  ' + shown)
        print(f'[dry-run] 출력 회수 위치: {a.out}')
        shutil.rmtree(tmp, ignore_errors=True)
        print('[dry-run] 실행하지 않았고 임시 폴더는 지웠습니다. 실제 실행 때는 새 임시 폴더를 만듭니다.')
        return
    if not codex:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit('codex 실행파일을 찾지 못했습니다 — --codex 또는 CODEX_BIN으로 지정하세요')
    print('실행:', shown)
    try:
        with open(brief, encoding='utf-8') as f:
            r = subprocess.run(cmd, stdin=f, cwd=tmp, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp, ignore_errors=True); sys.exit(f'{a.timeout}초 안에 끝나지 않아 중단했습니다')
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True); sys.exit(f'codex가 오류로 끝났습니다 (exit {r.returncode})')
    try:
        extra = collect(tmp, tmp_out, dest)
    except RuntimeError as e:
        sys.exit(str(e))
    if extra: print('경고: 임시 폴더에 출력 말고 다른 파일이 생겼습니다(버림):', ', '.join(extra))
    print('written', a.out, f'({os.path.getsize(dest):,} bytes) — 원본이므로 고치지 않는다. 다음: build_compare.py')

if __name__ == '__main__':
    main()
