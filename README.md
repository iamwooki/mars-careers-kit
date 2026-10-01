# 화성에서 취직하기 (mars-careers)

흩어진 경력을 한 번 제대로 정리해 두고, 거기서 자소서·공개 CV·지원 기록을 뽑아 쓰는 틀이에요.
Claude Code가 인터뷰어, 작가, 검수자 역할을 나눠 맡아요. 내 컴퓨터에서만 돌아가요.

## 준비물

- [Claude Code](https://claude.com/claude-code)
- Python 3.10 이상, `pip install pyyaml pillow`
- Chrome 또는 Edge (PDF로 저장할 때)

## 5분 안에 돌려 보기

```bash
unzip mars-careers.zip && cd mars-careers
python3 .claude/skills/career-inventory/scripts/build_ledger.py inventory   # 경력 원장 뷰어
python3 .claude/skills/cv-site/scripts/build_cv.py .                        # 공개 CV
python3 .claude/skills/job-apply/scripts/build_tracker.py .                 # 지원 현황
python3 .claude/skills/career-inventory/scripts/build_gap_report.py .       # 갭 분석 (뭘 더 채워야 하나)
python3 .claude/skills/self-profile/scripts/build_profile.py .              # 사용 설명서 (나는 어떤 사람인가)
open inventory/ledger.html inventory/gap_report.html self-profile.html site/index.html applications/지원현황.html
```

가상 인물 `김화성`의 데이터가 들어 있어서 화면이 어떻게 나오는지 먼저 볼 수 있어요.

## 내 걸로 시작하기

```bash
claude
```

그리고 이렇게 말해요.

```
예시 데이터 지우고 내 걸로 시작할게. 경력 정리부터 하고 싶어
```

Claude가 연도별로 가볍게 훑은 다음, 프로젝트 하나씩 S(상황)·T(과제)·A(행동)·R(성과)·I(증빙)를 물어봐요.
빈 양식을 채우게 하지 않아요. 기억나는 대로 말하면 카드로 정리해 주고, 모르는 건 "패스"라고 하면 표시만 남겨요.

## 자주 쓰는 말

| 하고 싶은 일 | 이렇게 말해요 |
|---|---|
| 경력 정리 | `2021년에 했던 정산 프로젝트 카드로 만들어줘` |
| 자료로 정리 | `이 폴더에 넣은 보고서 읽고 카드 초안 만들어줘. 모르는 것만 물어봐` |
| 빈칸 점검 | `카드 전체를 STAR-I 관점에서 점검하고 내가 뭘 더 채워야 하는지 정리해줘` → 갭 분석 페이지. 메모 칸에 적고 "답변 전체 복사"로 Claude에 돌려줘요 |
| 지원서 | `이 공고에 지원하려고 해. 문항은 이거야 (공고·문항 붙여넣기)` |
| 냉정한 검수 | `떨어뜨리는 사람 입장에서 이 자소서 봐줘` / `면접관이라면 뭘 물을까` |
| 공개 CV | `CV 페이지 업데이트해줘` → 확인 후 `github.io에 올려줘` |
| 제출 기록 | `○○에 제출했어. 제출 화면 PDF 넣어놨어` → 원장 대조 + 지원 현황 갱신 |
| 결과 | `○○ 서류 합격했어` |
| 나를 요약 | `지금까지 카드로 내가 어떤 사람인지 정리해줘` → 사용 설명서(패턴·맡을 수 있는 일·맞는 자리·숫자의 주인·약점) |

## 원칙 (이 틀이 지키는 것)

- **사실만 써요.** 카드에 없는 경험이나 숫자는 자소서에도 CV에도 나오지 않아요.
- **내 숫자와 남의 숫자를 갈라요.** "110억 절감"이 회사 숫자인지 내 숫자인지 카드에 적어 두고, 면접에서 무너지지 않게 해요.
- **자소서는 추천 → 선택 → 작성.** 문항마다 쓸 만한 경험과 키워드를 먼저 보여 주고, 내가 고른 조합으로 써요.
- **두 번 검수해요.** 사실 검수(거짓·과장·글자수)와 심사관 검수(진실이어도 떨어지는 이유)를 따로 해요.
- **공개와 비공개를 갈라요.** 밖으로 나가는 건 `site/` 하나뿐이에요.

## 꼭 읽어 주세요

- 내 데이터를 넣는 순간 이 폴더는 **이력·성적·연락처·지원 기록이 모인 개인정보 묶음**이 돼요.
  공개 저장소에 통째로 올리지 마세요. GitHub에 둘 거면 private으로, 공개하는 건 `site/`만요.
- 비밀번호·주민번호는 어디에도 적지 마세요. 지원 현황에는 수험번호까지만 적어요.
- 회사의 대외비 문서 원문은 넣지 마세요. 제목·일자·분량·내 역할과 내가 쓴 요약이면 충분해요.
- AI가 쓴 문장은 티가 나요. 마지막에는 꼭 내 말로 고쳐 쓰세요. 직접 쓴 글을 `applications/_reference/`에 넣어 두면 그 문체에 맞춰 줘요.
- 합격을 보장하지 않아요. 이 틀이 해 주는 건 "사실을 빠짐없이, 어긋남 없이" 까지예요.

## 들어 있는 것

```
.claude/agents/     career-analyst · resume-writer · quality-reviewer · portfolio-designer
.claude/skills/     career-orchestrator · career-inventory · job-apply · resume-writing
                    screener-review · self-profile · cv-site · portfolio-pdf
profile.md · self-profile.yaml · education.md · cv.yaml · inventory/ · applications/ · evidence/ · site/
```

예시 인물 `김화성`과 회사·학교 이름은 전부 지어낸 거예요.
