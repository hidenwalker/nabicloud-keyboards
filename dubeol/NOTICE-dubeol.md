# 두겹이·두줄이 (두벌식 애드온) 데이터 — 출처·라이선스·면책 고지 (NOTICE)

이 디렉터리(`addons/dubeol/`)의 자판 데이터는 아래 원저작물의 **동작 명세에 기반해
재구성한 2차적 저작물(Adapted Material)** 입니다.

## 원저작물 (Attribution)

- **두겹이 (Dugyeob-e)** — 두벌식 겹받침 모아치기 자판. 저장소: https://github.com/Sinseiki/Dugyeob-e_keyboard
- **두줄이 (Dujul-e)** — 두벌식 줄맞춤(효율 개선 배열) 자판. 저장소: https://github.com/Sinseiki/Dujul-e_keyboard
- **제작**: 신세기 (Sinseiki) · **소개 / 출처 표시**: **ssgi.kr**
- 관련(두벌식 모아치기 일반): https://github.com/Sinseiki/Dubeolsik_Moachigi

원저작자 요청(세모이 등 동일 계열 README §참고사항): *"다른 곳에 소개하실 때 ssgi.kr 를
함께 표시해주시면 감사드리겠습니다."* → 본 고지로 충족합니다.

## 라이선스 (License)

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

- 전문(영문 정본): https://creativecommons.org/licenses/by-sa/4.0/legalcode
- 전문(한국어): https://creativecommons.org/licenses/by-sa/4.0/legalcode.ko
- 요약: https://creativecommons.org/licenses/by-sa/4.0/deed.ko

### CC BY-SA 4.0 의무사항

- **저작자 표시(BY)**: 위 출처·제작자(신세기 / ssgi.kr) 표시를 유지할 것.
- **동일조건변경허락(SA)**: 이 데이터를 포함·변형하여 배포하는 경우 **CC BY-SA 4.0
  (또는 호환 라이선스)** 으로 배포해야 함.
- **변형 표시(3.b)**: 원본을 변형하였음을 명시할 것(아래 "변형 내용" 참조).

> ⚠️ **본체 병합 금지.** 본 데이터는 NabiCloud 본체(비공개 독점 셸)와 라이선스가 다르므로
> 본체 소스 트리에 **직접 병합하지 말고** 이 애드온 디렉터리(`addons/dubeol/`)로 분리
> 유지할 것. 배포 자리(`keyboards\dugyeobe.xml`)는 단일 XML 편의상 본체 keyboards\ 에
> 직접 스테이징하나, 라이선스 귀속·NOTICE 는 이 `addons/dubeol/` 가 정본이다.

## 변형 내용 (Modifications) — CC BY-SA §3(b)

원본 두겹이는 **AutoHotkey 스크립트 + 날개셋 입력기 자판 설정** 형식의 두벌식 모아치기
구현입니다. 본 데이터는 NabiCloud 에서 쓰기 위해 다음과 같이 재구성한 것이며, 원본을
변형하였습니다.

| 우리 산출물 | 원본 요소 | 변환 내용 |
| --- | --- | --- |
| `keyboards/dugyeobe.xml` | 두겹이 두벌식 베이스 배열 + 모아치기 명세 | 표준 두벌식(KS X 5002) 키맵 + `<flags loose-order="true"/>` + `type="dubeol-chord"`(enum 1007) + 표준 결합표 인라인으로 재구성 |
| `keyboards/dujul-e.xml` | 두줄이 "줄맞춤" 배열(표준 두벌식과 14글쇠 공유) + 단키 겹받침 명세 | 본가 KeyTable 의 줄맞춤 키맵을 NabiCloud V2 확장 XML(`<jaso engine="v2" role-flip="dubeol">` + `<jaso-map>`/`<combine>`) 로 + `type="dubeol-chord"`(1007) + `<key-context when="fill-jong">`(I=ㅄ/J=ㄶ/K=ㄺ/L=ㄲ, 두겹이와 다름) + 표준 결합표 인라인. 생성기 `_gen_dujul_xml.c`(DUBEOL_STD struct-copy + 줄맞춤 키맵). 엔진 무변경(데이터만). |
| `data/dugyeobe_abbrev.dic`<br>`data/dujul-e_abbrev.dic` | 본가 "부가기능 포함" XML 의 `<UserCompoTable>`(약어 상태머신, 자판당 70개) | 두 기호(Shift+빈글쇠) 연속입력→단어 상태머신을 **순서무관 글쇠쌍→단어** `key:value` `.dic` 로 전사·정규화. 본가 `<UserCompoTable>`↔빈도순 xlsx 조합키 교차검증(70/70). 생성기 `tools/gen_dubeol_abbrev.py`. 셸 코드(`AbbrevDict`)는 무변경 재사용, 데이터·기호레이어만 자판별. |

키맵 베이스는 **표준 두벌식(KS X 5002, 공개 표준)** 이며, 두겹이 고유 기여는 그 위의
**모아치기(동시치기) 동작 명세**(모음 앵커 V-start·겹받침/연음 분할)입니다. 본 구현은
그 동작 명세만 **독립 재구현**(`shared/engine/nabicloud/engine/engine-chord-dubeol.c`,
LGPL 엔진)했으며 **원본 AHK 코드·날개셋 IME 코드는 차용하지 않았습니다**.

## 날개셋 IME 저작권

날개셋 입력기 프로그램 자체의 저작권은 제작자 **김용묵** 님께 있습니다
(http://moogi.new21.org). 본 데이터에는 날개셋 IME 프로그램 코드가 **포함되어 있지
않으며**, 자판 정의 데이터·동작 명세만을 재구성한 것입니다.

## 동작 면책 (Disclaimer of Warranties)

원본은 CC BY-SA 4.0 §5 에 따라 **"있는 그대로(AS-IS) / 가용한 대로(AS-AVAILABLE)"**
제공되며, 원저작자 및 NabiCloud 는 본 재구성 데이터의 정확성·적합성·**동작을
보증하지 않습니다(동작 미보증, best-effort)**.

두겹이는 본가에서 AHK + 날개셋 chord 엔진(시간창 동시타 버퍼 + 자모 재정렬)을 전제로
설계되었습니다. NabiCloud 는 자체 통합 chord 추상화(셸 동시타 수집 + V-start 분류·
표준 오토마타 합성)로 그 동작을 **유사 재현**하며, 본가와의 1:1 일치를 보증하지
않습니다. 설계·한계는 `../../docs/DUBEOL_CHORD_DESIGN.md` 를 보십시오.
