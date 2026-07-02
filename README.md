# NabiCloud Keyboards (나비구름 추가 자판)

나비구름(NabiCloud) 한글 IME 의 **추가 자판 데이터 애드온** 저장소입니다.
실행 코드가 없는 **데이터 전용**(자판 XML·약어 사전·고지문) 저장소이며, 나비구름 본체가
런타임에 `<DLL>\keyboards\` / `<DLL>\addons\<family>\...` 에서 스캔·로드합니다.

> 이 저장소는 나비구름 모노레포의 `addons/` 를 fresh snapshot 으로 발행한 것입니다.
> 배포(설치)는 통합 다중선택 인스톨러 **NabiCloud-Addon**(본체 저장소에서 빌드)이 담당합니다.

## 구성·라이선스 (디렉터리별 SPDX)

> 이 저장소의 **모든 자판 데이터는 CC BY-SA 4.0** 으로 배포합니다.
> 318na·4z = 나비구름이 공개 배열 사실에서 **독립 구현**한 저작물을 CC BY-SA 4.0 으로 공개(설계자 출처표시) ·
> 세모이·두겹이/두줄이 = 신세기(Sinseiki) 님 CC BY-SA 4.0 원저작 기반 2차 저작물.

| 디렉터리 | 자판 | 라이선스 | 출처표시 |
|---|---|---|---|
| [`318na/`](318na/) | 세벌식 3-18Na | **CC BY-SA 4.0** (데이터 © 나비구름) | 배열 *설계* = navilera/NavilIME '318Na' 출처표시 — 코드·표현 비복제(독립 구현). 고지 [`318na/NOTICE-318na.md`](318na/NOTICE-318na.md) · 재유도 절차 [`318na/PROVENANCE-318na.md`](318na/PROVENANCE-318na.md) |
| [`4z/`](4z/) | 4z (가변종성·레지스터 머신 세벌식) | **CC BY-SA 4.0** (데이터 © 나비구름) | 배열 *설계* = 명랑소녀 (2026) 출처표시 — 날개셋 `.ist` 표현 비복제(독립 구현). 고지 [`4z/NOTICE-4z.md`](4z/NOTICE-4z.md) |
| [`semoe/`](semoe/) | 세모이 (세벌식 모아치기 e) 2014~2018 + 약어·UnitMix 데이터 | **CC-BY-SA-4.0** | 신세기 (Sinseiki) / ssgi.kr — 원저작물 2차적 저작물(Adapted Material). 고지 [`semoe/NOTICE-semoe.md`](semoe/NOTICE-semoe.md) |
| [`dubeol/`](dubeol/) | 두겹이·두줄이 (두벌식 모아치기) + 약어 사전 | **CC-BY-SA-4.0** | 신세기 (Sinseiki) / ssgi.kr — 동작 명세 기반 독립 재구성(AHK 비차용). 고지 [`dubeol/NOTICE-dubeol.md`](dubeol/NOTICE-dubeol.md) |

- **자판 배열**(키→자모 기능적 매핑) 자체는 저작권 대상이 아니며, 설계 고안자를 출처표시합니다.
- **약어 사전 등 실 데이터 저작물**은 원저작(본가) 라이선스를 따릅니다 — 세모이·두벌 약어 사전 =
  신세기 님 본가 데이터의 전사·정규화(CC BY-SA 4.0, 각 NOTICE 에 변형 내용 명시).
- CC BY-SA 4.0 전문: <https://creativecommons.org/licenses/by-sa/4.0/legalcode>
  (한국어 <https://creativecommons.org/licenses/by-sa/4.0/legalcode.ko>).
- ※ 세벌식 확장(신세벌식·3-89·순아래 1990·안마태(3beol)·3-2015 계열, LGPL-2.1 데이터)은 이 저장소가
  아니라 **나비구름 본체 설치본**에 포함됩니다.

## upstream 서브모듈

- `references/semoe-keyboard` → [Sinseiki/Semo-e_keyboard](https://github.com/Sinseiki/Semo-e_keyboard)
  @ v260615 (`4e7b88c`) — 세모이 본가 원본(대조·재생성용, 빌드 불요).

## 관련 저장소

- 본체(나비구름 IME, proprietary): private
- 조합 엔진(libhangul-nabicloud, LGPL-2.1): <https://github.com/hidenwalker/nabicloud-engine>
- 배포(인스톨러 다운로드): <https://github.com/hidenwalker/nabicloud-releases>
