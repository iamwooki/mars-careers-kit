# 공고 레이더 (jobs/)

잡코리아·인크루트·잡알리오(공공기관) 검색을 매일 한 번 긁어 **내 기준(config.json)** 으로 거르고 점수를 매겨 `public/jobs/`에 정적 대시보드로 보여 준다. LLM 없이 규칙만 쓴다.

```
python3 jobs/crawl.py            # jobs/config.json → jobs/data/jobs.json (30일 누적)
python3 jobs/build_page.py       # → public/jobs/index.html + data.json
```

- `config.json`: 검색어, 내 경력 연수(이보다 하한이 높은 공고 제외), 제외어, 제목·회사·지역 가점. 예시는 `config.example.json`.
- 점수는 규칙일 뿐 적합 판정이 아니다. 진짜 판정은 공고 원문을 하네스(job-apply)에 넣어서 한다.
- 자동화: `.github/workflows/jobs.yml` — 매일 07:30 KST에 GitHub Actions가 수집·커밋하고, `VERCEL_TOKEN`·`VERCEL_ORG_ID`·`VERCEL_PROJECT_ID` 시크릿이 있으면 Vercel에 배포한다.
- 개인 용도로 하루 1회, 요청 간격 1.5초. 포털 약관상 상업적 재배포 금지.

## 나만 보기 (Vercel)
`public/middleware.js`가 `/jobs/*`에 HTTP Basic 인증을 건다. 계정은 Vercel 환경변수 `JOBS_USER`·`JOBS_PASS`(Production)에만 있고 코드·저장소에는 없다.
```
cd public && printf 'ID' | vercel env add JOBS_USER production && printf 'PW' | vercel env add JOBS_PASS production
```
랜딩·데모에는 레이더가 노출되지 않는다 — 주소(`/jobs/`)를 직접 쳐서 들어간다.
