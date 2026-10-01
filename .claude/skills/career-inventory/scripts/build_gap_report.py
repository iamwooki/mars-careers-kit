#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inventory/gap.yaml + 카드 → inventory/gap_report.html (STAR-I 갭 분석: 무엇을 더 채워야 하는가)

사용:  python build_gap_report.py [프로젝트 루트]
원칙:  gap_report.html은 생성물이다. 진단·질문은 gap.yaml에서 고친다 (양식: assets/gap_template.yaml).
       질문은 세 상태다 — answer가 있으면 '답함', wait: true면 '자료 대기', 둘 다 없으면 '남음'(메모 칸이 열린다).
       메모는 브라우저(localStorage)에 저장되고 '답변 전체 복사'로 내보내 Claude에 붙여 넣는다.
"""
import sys, os, re, html, glob, datetime
import yaml

e = html.escape
SEC = ['S', 'T', 'A', 'R', 'I']
SECNAME = {'S': '상황', 'T': '과제', 'A': '행동', 'R': '성과', 'I': '증빙'}
LV = ['빈약', '보통', '충분']

CSS = """
:root{--bg:#fff;--fg:#202124;--mut:#5f6368;--line:#e0e0e0;--blue:#1a73e8;--soft:#f6f8fc;--r0:#fce8e6;--r0f:#a50e0e;--r1:#fef7e0;--r1f:#8a5a00;--r2:#e6f4ea;--r2f:#0d652d}
@media (prefers-color-scheme:dark){:root{--bg:#1f1f1f;--fg:#e8eaed;--mut:#9aa0a6;--line:#3c4043;--blue:#8ab4f8;--soft:#28292c;--r0:#4a2523;--r0f:#f6aea9;--r1:#453a1c;--r1f:#fdd663;--r2:#1e3a29;--r2f:#81c995}}
*{box-sizing:border-box}body{background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;max-width:980px;margin:0 auto;padding:28px 16px 120px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:44px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}h3{font-size:15px;margin:22px 0 8px}
.sub{color:var(--mut);font-size:13px}a{color:var(--blue);text-decoration:none}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:20px 0}.kpi div{background:var(--soft);border-radius:10px;padding:12px 14px}.kpi b{display:block;font-size:22px}.kpi span{font-size:12.5px;color:var(--mut)}
.find li{margin:6px 0}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px;min-width:640px}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:center}th{color:var(--mut);font-weight:500;font-size:12px}
td.t{text-align:left}tr.g td{text-align:left;font-weight:600;background:var(--soft);font-size:12.5px}td.p{color:var(--blue);letter-spacing:1px;white-space:nowrap}
.lv0{background:var(--r0);color:var(--r0f)}.lv1{background:var(--r1);color:var(--r1f)}.lv2{background:var(--r2);color:var(--r2f)}
.card{border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}.card.new{border-style:dashed}
.card header{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:flex-start}.card header small{display:block;color:var(--mut);font-size:12.5px}
.chips{display:flex;gap:4px;flex-wrap:wrap}.chip{font-size:11.5px;border-radius:4px;padding:1px 6px;white-space:nowrap}
.card.conf{border-color:var(--r2f)}td.st{font-size:12px;color:var(--mut);text-align:left;white-space:nowrap}
.qs li.ans .row,.qs li.wait .row{display:flex;gap:8px;align-items:flex-start}.qs li.ans .qt{color:var(--mut)}.qs li .a{margin:4px 0 0 28px;font-size:13.5px;border-radius:6px;padding:5px 9px}.qs li.ans .a{background:var(--r2);color:var(--r2f)}.qs li.wait .a{background:var(--r1);color:var(--r1f)}.qs li .a b{margin-right:6px}
.why{margin:10px 0 6px;font-size:14px;color:var(--mut)}
ol.qs,ul.qs{list-style:none;padding:0;margin:8px 0 0}.qs li{padding:8px 0;border-top:1px dashed var(--line)}.qs label{display:flex;gap:8px;align-items:flex-start;cursor:pointer}
.qs input{margin-top:5px;flex:none}.s{flex:none;width:20px;height:20px;border-radius:4px;font-size:12px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;margin-top:2px;color:#fff}
.sS{background:#5f6368}.sT{background:#9334e6}.sA{background:#1a73e8}.sR{background:#188038}.sI{background:#e37400}
.qs textarea{display:none;width:100%;margin:8px 0 2px 28px;max-width:calc(100% - 28px);min-height:64px;font:14px/1.5 inherit;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
.qs li.open textarea,.qs li.has textarea{display:block}.qs li.done .qt{color:var(--mut);text-decoration:line-through}
.mats{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;font-size:12.5px}.mats i{font-style:normal;color:var(--mut)}.mats span{background:var(--soft);border-radius:12px;padding:2px 10px}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--bg);border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap;font-size:13px}
.bar progress{width:180px}.bar button{border:1px solid var(--blue);background:var(--blue);color:#fff;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:13px}.bar button.ghost{background:transparent;color:var(--blue)}
.note{background:var(--soft);border-radius:10px;padding:12px 16px;font-size:14px;margin:12px 0}
dl.mat{display:grid;grid-template-columns:120px 1fr;gap:6px 14px;font-size:14px}dl.mat dt{font-weight:600}dl.mat dd{margin:0;color:var(--mut)}
@media(max-width:600px){dl.mat{grid-template-columns:1fr}}
@media print{.bar{display:none}.qs textarea{display:block}}
"""

JS = """
const K='career-gap-2026-09';let st={};try{st=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(K,JSON.stringify(st))}catch(e){}};
const items=[...document.querySelectorAll('li[data-key]')];
function paint(){let d=0;items.forEach(li=>{const s=st[li.dataset.key]||{};li.querySelector('input').checked=!!s.done;li.classList.toggle('done',!!s.done);
 li.classList.toggle('has',!!(s.text&&s.text.trim()));if(s.done)d++});document.getElementById('prog').value=d;document.getElementById('cnt').textContent=d+' / '+items.length}
items.forEach(li=>{const k=li.dataset.key,cb=li.querySelector('input'),ta=li.querySelector('textarea');ta.value=(st[k]||{}).text||'';
 cb.addEventListener('change',()=>{st[k]=Object.assign({},st[k],{done:cb.checked});save();paint()});
 li.querySelector('.qt').addEventListener('click',ev=>{ev.preventDefault();li.classList.toggle('open');if(li.classList.contains('open'))ta.focus()});
 ta.addEventListener('input',()=>{st[k]=Object.assign({},st[k],{text:ta.value});save();li.classList.toggle('has',!!ta.value.trim())})});
document.getElementById('prog').max=items.length;paint();
document.getElementById('exp').onclick=()=>{let out='# STAR-I 갭 답변 ('+new Date().toISOString().slice(0,10)+')\\n';let cur='';
 items.forEach(li=>{const s=st[li.dataset.key]||{};if(!(s.text&&s.text.trim()))return;const sec=li.closest('section');const hb=sec&&sec.querySelector('header b');const h=hb?hb.textContent:'새 카드 후보';
  if(h!==cur){out+='\\n## '+h+'\\n';cur=h}out+='- Q: '+li.querySelector('.qt').textContent+'\\n  A: '+s.text.trim().replace(/\\n/g,'\\n     ')+'\\n'});
 navigator.clipboard.writeText(out).then(()=>{const b=document.getElementById('exp');b.textContent='복사됨 — Claude에 붙여넣기';setTimeout(()=>b.textContent='답변 전체 복사',2500)})};
document.getElementById('openall').onclick=()=>items.forEach(li=>li.classList.add('open'));
"""


def rich(t):
    t = e(str(t if t is not None else ''))
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', t)


def read_cards(root):
    out = {}
    for f in sorted(glob.glob(os.path.join(root, 'inventory', 'P*.md'))):
        s = open(f, encoding='utf-8').read()
        m = re.match(r'^---\s*\n(.*?)\n---', s, re.S)
        fm = dict((k, v.strip().strip('"')) for k, v in re.findall(r'^([\w가-힣]+):\s*(.*)$', m.group(1), re.M)) if m else {}
        a = re.search(r'^## A.*?\n(.*?)(?=^## )', s, flags=re.S | re.M)
        out[fm.get('id', os.path.basename(f)[:3])] = {'title': fm.get('title', ''), 'period': fm.get('period', ''),
                                                      'status': fm.get('status', 'draft'), 'alen': len(a.group(1).strip()) if a else 0}
    return out


def build(root):
    d = yaml.safe_load(open(os.path.join(root, 'inventory', 'gap.yaml'), encoding='utf-8'))
    real = read_cards(root)
    groups, cards = d.get('groups') or ['전체'], d.get('cards') or []
    for c in cards:
        r = real.get(str(c['id'])[:3], {})
        c.setdefault('title', r.get('title', '')); c.setdefault('period', r.get('period', ''))
        if r.get('status') == 'confirmed' and not str(c.get('state', '')).startswith('confirmed'):
            c['state'] = ('confirmed · ' + c['state']) if c.get('state') else 'confirmed'
        c.setdefault('priority', 3); c.setdefault('score', [0, 0, 0, 0, 0]); c.setdefault('questions', [])
    qs = [q for c in cards for q in c['questions']]
    n_ans = sum(1 for q in qs if q.get('answer')); n_wait = sum(1 for q in qs if q.get('wait') and not q.get('answer'))
    n_open = len(qs) - n_ans - n_wait
    n_conf = sum(1 for v in real.values() if v['status'] == 'confirmed')
    alens = [v['alen'] for v in real.values()]; avg = round(sum(alens) / len(alens)) if alens else 0

    heat = ''
    for gi, g in enumerate(groups):
        mine = [c for c in cards if c.get('group', 0) == gi]
        if not mine:
            continue
        heat += '<tr class="g"><td colspan="9">%s</td></tr>' % e(g)
        for c in mine:
            cells = ''.join('<td class="lv%d" title="%s %s">%s</td>' % (v, SECNAME[k], LV[v], LV[v]) for k, v in zip(SEC, c['score']))
            heat += '<tr><td><a href="#%s">%s</a></td><td class="t">%s</td>%s<td class="p">%s</td><td class="st">%s</td></tr>' % (
                e(str(c['id'])), e(str(c['id'])), e(c['title']), cells, '★' * (5 - int(c['priority'])), e(c.get('state', '')))

    body = ''
    for gi, g in enumerate(groups):
        mine = sorted([c for c in cards if c.get('group', 0) == gi], key=lambda c: c['priority'])
        if not mine:
            continue
        body += '<h2>%s</h2>' % e(g)
        for c in mine:
            chips = ''.join('<span class="chip lv%d">%s %s</span>' % (v, k, LV[v]) for k, v in zip(SEC, c['score']))
            li = ''
            for i, q in enumerate(c['questions']):
                sec = q.get('sec', 'A'); key = '%s-%d' % (c['id'], i)
                head = '<span class="s s%s">%s</span><span class="qt">%s</span>' % (sec, sec, rich(q['q']))
                if q.get('answer'):
                    li += '<li class="ans"><div class="row">%s</div><div class="a"><b>답함</b> %s</div></li>' % (head, rich(q['answer']))
                elif q.get('wait'):
                    li += '<li class="wait"><div class="row">%s</div><div class="a"><b>자료 대기</b> 파일을 받으면 채운다</div></li>' % head
                else:
                    li += '<li data-key="%s"><label><input type="checkbox">%s</label><textarea placeholder="여기에 기억나는 대로 적기 (문장이 아니어도 됨)"></textarea></li>' % (e(key), head)
            mats = ''.join('<span>%s</span>' % e(m) for m in c.get('materials') or [])
            body += ('<section class="card%s%s" id="%s"><header><div><b>%s</b> %s<small>%s%s</small></div><div class="chips">%s</div></header><p class="why">%s</p><ol class="qs">%s</ol>%s</section>'
                     % (' new' if c.get('new') else '', ' conf' if str(c.get('state', '')).startswith('confirmed') else '', e(str(c['id'])), e(str(c['id'])), e(c['title']),
                        e(c['period']), (' · ' + e(c['state'])) if c.get('state') else '', chips, rich(c.get('why', '')), li,
                        ('<div class="mats"><i>찾아올 자료</i>%s</div>' % mats) if mats else ''))

    def block(title, items, ordered=False):
        if not items:
            return ''
        tag = 'ol' if ordered else 'ul class="find"'
        return '<h2>%s</h2><%s>%s</%s>' % (title, tag, ''.join('<li>%s</li>' % rich(i) for i in items), tag.split()[0])

    newc = ''
    for gname in sorted(set(n.get('group', '새 카드 후보') for n in d.get('new_cards') or []), key=lambda x: [n.get('group', '새 카드 후보') for n in d['new_cards']].index(x)):
        items = [n for n in d['new_cards'] if n.get('group', '새 카드 후보') == gname]
        newc += '<h2>새로 만들 카드 후보 — %s</h2><section><ul class="qs">%s</ul></section>' % (e(gname), ''.join(
            '<li data-key="N-%s-%d"><label><input type="checkbox"><span class="qt"><b>%s</b> — %s</span></label><textarea placeholder="시기 · 과목/사업 · 내가 한 일 · 남은 자료"></textarea></li>'
            % (e(gname), i, rich(n['title']), rich(n.get('desc', ''))) for i, n in enumerate(items)))
    mat = d.get('materials') or []
    math = ('<h2>찾아올 자료</h2><dl class="mat">%s</dl>' % ''.join('<dt>%s</dt><dd>%s</dd>' % (e(m['kind']), rich(m['desc'])) for m in mat)) if mat else ''
    meta = d.get('meta') or {}
    page = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex"><title>STAR-I 갭 분석</title><style>%s</style></head><body>'
            '<h1>경력 원장 STAR-I 갭 분석</h1><div class="sub">비공개 내부 자료 · 카드 %d장 · %s%s · 원천은 inventory/ 카드(md)이고 이 페이지는 채울 것의 목록입니다</div>'
            '<div class="kpi"><div><b>%d / %d</b><span>confirmed 카드</span></div><div><b>%d개</b><span>답한 질문</span></div><div><b>%d개</b><span>자료를 받으면 채울 질문</span></div>'
            '<div><b>%d개</b><span>아직 남은 질문</span></div><div><b>%d자</b><span>카드 \'행동(A)\' 평균 분량</span></div></div>'
            '%s%s<h2>카드 × STAR-I 상태표</h2><div class="sub">★이 많을수록 먼저 채울 카드. 카드 ID를 누르면 질문으로 이동합니다.</div>'
            '<div class="wrap"><table><tr><th>ID</th><th style="text-align:left">카드</th><th>S 상황</th><th>T 과제</th><th>A 행동</th><th>R 성과</th><th>I 증빙</th><th>우선</th><th>상태</th></tr>%s</table></div>'
            '<div class="note"><b>쓰는 법</b> — 남은 질문의 문장을 누르면 메모 칸이 열립니다. 문장으로 다듬지 말고 기억나는 대로 적으세요. 적은 내용은 이 브라우저에 자동 저장됩니다. '
            '아래 막대의 <b>답변 전체 복사</b>를 눌러 Claude에 붙여 넣으면 카드(md)에 반영하고 원장을 다시 만듭니다. 한 번에 2~3장이 적당합니다. 기억이 안 나는 질문은 체크만 하고 넘어가세요.</div>'
            '%s%s%s%s<div class="note"><b>반출 주의</b> — 대외비·내부 검토문서 원문은 이 폴더로 가져오지 않습니다. 문서 <b>제목·일자·분량·내 역할</b>과 본인이 쓴 요약만 적으면 카드에는 충분합니다. '
            '개인정보가 든 파일은 evidence/에만 두고 site/에는 넣지 않습니다.</div>'
            '<div class="bar"><progress id="prog" value="0" max="1"></progress><span id="cnt"></span><button id="exp">답변 전체 복사</button><button id="openall" class="ghost">메모 칸 모두 열기</button></div>'
            '<script>%s</script></body></html>') % (
        CSS, len(real), e(str(meta.get('updated', datetime.date.today().isoformat()))), (' · ' + e(meta['note'])) if meta.get('note') else '',
        n_conf, len(real), n_ans, n_wait, n_open, avg,
        block('달라진 것', d.get('changes')), block('아직 남은 간격', d.get('remaining')), heat,
        block('다음 순서 (제안)', d.get('next'), True), body, newc, math, JS)
    out = os.path.join(root, 'inventory', 'gap_report.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('OK: %s (카드 %d장 중 %d장 진단, 질문 %d = 답함 %d · 자료 대기 %d · 남음 %d)' % (out, len(real), len(cards), len(qs), n_ans, n_wait, n_open))


if __name__ == '__main__':
    try:
        build(sys.argv[1] if len(sys.argv) > 1 else '.')
    except yaml.YAMLError as ex:
        sys.exit('inventory/gap.yaml 형식 오류: %s\n→ 문장이 든 값은 큰따옴표로 감싸고, 한 줄짜리 {key: value} 안의 물음표·쉼표·배지를 확인하세요.' % ex)
