# 두겹이·두줄이 약어 데이터 (best-effort)

출처: ssgi.kr / github.com/Sinseiki (두겹이·두줄이) · CC BY-SA 4.0
라이선스·면책·변형고지는 상위 [`../NOTICE-dubeol.md`](../NOTICE-dubeol.md) 참조. 본체 트리 직접 병합 금지(별도 애드온 유지).

원본은 본가 "**부가기능 포함**" 날개셋 IME 설정 XML(`두벌식 겹받침 e (두겹이) (부가기능 포함).xml` 등)의
`<UserCompoTable>` 상태머신이며, 아래 `.dic` 는 거기서 전사·변환한 산출물이다. 설계 = [`../../../docs/DUBEOL_ABBREV_DESIGN.md`](../../../docs/DUBEOL_ABBREV_DESIGN.md).

## 본가 약어 메커니즘 (전사 대상)

본가 약어는 **두 개의 기호(Shift+빈글쇠로 입력되는 □ … ↔ · 등)를 연속 입력 → 단어** 인 상태머신이다:

- `state=0` + `key=<기호>` + `newstate=S` + `interim=<기호>` : 첫 기호 입력 → 상태 S 전이(기호를 preedit 표시)
- `state=S` + `key=<기호2>` + `result=<단어>` : 둘째 기호 입력 → 단어 확정·commit

이 표는 **완전 대칭**이다(기호A→기호B = 기호B→기호A = 같은 단어). 즉 약어는 **순서무관 기호쌍 → 단어**
사상이며, 자판당 정확히 **70개**(빈도순)다. 기호는 표준 두벌식 Shift 층에서 "된소리/이중모음이 없는 빈 자리"
(자음 ㅁㄹㄴㅎㅋ… · 모음 ㅗㅜㅡㅕ… 의 Shift 위치, 두줄이는 추가로 `;`키)에만 의도적으로 배치된다 →
약어 트리거 글쇠 집합은 **된소리(ㄸㄲㅃㅉ)·이중모음(ㅒㅖ)·단키겹받침(fill-jong) 글쇠와 서로소(disjoint)** 다
(생성기가 assert 로 검증).

## 산출 파일

| 파일 | 원본 요소 | 형식 | 항목 수 | 비고 |
| --- | --- | --- | --- | --- |
| `dugyeobe_abbrev.dic` | 두겹이 `<UserCompoTable>`(141 entry → 70 쌍) | UTF-8 `key:value` | 70행(+헤더) | 순서무관 글쇠쌍→단어. 빈도순. 기호 15종 |
| `dujul-e_abbrev.dic` | 두줄이 `<UserCompoTable>`(140 entry → 70 쌍) | UTF-8 `key:value` | 70행(+헤더) | 동일. 기호 15종(`;`키=`:` 포함). 두겹이와 글쇠↔기호 배정 다름 |

두 자판의 **단어 집합은 동일**(70개)하나, 자판마다 기호→글쇠 배정이 달라 글쇠쌍 매핑이 다르다.

## `.dic` 키 형식 — base 글쇠쌍 (★`:` 충돌 회피)

```
<글쇠1><글쇠2>:<단어>
```

- **글쇠 = 물리 base 글쇠**(소문자 a–z · 두줄이는 `;` 포함), 코드포인트 오름차순 정렬(순서무관 쌍의 정규형).
  실제 입력은 **Shift와 함께**(예 `df` = Shift+D 후 Shift+F). 셸이 키이벤트 VK 에서 직접 계산.
  ★기호(□ … 등)가 아니라 base 글쇠로 키잉한 이유: 두줄이 `:` 기호가 `key:value` 구분자 `:` 와 충돌하기 때문.
- **단어 = 본가 `result` 그대로** — 끝공백 보존("으로 "·"입니다. "·"사람"). xlsx 범례의 `v` = 공백.
- 파일 순서 = 빈도 순위. `#` 주석 무시. 헤더에 기호 레이어(base 글쇠→preedit 기호) 기재.

## 교차검증 (정본 일치)

생성기가 **본가 `<UserCompoTable>`(정본) ↔ 빈도순 xlsx '조합키' 컬럼**(사람이 읽는 문서)을 자모쌍 단위로
교차대조해 **70/70 일치**를 assert 한다(불일치 시 생성 중단). 추가로 대칭성·충돌·글쇠쌍 유일성·트리거∩된소리
서로소를 검증한다. 셀프테스트(메커니즘) = `selftest_jaso_filljong.c`(엔진) 와 별개로, 약어 값은 이 교차검증이 게이트.

## 재생성

```
python ../tools/gen_dubeol_abbrev.py            # 본가 XML → .dic 재생성 + 검증 보고
python ../tools/gen_dubeol_abbrev.py --verify   # 재생성 없이 파싱·대칭·충돌·xlsx 교차검증만
```

직접 편집 금지 — 본가 XML(`references/{dugyeob-e,dujul-e}/부가기능 포함/`) 수정 후 재생성한다.
표준 라이브러리만 사용(zipfile + re), openpyxl 불요.

## 배포

런타임 소비(약어 트리거)는 [`DUBEOL_ABBREV_DESIGN.md`](../../../docs/DUBEOL_ABBREV_DESIGN.md) 참조 —
`<DLL>\addons\dubeol\data\*.dic` 로 설치, 셸이 활성 자판(dubeol-chord)·opt-in 설정일 때만 로드(골든 봉인).
