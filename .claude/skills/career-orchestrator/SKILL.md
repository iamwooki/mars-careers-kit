---
name: career-orchestrator
description: >
  커리어 하네스 오케스트레이터. 경력 정리 → 자소서 → 포트폴리오 PDF 전체 워크플로우를 조율한다.
  "자소서 쓰고 싶어", "경력 정리하고 싶어", "포트폴리오 만들어줘", "OO에 지원하려고 해",
  "지원서 준비", "이력서/경력기술서 만들어", "CV/bio 페이지", "웹 이력서",
  "github.io 사이트 만들어/업데이트/배포", 그리고 후속 요청인 "자소서 수정해줘",
  "포트폴리오 다시/재생성/업데이트", "카드 추가하고 자소서에 반영", "이전 결과 개선",
  "다른 곳에 또 지원", "공고 넣을게/직무기술서 첨부/문항은 이거야"(→ job-apply 위임), "심사관/면접관 관점으로 봐줘"(→ screener-review) 요청 시 반드시 이 스킬을 사용할 것.
  단순 맞춤법 교정이나 하네스 자체 수정 요청은 제외.
---

# 커리어 오케스트레이터

경력 인벤토리(재료) → 지원처 분석 → 자소서 + 포트폴리오 PDF(산출물)를 만드는
전체 워크플로우. **실행 모드: 하이브리드** (Phase별 상이, 각 Phase에 명시).

## Phase 0: 컨텍스트 확인 (매 실행 필수)

1. `inventory/`의 카드 수와 status(draft/confirmed) 집계
2. `applications/` 하위 기존 지원처 폴더 확인
3. 실행 모드 결정:
   - 인벤토리 비어있음 → **초기 실행** (Phase 1부터)
   - 카드 있음 + 새 지원처 → **Phase 2부터** (인터뷰는 부족분만)
   - 기존 산출물 부분 수정 요청 → **부분 재실행** (해당 에이전트만, Phase 4의 해당 단계로)
   - 사용자가 새 경력 추가 요청 → Phase 1 인터뷰 후 영향받는 산출물만 갱신
4. 결정된 계획을 사용자에게 한 줄로 알리고 진행한다.

## Phase 1: 경력 인터뷰 — 실행 모드: 메인 세션 직접

서브 에이전트는 사용자와 대화할 수 없으므로 인터뷰는 반드시 메인 세션이 수행한다.

1. career-inventory 스킬을 로드하고 그 인터뷰 진행법을 따른다.
2. 인터뷰 원자료를 `_workspace/raw_interview_{날짜}.md`에 축적한다 (사용자 발화 요지 그대로, 해석 없이).
3. 세션당 카드 2~3장 분량이 한계 — 사용자가 지치면 중단하고 Phase 2로 넘긴다.
   카드 후보 목록이 남아 있으면 "다음에 이어서 할 후보"로 `_workspace/backlog.md`에 기록.

## Phase 2: 구조화 — 실행 모드: 서브 에이전트 (career-analyst)

1. `Agent(subagent_type: general-purpose, model: "opus")`로 career-analyst 정의를 프롬프트에
   포함해 호출한다. 입력: 원자료 경로, 기존 inventory 상태, (있으면) 지원처 공고.
2. 반환된 "추가 인터뷰 필요" 질문이 있으면 메인 세션이 사용자에게 묻고,
   답을 원자료에 추가한 뒤 career-analyst를 재호출한다 (최대 2회 왕복).
3. **사용자 확인 게이트**: draft 카드를 사용자에게 요약 제시하고 confirmed 전환 승인을 받는다.
   이 게이트를 건너뛰고 산출물을 만들지 않는다 — 사실 오류가 자소서까지 전파된다.

## Phase 3: 지원처 분석 — 실행 모드: 서브 에이전트 (career-analyst)

**위임 규칙 (보조 산출물)**: "카드에 뭐가 부족해 / 내가 뭘 더 채워야 하지 / 빈칸 점검"은 `career-inventory`의 갭 분석 페이지(gap.yaml → gap_report.html), "내가 어떤 사람인지 정리해줘 / 나를 요약해줘 / 어떤 자리에 맞을까"는 `self-profile` 스킬(self-profile.yaml → self-profile.html)에, "인간관계도 / 사람 카드 / 이 사람 기록해줘 / OO팀 사람들 정리"는 `people-graph` 스킬(people/people.yaml → people/people.html, 연락처 금지)에 위임한다. 셋 다 비공개 내부 문서다.

**사용자가 공고(직무기술서)와 자소서 문항을 함께 제공하면 Phase 3~4 전체를 `job-apply` 스킬에 위임한다.**
job-apply는 입력 정규화(00_input.md) → 분석(00_target.md) → 재료 확인 게이트 → 장면 재발굴·경험 추천(00_materials.md) → 초안
→ ChatGPT 대조(문항별_비교.html) → 사실 검수 ‖ 심사관 검수(screener-review, 병렬·독립) → 개정판·윤문 → 소재정리(04_소재정리.md)
→ 분석보고서 HTML(build_report.py)까지를 지원서 한 건 단위로 표준화한 파이프라인이다. 총괄과 사용자 승인 게이트는 메인 세션이 맡는다.
아래 Phase 3·4 서술은 포트폴리오를 함께 만들거나 job-apply 범위 밖의 조합이 필요할 때의 기준이다.

지원처가 정해진 경우만. 공고 텍스트/URL을 받아 career-analyst가 `00_target.md`
(요구 역량, 문항, 카드 매핑)를 작성한다. 지원처 미정이면 건너뛰고 마스터판(`_master`)으로 진행.

## Phase 4: 산출물 생성 — 실행 모드: 에이전트 팀 (생성-검증 패턴)

1. `TeamCreate`로 팀 구성: resume-writer, portfolio-designer, quality-reviewer (+리더=메인)
2. `TaskCreate`:
   - T1 자소서 초안 (resume-writer) — 자소서 요청 시
   - T2 포트폴리오 HTML+PDF (portfolio-designer) — 포트폴리오 요청 시 (T1과 병렬)
   - T2b 공개용 CV 웹페이지 site/index.html (portfolio-designer, cv-site 스킬) — CV/bio/github.io 요청 시.
     마스킹 확인 목록과 git push는 리더가 사용자 승인 후 처리 (푸시 = 공개 발행)
   - T3 자소서 검수 (quality-reviewer, T1 의존)
   - T4 포트폴리오 검수 (quality-reviewer, T2 의존)
   - T5 수정 반영 (각 작성자, T3/T4 의존 — 리더가 대조해 만든 반영 목록으로)
3. 검수→수정은 최대 2라운드. 검수자는 리더에게만 보고하고 작성자와 직접 주고받지 않는다. 미해결 쟁점은 리더가 수합해 사용자 판단으로 넘긴다.
   자소서 검수는 사실 검수(T3)와 **심사관 검수(screener-review)** 를 **동시에, 서로 모르게** 돌린다 — 사실이 맞아도 떨어지는 이유를 따로 잡기 위해. 리더가 두 리포트를 대조한다(job-apply Phase 5와 같은 방식).
4. 팀 정리 후 리더가 최종본을 확정: `02_resume_final.md`, `portfolio.pdf`
5. 자소서만 또는 포트폴리오만 요청이면 해당 작성자 + 검수자 2인 팀으로 축소.
   **단일 산출물 + 수정 1건 같은 경량 작업이면 팀 없이 서브 에이전트 1회 호출로 대체** (팀 오버헤드 회피).

## 데이터 전달 프로토콜

- **파일 기반(주)**: 모든 산출물은 약속된 경로로. 중간 산출물은 `_workspace/`
  (`{phase}_{agent}_{artifact}.md` 컨벤션), 검수 리포트는 `_workspace/review_*.md`
- **태스크 기반**: Phase 4 팀의 진행 관리 (TaskCreate 의존 관계)
- **메시지 기반**: 검수 지적 전달, 숫자 불일치 조율 (resume-writer ↔ portfolio-designer ↔ quality-reviewer)
- 디렉토리 구조:
  ```
  career/
  ├── profile.md              # 기본 프로필 (이름·연락처·경력 연표)
  ├── inventory/              # L1 themes / L2 카드 / L3 achievements
  ├── applications/{지원처}/   # 00_target → 01_draft → 02_final + portfolio.pdf
  ├── site/                   # 공개용 CV 웹페이지 (github.io 리포로 푸시)
  └── _workspace/             # 인터뷰 원자료, 검수 리포트 (보존)
  ```

## 에러 핸들링

| 상황 | 대응 |
|------|------|
| 에이전트 실패 | 1회 재시도 → 재실패 시 해당 산출물 없이 진행, 사용자에게 누락 보고 |
| 카드-산출물 사실 충돌 | 카드(원천) 기준 통일. 카드 자체가 틀렸다면 사용자에게 확인 |
| PDF 렌더 실패 | portfolio-designer가 1회 재시도 → HTML만 전달 + 사유 보고 |
| draft 카드로만 산출 가능 | 진행하되 최종 보고에 "확인 필요 카드" 명시 |
| 검수 2라운드 후 미합의 | 쟁점 양쪽 안을 사용자에게 제시, 사용자 선택 반영 |

## 완료 보고 형식

1. 산출물 경로 목록 2. 사용한 카드 / 제외한 카드와 사유
3. 확인 필요 항목(draft 카드, 미합의 쟁점) 4. 다음 개선 제안 1~2개 (인터뷰 백로그 등)

## 테스트 시나리오

**정상 흐름**: 카드 6장 confirmed 상태에서 "OO공단에 지원하려는데 자소서랑 포트폴리오 만들어줘"
→ Phase 0(카드 있음, 새 지원처) → Phase 3(공고 분석) → Phase 4(3인 팀, T1~T5)
→ `applications/OO공단/`에 02_final + portfolio.pdf → 완료 보고.

**에러 흐름**: Phase 4에서 resume-writer가 3번 문항 소재 부족 보고
→ 리더가 사용자에게 3번 문항 관련 추가 인터뷰 1건 진행 → career-analyst로 카드 1장 추가
→ 사용자 confirmed → resume-writer 재호출(3번 문항만) → 검수 → 완료.
포트폴리오는 이 왕복과 무관하게 병렬로 완료되어 있어야 한다.
