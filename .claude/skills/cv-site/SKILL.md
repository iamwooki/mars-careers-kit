---
name: cv-site
description: >
  공개용 CV/bio 웹페이지 생성·배포 스킬. 내부 원장(inventory)에서 공개 가능한 내용만 선별해
  github.io용 반응형 단일 페이지(site/index.html)를 만든다.
  "CV 페이지", "bio 페이지", "웹 이력서", "github.io에 올려", "프로필 사이트/홈페이지 만들어",
  "사이트 업데이트/배포", "온라인 포트폴리오" 요청 시 반드시 이 스킬을 사용할 것.
  제출용 A4 PDF는 portfolio-pdf, 내부 경력 정리는 career-inventory가 담당한다.
---

# CV/Bio 웹페이지 (github.io)

## 내부 원장과의 관계

`inventory/`는 **비공개 원장**이다 — 모든 사실·숫자·증빙을 담는다.
이 스킬의 산출물은 **공개 쇼윈도**다 — 원장에서 공개 가능한 것만 꺼내 보여준다.
방향은 항상 원장 → 사이트 단방향. 사이트를 고치고 싶으면 원장을 고치고 재빌드한다
(사이트에서 직접 고치면 원장과 어긋나 다음 빌드에서 되돌아간다).

## 공개용 마스킹 규칙 (빌드 전 필수 점검)

인터넷에 영구 공개되는 페이지다. 다음을 기계적으로 적용한다:

1. **연락처**: 전화번호 금지. 이메일은 공개용 계정만. 링크는 GitHub·LinkedIn·블로그 정도.
2. **내부 정보**: 소속 기관의 내부 시스템명·부서 구조·미공개 사업명은 일반화한다
   (예: "OO시스템 개선" → "내부 행정시스템 개선").
3. **숫자**: 예산액·인원 등 조직 내부 규모가 드러나는 수치는 비율·배수로 변환하거나 제외
   ("연 96시간 절감"은 무방, "부서 예산 3.2억 중…"은 제외).
4. **인물**: 상사·동료 실명 금지. 외부 인사(해외 기관 담당자 등)도 본인 외 타인 실명은 쓰지 않는다 — 기관·팀명까지만.
5. 판단이 애매한 항목은 빼는 쪽을 기본값으로 하고, 목록으로 만들어 사용자에게 확인받는다.

## 페이지 구조 (assets/cv-template.html)

**디자인 방향**: 학계 개인 CV 스타일 — 흰 배경, 단일 컬럼,
장식 없는 미니멀. 색은 링크 파랑 하나만, 카드·배지·그라데이션 금지. 섹션은 얇은 회색
구분선의 헤딩, 경력·학력은 왼쪽 날짜 컬럼 + 오른쪽 내용의 목록형.

**타이포·여백 리디자인**: 위 미니멀 방향은 유지하되 위계와 여백을 키웠다 — 본문 폭 900px(상하 64/72px), 이름 2.25rem(-0.8px)·영문 1.15rem, 섹션 제목 1.35rem, 섹션 간격 54px·항목 간격 20px, 사진 136px, 날짜 컬럼 140px(간격 22px). Projects는 접힘 상태에서 1행 '이름 + 기간(오른쪽)', 2행 '역할 · 핵심 성과'(cv.yaml `role:` + `gist:`)로 보이고 항목 사이는 가는 구분선. 모바일은 이름 → 기간 → 역할·성과 세 줄.

**문구·구분자 규칙**: 본문에 대시(—)를 쓰지 않는다 — 대시가 반복되면 "AI가 생성한 글"처럼 읽힌다. 템플릿의 구분(프로젝트 요약·포상 설명·자격 발급처)은 간격+회색 글자로 하고,
cv.yaml 문구의 부가설명은 마침표·쉼표·괄호로 끊는다. 표기는 한 가지로 통일한다
(같은 대상은 페이지 전체에서 한 가지 이름으로만 부른다. 구 안의 가운뎃점은 붙여 쓴다).
AI 문체 점검용 스킬을 따로 갖고 있으면 마지막에 한 번 돌린다(없어도 된다).

단일 페이지, 위에서 아래로:

| 섹션 | 내용 | 원천 |
|------|------|------|
| Profile | 원형 사진(없으면 이니셜), 이름(한/영), 직함, 소속, 링크 | profile.md |
| About | 3~4문장 소개 — 정체성 + 무엇을 왜 하는 사람인지 | profile.md + themes.md |
| Experience | 날짜 컬럼형 경력 목록 (기관명은 공개 수준으로) | profile.md |
| Projects | 대표 4~7개: 접힘 = 제목+기간 / 역할 · 핵심 성과 한 줄, 펼침 = 문제+행동 1~2문장·성과 목록·링크 | inventory confirmed 카드 |
| Skills | 분류별 불릿 목록 (태그 배지 아님) | profile.md |
| Education & Certifications | 날짜 컬럼형 목록 | profile.md |
| Outside Work (선택) | 업무 밖 활동 — 사이드 프로젝트·취미·SNS 링크. 이름(링크) + 한 줄 소개. 맨 아래 배치 | cv.yaml `outside_work` |
| Footer | Last updated + 공개 연락 수단 | - |

템플릿은 반응형(모바일 대응)·다크모드 대응이며 외부 의존성이 없다(폰트·JS CDN 불필요).
CSS 구조는 유지하고 내용만 치환한다.

## 빌드 절차 (내부 관리시스템)

**`site/index.html`은 생성물이다 — 직접 수정 금지.** 데이터 흐름:

```
inventory/ 카드 (원천 사실)
  → cv.yaml (공개 큐레이션: 마스킹 통과 문구 + card: 참조)
  → scripts/build_cv.py
  → site/index.html (생성물)
```

1. **내용 변경**: `{프로젝트}/cv.yaml` 수정. 각 프로젝트·포상 항목의 `card:` 필드로
   원천 카드를 참조한다 — 카드에 없는 사실을 cv.yaml에 쓰지 않는다.
   이미지(사진·로고 등)는 `site/assets/`에 두고 cv.yaml에는 `assets/파일명`으로 참조한다.
   로고 규격: 256×256 RGBA(투명 배경, 내용은 가운데 정렬·여백 약 4%), 화면에서는 20px로 렌더되므로 가는 선·작은 글자는 피한다. 스크린샷에서 만들 때는 가장자리 배경만 투명 처리(flood fill)해 내부 흰색은 보존한다
   (site/ 루트에는 index.html만 둔다).
2. **마스킹 심사**: cv.yaml에 넣는 문구는 아래 마스킹 규칙 통과분만. 애매하면 사용자 확인.
3. **빌드**:
   ```powershell
   python "{이 스킬 경로}\scripts\build_cv.py" "{프로젝트 루트}"
   ```
4. **디자인 변경**: build_cv.py의 TEMPLATE(CSS 포함)에서 수정 후 재빌드.
   `assets/cv-template.html`은 디자인 레퍼런스로 유지.
5. **검증**: Edge headless 스크린샷으로 데스크톱(1200px)·모바일(500px) 렌더 확인
   ```powershell
   & msedge --headless=new --screenshot="chk.png" --window-size=1200,2200 "file:///...site/index.html"
   ```

Projects 섹션은 펼쳐보기(`<details>`) — 접힘 시 제목+기간+성과 한 줄(gist), 인쇄 시
`beforeprint` 스크립트가 자동 전체 펼침.

## 링크 미리보기 명함 (og:image)

카카오톡·슬랙 등에 주소를 붙이면 뜨는 썸네일은 `site/assets/og-card.png`(1200x630)다 — CV 상단 프로필
블록(사진·이름·직함·소속·주소)을 명함처럼 보여준다. og 태그가 없으면 메신저가
프로필 사진을 임의로 잘라 쓴다.

- cv.yaml `meta.url` + `meta.og_image`가 있으면 build_cv.py가 og/twitter 메타 태그를 출력한다.
- 이미지 생성: `python scripts/build_og.py {프로젝트 루트}` — **프로필(이름·직함·소속·사진)이 바뀔 때만** 재실행.
- og:image URL에는 `?v={meta.updated}`가 붙는다. 메신저는 썸네일을 오래 캐시하므로, 카카오톡은
  https://developers.kakao.com/tool/debugger/sharing 에서 캐시 초기화가 필요할 수 있다.

## 방문 통계 (선택)

github.io에는 방문 통계가 없다. 내부 확인용으로 세고 싶으면 무료·무쿠키 도구인 GoatCounter를 쓴다.
사용자가 goatcounter.com에서 직접 가입해 코드(예: `myname`)를 만들고 알려 주면 `cv.yaml`의 `meta.goatcounter: myname`에 적고 재빌드한다
— build_cv.py가 `</body>` 앞에 집계 스크립트 한 줄을 넣는다. 화면에는 아무것도 표시되지 않고, 숫자는 `https://{코드}.goatcounter.com`에 로그인한 본인만 본다.
계정 생성은 사용자가 직접 한다(Claude가 대신 만들지 않는다). 키가 없으면 스크립트는 들어가지 않는다.

## 외부 링크 아카이브 (site/archive/)

외부 사이트(기관 누리집 등)는 사라질 수 있으므로, CV에서 거는 중요한 외부 자료는 `site/archive/`에 보존하고
`(보도자료, 사본)` 쌍으로 링크한다.

- **보도자료** = 원래의 원본 페이지 URL (외부 링크 그대로). 원본 문서 파일(PDF)은 `archive/{게시일}_{종류}_{슬러그}.pdf`로 보존하고 사본 페이지의 첨부파일로 연결한다
- **사본** = 원문 웹페이지를 재구성한 정적 HTML → 같은 이름의 `.html`. 상단에 아카이브 고지
  (원문 URL·게시일·수집일·출처/저작권)를 두고, 본문은 원문 그대로, `noindex` + `canonical`은 원문 URL.
- 공개된 공식 자료만 대상. 내부 문서·미공개 자료는 아카이브하지 않는다.
- `site/archive/`는 build_cv.py가 건드리지 않는 정적 파일이다 (index.html만 생성물).
- 프로젝트 `links:` 항목에 `archive: archive/{파일}.html`을 주면 '원문 ↗ · 사본'으로 병기된다 (2026-10-12, P18 기획보고서 3건에 첫 적용).
- **원본 페이지 보존본**(선택, 2026-10-12 사용자 요청): 원문이 삭제된 경우 정리본 사본과 별도로 `archive/{이름}_original/index.html` + `assets/`에 당시 HTML·CSS·이미지·스크립트를 그대로 저장한다(웹 아카이브 `id_` 원본에서 수집, 상대 경로로 재작성, 상단에 보존 고지 배너·noindex·canonical만 주입). 정리본 사본의 고지문에서 링크한다. 동적 기능(검색·버튼)은 동작하지 않는다고 고지. 수집 절차는 _workspace/2026-10-12_원본보존본/ 스크립트 참조

## github.io 배포

전제: GitHub 계정. 리포지토리 `{username}.github.io` (사이트 주소가 https://{username}.github.io 가 된다).

```powershell
# 최초 1회 — site/를 리포로 초기화
cd site
git init -b main
git remote add origin https://github.com/{username}/{username}.github.io.git
git add . ; git commit -m "publish CV" ; git push -u origin main
# 이후 업데이트는 add/commit/push만
```

gh CLI가 있으면 `gh repo create {username}.github.io --public --source . --push`로 한 번에 가능.
푸시 후 반영까지 1~2분. **푸시 = 공개 발행이므로 반드시 사용자에게 최종 확인을 받고 푸시한다.**

## 업데이트 흐름

원장(카드·프로필)이 갱신되면 → 마스킹 심사(신규 항목만) → 재빌드 → 스크린샷 검증 →
사용자 확인 → 푸시. Footer의 Last updated를 갱신한다.

## 저장소 README의 News (site/README.md)

GitHub 저장소 첫 화면용 소식란. 학계 CV News 스타일(최신순, `**[YYYY.MM]** 이모지 한 문장` 해요체). CV 페이지 자체(index.html)에는 News를 두지 않는다.
**사이트 개설(2026.07) 이후 새로 추가된 것만** 적는다(사용자 결정 2026-10-26, 이전 경력 이정표는 넣지 않음).
공개 CV에 새 항목(서비스·자격·수상·발표 등)을 올려 푸시할 때 README News에도 한 줄을 맨 위에 추가한다. 날짜는 사건의 실제 월(인증일·공개월)을 쓴다.
