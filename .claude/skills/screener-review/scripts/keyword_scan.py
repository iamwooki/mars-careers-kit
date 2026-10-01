#!/usr/bin/env python3
"""자소서 문항별 직무 어휘 vs 내부(비직무) 어휘 빈도.
사용: python keyword_scan.py 자소서.md [--job "사업비,원가,..."] [--noise "위원회,법령,..."] [--preset pmo]
--job/--noise 미지정 시 preset 사용 (기본 pmo). 공고 수행직무 명사를 --job에 넣는 것이 정확하다."""
import re, sys
PRESETS = {
 'pmo': (['사업비','원가','산정','기능점수','투입공수','공수','일정','수행사','검수','산출물','요구사항','제안요청서','RFP','과업','예산','계약','리스크','품질','진척','성과지표','타당성','중복','연계','통합','WBS','감리','PMO','사업관리','사업계획'],
         ['위원회','법령','보도자료','협의회','동향','안건','정책','TF','분과','국정','부처']),
 'dev': (['구현','배포','테스트','API','장애','코드','리팩토링','CI','데이터베이스','DB','쿼리','SQL','스키마','Git','커밋','빌드','롤백','예외','로그','프레임워크','함수','클래스','알고리즘','자료구조','트랜잭션','인덱스'],  # '설계·운영·성능·모니터링'은 기획 문서에도 흔해 제외
         ['기획','정책','보고서','회의','협의','행사','홍보','안건']),
 'plan': (['기획','요구사항','사용자','지표','전환율','로드맵','우선순위','A/B','리서치','런칭','KPI','백로그','스펙'],
          ['정책','법령','위원회','연구','논문','행사']),
}
def main():
    a = sys.argv[1:]; path = a[0]
    preset = a[a.index('--preset')+1] if '--preset' in a else 'pmo'
    job, noise = PRESETS[preset]
    if '--job' in a: job = [x.strip() for x in a[a.index('--job')+1].split(',') if x.strip()]
    if '--noise' in a: noise = [x.strip() for x in a[a.index('--noise')+1].split(',') if x.strip()]
    md = re.sub(r'<!--.*?-->', '', open(path, encoding='utf-8').read(), flags=re.S)
    secs = re.findall(r'^## (\d+)[.．][^\n]*\n(.*?)(?=^## |\Z)', md, flags=re.S|re.M)
    def cnt(body, terms): return {t: len(re.findall(re.escape(t), body)) for t in terms if re.search(re.escape(t), body)}
    tj = tn = 0
    print(f"{'문항':<5}{'직무어휘':>8}{'내부어휘':>8}  상위 직무어휘 / 상위 내부어휘")
    for n, b in secs:
        j = cnt(b, job); nz = cnt(b, noise); sj, sn = sum(j.values()), sum(nz.values()); tj += sj; tn += sn
        top = lambda d: ', '.join(f"{k}×{v}" for k, v in sorted(d.items(), key=lambda x: -x[1])[:6]) or '—'
        print(f"{n:<5}{sj:>8}{sn:>8}  {top(j)} / {top(nz)}")
    ratio = tj / (tj + tn) if tj + tn else 0
    print(f"합계  직무 {tj} · 내부 {tn} · 직무 비율 {ratio:.0%}  → {'직무 사람으로 읽힘' if ratio >= 0.6 else '경계' if ratio >= 0.4 else '다른 직군으로 분류될 위험'}")
if __name__ == '__main__': main()
