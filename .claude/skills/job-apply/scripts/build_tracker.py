#!/usr/bin/env python3
"""지원 현황 뷰어 생성: applications/지원현황.yaml → applications/지원현황.html

사용: python .claude/skills/job-apply/scripts/build_tracker.py [프로젝트 루트]
yaml이 원천이고 html은 생성물이다(직접 수정 금지). 비공개 — site/ 반입 금지.
"""
import sys
import html
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

TONE = {
    "준비중": "gray", "제출": "blue", "미지원": "gray", "포기": "gray",
    "서류합격": "green", "필기합격": "green", "면접합격": "green", "최종합격": "green",
    "서류탈락": "red", "필기탈락": "red", "면접탈락": "red", "최종탈락": "red",
}
RESULT_TONE = {"합격": "green", "탈락": "red", "대기": "blue"}

CSS = """
:root{--bg:#fff;--fg:#202124;--mut:#5f6368;--line:#e0e0e0;--blue:#1a73e8;--green:#188038;--red:#c5221f;--gray:#5f6368;--chip:#f1f3f4}
@media (prefers-color-scheme:dark){:root{--bg:#1f1f1f;--fg:#e8eaed;--mut:#9aa0a6;--line:#3c4043;--blue:#8ab4f8;--green:#81c995;--red:#f28b82;--gray:#9aa0a6;--chip:#303134}}
body{background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;max-width:920px;margin:32px auto;padding:0 16px}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--mut);font-size:13px;margin-bottom:20px}
.sum{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}.sum span{background:var(--chip);border-radius:16px;padding:3px 12px;font-size:13px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:500;font-size:12px}.wrap{overflow-x:auto}
.b{display:inline-block;border:1px solid currentColor;border-radius:4px;padding:0 7px;font-size:12px;white-space:nowrap}
.blue{color:var(--blue)}.green{color:var(--green)}.red{color:var(--red)}.gray{color:var(--gray)}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
details{border:1px solid var(--line);border-radius:8px;margin:12px 0;padding:0 14px}summary{cursor:pointer;padding:12px 0;font-weight:600}
summary .b{margin-left:8px;font-weight:400}h3{font-size:13px;color:var(--mut);margin:16px 0 4px;font-weight:500}
ul{margin:4px 0 12px;padding-left:20px}dl{display:grid;grid-template-columns:110px 1fr;gap:2px 12px;margin:4px 0 12px}dt{color:var(--mut);font-size:13px}dd{margin:0}
.st{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 12px}.st div{border:1px solid var(--line);border-radius:6px;padding:4px 10px;font-size:13px}
.st small{display:block;color:var(--mut)}
"""


def e(v):
    return html.escape(str(v if v is not None else ""))


def badge(text, tone):
    return f'<span class="b {tone}">{e(text)}</span>'


def link(rel):
    return quote(str(rel))


def next_stage(app):
    for s in app.get("stages", []):
        if s.get("result") in ("대기", "-"):
            d = s.get("date") or ""
            return f'{s["name"]}{" · " + d if d else ""}'
    return ""


def render(apps):
    apps = sorted(apps, key=lambda a: str(a.get("submitted") or "0"), reverse=True)
    counts = {}
    for a in apps:
        counts[a["status"]] = counts.get(a["status"], 0) + 1
    out = [f"<!doctype html><html lang=ko><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<meta name=robots content=noindex><title>지원 현황</title><style>{CSS}</style>",
           "<h1>지원 현황</h1>",
           f'<div class=sub>비공개 내부 자료 · 원천 applications/지원현황.yaml · 생성 {date.today().isoformat()}</div>',
           '<div class=sum>' + f"<span>전체 {len(apps)}</span>" +
           "".join(f"<span>{e(k)} {v}</span>" for k, v in counts.items()) + "</div>",
           "<div class=wrap><table><tr><th>제출일<th>기관<th>직무<th>상태<th>다음 단계<th>수험번호</tr>"]
    for a in apps:
        out.append(f"<tr><td>{e(a.get('submitted') or '—')}<td><a href='#{e(a['id'])}'>{e(a['org'])}</a>"
                   f"<td>{e(a['role'])}<td>{badge(a['status'], TONE.get(a['status'], 'gray'))}"
                   f"<td>{e(next_stage(a))}<td>{e(a.get('exam_no') or '—')}</tr>")
    out.append("</table></div>")
    for a in apps:
        out.append(f"<details id='{e(a['id'])}' open><summary>{e(a['org'])} · {e(a['role'])}"
                   f"{badge(a['status'], TONE.get(a['status'], 'gray'))}</summary><dl>")
        rows = [("공고", e(a.get("posting"))), ("전형 구분", e(a.get("track"))),
                ("제출일", e(a.get("submitted") or "—")), ("수험번호", e(a.get("exam_no") or "—")),
                ("조회", f"<a href='{e(a.get('portal'))}'>{e(a.get('portal'))}</a>" if a.get("portal") else ""),
                ("로그인", e(a.get("login_note"))),
                ("작업 폴더", f"<a href='{link(a['folder'])}/'>{e(a['folder'])}/</a>" if a.get("folder") else ""),
                ("제출본", f"<a href='{link(a['submitted_copy'])}'>{e(Path(a['submitted_copy']).name)}</a>" if a.get("submitted_copy") else ""),
                ("자소서 판", e(a.get("essay_version")))]
        out += [f"<dt>{k}<dd>{v}" for k, v in rows if v]
        out.append("</dl>")
        if a.get("stages"):
            out.append("<h3>전형 단계</h3><div class=st>")
            for s in a["stages"]:
                r = s.get("result", "-")
                out.append(f"<div>{e(s['name'])} {badge(r, RESULT_TONE.get(r, 'gray')) if r != '-' else ''}"
                           f"<small>{e(s.get('date') or '일정 미정')}{' · ' + e(s['note']) if s.get('note') else ''}</small></div>")
            out.append("</div>")
        for title, key in (("진행 기록", "timeline"), ("지원서에 적어 낸 값", "submitted_facts"), ("면접 대비", "interview_prep")):
            items = a.get(key) or []
            if items:
                out.append(f"<h3>{title}</h3><ul>")
                for it in items:
                    out.append(f"<li>{e(it['date'])} — {e(it['event'])}" if isinstance(it, dict) else f"<li>{e(it)}")
                out.append("</ul>")
        if a.get("lessons"):
            out.append(f"<h3>회고</h3><p>{e(a['lessons'])}</p>")
        out.append("</details>")
    return "\n".join(out)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    src = root / "applications" / "지원현황.yaml"
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    apps = data["applications"]
    for a in apps:
        if a["status"] not in TONE:
            sys.exit(f"알 수 없는 status: {a['status']} ({a['id']})")
    dst = root / "applications" / "지원현황.html"
    dst.write_text(render(apps), encoding="utf-8")
    print(f"{dst} — {len(apps)}건")


if __name__ == "__main__":
    main()
