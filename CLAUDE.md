# mars-careers — 화성에서 취직하기

## 하네스: 커리어 (경력 원장 · 자소서 · 공개 CV)

**목표:** 흩어진 경력을 STAR-I 카드로 자산화하고, 그 카드에서 지원처별 자소서·공개 CV·포트폴리오 PDF를 만든다.
카드(사실)가 원천이고 나머지는 전부 카드에서 나오는 생성물이다. 카드에 없는 사실은 어디에도 쓰지 않는다.

**트리거:**
- 경력 정리·자소서·포트폴리오·지원서 관련 요청 → `career-orchestrator` 스킬
- "내가 했던 일 정리하고 싶어", "경력 카드 추가/수정" → `career-inventory` 스킬 (인터뷰로 끌어낸다)
- 공고(직무기술서)+자소서 문항을 함께 주면 → `job-apply` 스킬 (분석 → 장면 찾기·경험 추천 → 사용자 선택 → 작성 → ChatGPT 판과 비교(선택) → 사실 검수와 심사관 검수를 따로 → 소재 정리 한 장 → 보고서 HTML)
- "심사관/면접관 관점으로 봐줘" → `screener-review` 스킬
- "카드에 뭐가 부족해 / 내가 뭘 더 채워야 하지 / 빈칸 점검" → `career-inventory`의 갭 분석 (inventory/gap.yaml → gap_report.html)
- "내가 어떤 사람인지 정리해줘 / 나를 요약해줘 / 어떤 자리에 맞을까" → `self-profile` 스킬 (self-profile.yaml → self-profile.html)
- "CV 페이지 만들어/업데이트" → `cv-site` 스킬, 제출용 A4 PDF → `portfolio-pdf` 스킬
- 단순 질문(예: "STAR가 뭐야")은 직접 응답

## 지켜야 할 것

1. **사실만.** 카드에 없는 경험·숫자·역할을 지어내지 않는다. 모르면 `[인터뷰 필요]`/`[확인 필요]`로 남기고 묻는다.
2. **내 것과 남의 것을 가른다.** 팀·회사의 성과 숫자는 누가 산출했는지, 그중 내 몫이 무엇인지 카드에 적는다.
3. **공개와 비공개를 가른다.** `inventory/`·`profile.md`·`education.md`·`evidence/`·`applications/`는 비공개. 공개되는 것은 `site/`뿐이고,
   `cv.yaml`에 넣는 문구는 cv-site 스킬의 마스킹 규칙을 통과한 것만.
4. **비밀번호·주민번호·계좌는 어디에도 적지 않는다.** 수험번호·접수번호까지만.
5. **타인 실명은 공개 산출물에 쓰지 않는다.** 기관·팀명까지만.
6. **생성물은 직접 고치지 않는다.** `inventory/ledger.html`, `inventory/gap_report.html`, `self-profile.html`, `site/index.html`, `applications/지원현황.html`, 분석보고서 HTML은 원천(md·yaml)을 고치고 다시 만든다.
7. **자소서는 추천 → 선택 → 작성 순서.** 문항별 키워드와 후보 경험을 먼저 보여 주고, 사용자가 고른 조합으로 쓴다. 지원동기는 그 회사의 실제 서비스를 먼저 조사한다.

## 폴더

```
profile.md            기본 프로필·연표 (비공개)
education.md          학력·성적·장학 (비공개, 선택)
inventory/            경력 카드 P01_*.md (원천) + ledger.html · gap.yaml → gap_report.html (생성물)
self-profile.yaml     「사용 설명서」의 원천 → self-profile.html (생성물, 비공개)
cv.yaml               공개 CV의 원천 (마스킹 통과 문구만) → site/index.html
site/                 공개 사이트 (github.io 등에 올리는 유일한 폴더)
applications/         지원처별 폴더 + 지원현황.yaml → 지원현황.html
evidence/             증빙 원본 (비공개, 주민정보가 든 파일이 많다)
_workspace/           인터뷰 원자료·검수 리포트·작업 기록
```

## 새 환경 점검

- **Python 3** + `pip install pyyaml pillow`
- **Chrome 또는 Edge** (PDF 렌더·스크린샷 검증용, `--headless=new`)
- 첫 세션에서 아래 세 줄이 돌아가면 준비 끝:
  `python3 .claude/skills/career-inventory/scripts/build_ledger.py inventory`
  `python3 .claude/skills/cv-site/scripts/build_cv.py .`
  `python3 .claude/skills/job-apply/scripts/build_tracker.py .`
  `python3 .claude/skills/career-inventory/scripts/build_gap_report.py .`
  `python3 .claude/skills/self-profile/scripts/build_profile.py .`

## 예시 데이터

처음 들어 있는 `김화성`은 실존하지 않는 가상 인물이다. 화면이 어떻게 나오는지 본 뒤에는
"예시 데이터 지우고 내 걸로 시작할게"라고 말하면 된다 — profile.md·cv.yaml·inventory/P*.md·inventory/gap.yaml·self-profile.yaml·applications/지원현황.yaml을 비우고 인터뷰를 시작한다.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| (여기에 하네스를 고칠 때마다 한 줄씩 쌓는다) | | | |
