# 세모이 데이터 변환본 (best-effort)

출처: ssgi.kr / https://github.com/Sinseiki/Semo-e_keyboard · CC BY-SA 4.0
라이선스·면책·변형고지는 상위 `../NOTICE` 참조. 본체 트리 직접 병합 금지(별도 애드온 유지).

원본은 날개셋 IME 설정 XML(`세모이 (한 번에 모아치기).xml` 등)이며, 아래 표는
거기서 추출·변환한 산출물이다.

## 산출 파일

| 파일 | 원본 요소 | 형식 | 항목 수 | 비고 |
| --- | --- | --- | --- | --- |
| `semoe_word_abbr.dic` | `UserCandiTable` (370 key) | UTF-8 `key:value` | 394행 | 2단계 사용자정의 후보. 음절열→단어. 한 key가 여러 후보면 여러 줄. 가장 실용적·바로 사용 가능 |
| `semoe_chord_abbr.dic` | 약어표 xlsx 조합키(정본) | UTF-8 `key:value` | 1349행(+헤더) | chord 자모열→단어 약어. ★정본 입력 = `../reference/세모이 자판 약어 (가나다순).xlsx` 조합키 컬럼(사용자가 치는 base 자모). 재도출 = `../tools/gen_chord_abbr_from_xlsx.py`(런타임 동일 fold). distinct 단어 1349/1354=99.6% |
| `semoe_chord_abbr_raw.tsv` | `HanSubstTable`(역추론) | UTF-8 `U+xxxx+...\t단어` | 1372행 | 합성-후 시그니처 역추론본. **정본에서 강등 → 교차검증용 reference**(2026-06-19, xlsx 조합키 정본화). 폐기 아님 |
| `semoe_chord_abbr_holdback.tsv` | xlsx 자판미도달 | UTF-8 | 5건 | 슬롯-역할 불일치(ㅗ(왼쪽)·중성슬롯 자음·종성슬롯 모음)로 보류. 추측 매핑 금지 |
| `semoe_chord_abbr_pua.tsv` | (해소) | UTF-8 | 0건 | 과거 PUA 격리. xlsx base 입력 정본화로 자연 회복되어 빈 격리 |
| `semoe_jamo_mix.xml` | `UnitMixTable` (437) | XML | CHO 161 / JUNG 133 / JONG 143 | chord 내 같은 자리 두 자모 단위의 합성 규칙. 단위코드(`G_`,`GG` 등)는 날개셋 내부표기 보존 |

## 변환 한계 (메인 검토 필요 / best-effort)

1. **chord 입력 엔진 미포함.** 세모이는 날개셋의 KeyDown/KeyUp chord 버퍼 +
   강제종료 타이머(기본 40ms) + 자모 재정렬 알고리즘을 전제한다. `semoe_chord_abbr`의
   key는 그 엔진을 거친 "결과 자모집합"이라, 엔진 없이는 약어 트리거를 재현할 수 없다.
   NabiCloud에 모아치기(chord) 엔진이 갖춰져야 실사용 가능.
2. **KeyTable/Automata/UserCompo 미변환.** 키맵 값이 날개셋 조건식
   (`T==101 ? 0x2160 : ...`, 상태머신 `Automata state=...`)으로 되어 있어 우리 형식으로
   기계 변환 불가. 키 배열·기호확장·상태전이는 미반영(원본 XML/배열도 PNG 참조).
3. **종성 옛한글/PUA 슬롯.** 약어 1171건이 종성에 U+11C3↑·U+A96x·U+D7xx·PUA(U+F8xx)를
   약어 인코딩 슬롯으로 사용. 호환자모로 환원 불가하여 코드포인트로 보존. 의미상
   "단어 약어"이지 음절이 아님.
4. **단어 약어 권장 경로.** 즉시 활용 가능한 것은 `semoe_word_abbr.dic`(음절열→단어)뿐이며,
   `semoe_chord_abbr`는 chord 엔진 구현 시 매핑 테이블로 사용.

## 미취득 / 추가 검토 자료 (원 저장소 내)
- `세모이 자판 약어 (가나다순).xlsx` / `(빈도순).xlsx`: HanSubst와 동일 정본(1363 일반약어 +
  15 종결어미). 사람이 읽는 표 형태(표시글자/품사/조합키). 필요 시 별도 추출 가능.
- `*.pdf`(모아치기 설명·약자 안내·이용안내), 배열도 PNG, 스티커, 직결식/옛한글/모바일/두벌식혼용
  변형 자판 XML, `DirectGothic-Semoe.ttf`(폰트 — 별도 폰트 라이선스 `폰트 라이선스.txt`).
