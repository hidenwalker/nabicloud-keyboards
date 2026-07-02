# 세모이 공식 규격·약어 원본 자료 — 출처·라이선스 고지 (NOTICE-reference)

이 디렉터리(`addons/semoe/reference/`)에는 세모이(세벌식 모아치기 e) 자판의 **공식
규격 문서와 약어 부록 원본**을 변형 없이 그대로 보존합니다. 재배포는 원본 라이선스
(CC BY-SA 4.0)가 허용합니다.

## 보존 파일 (Preserved Files)

| 파일 | 설명 | 형식 |
| --- | --- | --- |
| `세벌식 모아치기 e 규격.pdf` | 세모이 자판 공식 규격 문서(배열도·단일글쇠·결합규칙·추가기능·부록 Automata·옛한글 결합) | PDF (10p) |
| `세모이 자판 약어 (가나다순).xlsx` | 공식 약어 부록 — 가나다순 정렬 (2018-11-14) | XLSX |
| `세모이 자판 약어 (빈도순).xlsx` | 공식 약어 부록 — 빈도순 정렬 (2018-11-14) | XLSX |

우리 표현으로 정리한 규격 본문은 `../../docs/SEMOE_SPEC.md` 에 있습니다(이 원본을
근거로 전사). 원본의 정확한 수치·표는 위 파일이 정본입니다.

## 원저작물 (Attribution)

- **이름**: 세모이 (세벌식 모아치기 e) keyboard
- **제작**: 신세기 (Sinseiki)
- **소개 / 출처 표시**: **ssgi.kr**
- **저장소**: https://github.com/Sinseiki/Semo-e_keyboard  (버전 v260615)
- **설명 문서(블로그)**:
  - 자판 설명: https://blog.naver.com/eekdland/220526834927
  - 결합(모아치기) 규칙: https://blog.naver.com/eekdland/220239514856
  - 한 번에 모아치기 구현: http://pat.im/1109 (팥알 님)

원저작자 요청(원본 README §참고사항): *"다른 곳에 소개하실 때 ssgi.kr 를 함께
표시해주시면 감사드리겠습니다."* → 본 고지로 충족합니다.

## 라이선스 (License)

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

- 전문(영문 정본): https://creativecommons.org/licenses/by-sa/4.0/legalcode
- 전문(한국어): https://creativecommons.org/licenses/by-sa/4.0/legalcode.ko
- 요약: https://creativecommons.org/licenses/by-sa/4.0/deed.ko

### 재배포 근거 및 의무사항

- **재배포 허용**: CC BY-SA 4.0 은 자료의 복제·재배포를 허용합니다. 본 디렉터리의
  PDF·XLSX 는 **변형 없이 원본 그대로** 보존되므로 그대로 재배포할 수 있습니다.
- **저작자 표시(BY)**: 위 출처·제작자(신세기 / ssgi.kr) 표시를 유지할 것.
- **동일조건변경허락(SA)**: 이 자료를 변형하여 배포하는 경우 **CC BY-SA 4.0**
  (또는 호환 라이선스)으로 배포해야 함.

## 날개셋 IME 저작권

세모이 약어 XLSX 의 "조합키" 열은 날개셋 입력기에서의 입력 방법을 표기한 것입니다.
날개셋 입력기 프로그램 자체의 저작권은 제작자 **김용묵** 님께 있습니다
(http://moogi.new21.org). 본 자료에는 날개셋 IME 프로그램 코드가 포함되어 있지
않으며, 공개된 규격 문서와 약어 데이터(문서·표)만을 보존한 것입니다.

## 약어 부록 형식 메모 (참고)

- 두 XLSX 는 정렬 순서만 다른 **동일 항목 집합**(번호 매겨진 약어 1365개)을 담습니다.
- 열 구성: `번호 / 표시되는 글자 / 품사·어미 / 조합키(초성) / 조합키(중성) / 조합키(종성)`.
  시트 안에 여러 표(일반 약어 + 종결어미 약어 / 용언 위주 추가 약어)가 좌우로 배치됩니다.
- 비고: `v` 는 공백(space)을 의미. 통계상 빈도 순서는 정확하지 않을 수 있음(원본 주석).

## ★조합키 컬럼 = 약어 .dic 입력 정본 (2026-06-19)

`(가나다순).xlsx` 의 **조합키(초성/중성/종성) 컬럼**은 사용자가 실제로 치는 base 자모(호환자모 표기,
합용은 "ㄱ+ㅈ", `v`=공백)를 적은 **공개 legend**이며(SEMOE_CHORD_UNITCODE §1-B), 세모이 약어 자동치환
사전 `../data/semoe_chord_abbr.dic` 의 **입력 정본**으로 삼는다. 재도출 도구 = `../tools/gen_chord_abbr_from_xlsx.py`
(런타임 동일 fold: UnitMix 합용표 우선 → 표준 결합표 fallback → canonical 키). 역추론 시그니처 파일
`../data/semoe_chord_abbr_raw.tsv` 는 **교차검증용 reference 로 강등**(정본 아님, 폐기 아님). 원본 xlsx 는
변형 없이 그대로 보존(CC BY-SA 4.0).
