# 세모이 (세벌식 모아치기 e) 애드온

나비구름(NabiCloud)의 **외부 XML 자판 애드온**입니다. 세모이는 신세기(Sinseiki) 님이
설계한 세벌식 모아치기 자판군이며, 이 디렉터리는 그 자판 데이터를 CC BY-SA 4.0
2차 저작물로 담습니다. 출처·라이선스·면책은 [NOTICE-semoe.md](NOTICE-semoe.md),
표기 규약은 [NAMING.md](NAMING.md)를 따릅니다.

이 애드온은 **자판 데이터만** 설치하며 나비구름 본체가 먼저 설치돼 있어야 합니다.
엔진 코어는 무수정이고, 본 자판들은 로더(`keyboard-loader.c`)가 외부 XML로 읽어
`type="jaso-sebeol"`(엔진 enum **1005**) 경로로 동작합니다.

## 1. 모아치기 ↔ 이어치기 — config `[semoe] moachigi`

세모이는 **모아치기**(동시타·재정렬)와 **이어치기**(순차 입력)를 가집니다. 두 모드는
별도 자판 파일이 아니라 **하나의 자판 + 설정 스위치**로 다룹니다.

- 출하 기준 모아치기를 켜는 자판은 `3moa-semoe-2018.xml` **1종뿐**입니다
  (이 파일만 `<flags loose-order="true">`). 나머지 4종은 `loose-order="false"`라
  이어치기로 동작합니다.
- 셸 설정 `config.ini` 의 `[semoe] moachigi`(기본 1=인정) 가 loose-order 선언 자판의
  모아치기 동작을 켜고 끕니다. loose-order 미선언 자판은 이 설정과 무관하게
  이어치기 baseline 입니다(불변식: DECISIONS §23).
- (참고) 과거 동봉되던 이어치기 전용 변형은 2018 과 `loose-order` 플래그만 다른
  중복본이라 출하에서 제거됐습니다. 이어치기는 위 설정으로 이미 커버됩니다.

## 2. 약어 입력 — config + `.dic` (별도 애드온 분리)

세모이의 약어(준말) 입력은 **config 게이트 + 약어 사전(`.dic`)** 조합으로 동작하며,
데이터 출처·분량 때문에 **별도 애드온으로 분리**합니다. 사전 원본은
`data/semoe_chord_abbr.dic`(+ `*_raw.tsv`/`*_pua.tsv`/`*_holdback.tsv` 생성 자료)이고,
재생성 도구는 `tools/regen_chord_abbr_dic.py`·`tools/gen_chord_abbr_from_xlsx.py`
입니다. 약어 사전은 CC BY-SA 출처(`reference/세모이 자판 약어 *.xlsx`)에서 파생하므로
ShareAlike 의무가 따릅니다.

## 3. 자판 5종 (이어치기 중복본 제거 후)

본가 스냅샷(`v260615`)에서 옮긴 코호트는 연도별 5종입니다:

| id | 표시명 | 비고 |
|---|---|---|
| `3moa-semoe-2014` | 세벌식 세모이 2014 | pre-e 세대 |
| `3moa-semoe-2015` | 세벌식 세모이 2015 | e 로 수렴 중 |
| `3moa-semoe-2016` | 세벌식 세모이 2016 | 확장 기호열(symbol-func=semoe) |
| `3moa-semoe-2017` | 세벌식 세모이 2017 | 확장 기호열 + ㅇ 첫소리 |
| `3moa-semoe-2018` | 세벌식 세모이 2018 모아치기 (v260615) | loose-order=true(모아치기 켜짐) |

`type=jaso-sebeol`(1005) 단일 경로이며, 모아치기 합성기(`semoe-chord`, enum 1006)는
출하 자판에 바인딩되지 않은 별도 트랙입니다(DECISIONS §22~24). 표시명은
[keyboard-names.append.txt](keyboard-names.append.txt) 가 본체 `keyboards/keyboard-names.txt`
뒤에 append 하는 방식으로만 덧붙습니다(자판 XML `<name>`·id 불변).

## 4. 설치 / 시드 경로

- **자판 XML**: 인스톨러가 `addons/semoe/keyboards/*.xml`(글롭)을
  `<본체>\addons\semoe\keyboards\` 로 복사 → 로더가 스캔해 '외부(xml)' 목록에 노출.
- **표시명**: `keyboard-names.append.txt` 를 본체 `keyboards\keyboard-names.txt` 뒤에
  마커 블록으로 append(중복 가드).
- **모아치기 시드**: 애드온 인스톨러가 라이선스 동의 후 모아치기 on/off 선택값을
  `<본체>\addons\semoe\moachigi.seed`("0"/"1")에 기록. 런타임에 `config.ini` 의
  `[semoe] moachigi` 키가 없을 때만 이 seed 로 비파괴 append(per-user 보존).
- **인스톨러**: `windows/installer/NabiCloud-semoe-addon.nsi`(makensis). 글롭 설치라
  자판 수가 바뀌어도 스크립트 수정 없이 따라갑니다.

## 5. 검증

- 외부 XML 로드: `shared/engine/tests/semoe_xml_verify.c` → `SEMOE_XML_ALL_PASS`(5/5).
- 3beol 대조: `shared/engine/tests/diff_semoe.c` → mismatch 0(5종).
