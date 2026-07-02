# 세모이 (세벌식 모아치기 e) 데이터 — 출처·라이선스·면책 고지 (NOTICE)

이 디렉터리(`addons/semoe/`)의 데이터는 아래 원저작물에서 취득·변환한 **2차적 저작물
(Adapted Material)** 입니다.

## 원저작물 (Attribution)

- **이름**: 세모이 (세벌식 모아치기 e) keyboard
- **제작**: 신세기 (Sinseiki)
- **소개 / 출처 표시**: **ssgi.kr**
- **저장소**: https://github.com/Sinseiki/Semo-e_keyboard
- **설명 문서**:
  - 자판 설명: https://blog.naver.com/eekdland/220526834927
  - 결합(모아치기) 규칙: https://blog.naver.com/eekdland/220239514856

원저작자 요청(원본 README §참고사항): *"다른 곳에 소개하실 때 ssgi.kr 를 함께
표시해주시면 감사드리겠습니다."* → 본 고지로 충족합니다.

## 라이선스 (License)

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

- 전문(영문 정본): https://creativecommons.org/licenses/by-sa/4.0/legalcode
- 전문(한국어): https://creativecommons.org/licenses/by-sa/4.0/legalcode.ko
- 요약: https://creativecommons.org/licenses/by-sa/4.0/deed.ko
- 원본 LICENSE 전문은 원 저장소 `LICENSE` 파일에 포함되어 있습니다.

### CC BY-SA 4.0 의무사항

- **저작자 표시(BY)**: 위 출처·제작자(신세기 / ssgi.kr) 표시를 유지할 것.
- **동일조건변경허락(SA)**: 이 데이터를 포함·변형하여 배포하는 경우 **CC BY-SA 4.0
  (또는 호환 라이선스)** 으로 배포해야 함.
- **변형 표시(3.b)**: 원본을 변형하였음을 명시할 것(아래 "변형 내용" 참조).

> ⚠️ **본체 병합 금지.** 본 데이터는 NabiCloud 본체(GPL 등)와 라이선스가 다르므로
> 본체 소스 트리에 **직접 병합하지 말고** 이 애드온 디렉터리(`addons/semoe/`)로
> 분리 유지할 것. 커밋 위치(별도 애드온 vs `addons/` NOTICE)는 메인 검토 사항.

## 변형 내용 (Modifications) — CC BY-SA §3(b)

원본은 **날개셋 입력기 IME 의 자판 설정 XML** 형식입니다. 본 데이터는 NabiCloud 에서
쓰기 위해 다음과 같이 추출·변환한 것이며, 원본을 변형하였습니다.

| 우리 산출물 | 원본 요소 | 변환 내용 |
| --- | --- | --- |
| `data/dictionary/80-abbrev-semoe.txt` | `<UserCandiTable>` | 음절열→단어 약어, `key:value` 평면화(394행) |
| `data/semoe_2stage_candidates.tsv` | `<UserCandiTable>` | 2단계 후보(순서 보존, key→후보목록) |
| `data/semoe_word_abbr.dic` | `<UserCandiTable>` | 위 동일 소스(staging 원본) |
| `data/semoe_chord_abbr.dic` | `<HanSubstTable>` | chord 자모열→단어 약어(1372행, 옛한글/PUA 보존) |
| `data/semoe_chord_abbr_raw.tsv` | `<HanSubstTable>` | 무손실 코드포인트 원본 |
| `data/semoe_jamo_mix.xml` | `<UnitMixTable>` | 자모 조합 규칙(437) |
| `data/semoe_unitmix_combine.tsv` | `<UnitMixTable>` | 약어 key-fold용 UnitMix overlay(311행, 방향성 보존) |
| `archive/semoe-chord.xml` | `<KeyTable>` | 기본 레이어만 best-effort 변환(부분) — ★2026-06-19 강등·2026-06-26 `archive/` 이동(셸 미로드·미배포; `archive/README.md`) |

미변환(불가) 요소: `<Automata>`·`<UserCompoTable>`·`<KeyProgram>`·조건식 키맵 등
(날개셋 chord 엔진/상태머신 의존). 상세는 `../../docs/SEMOE_DATA_ACQUISITION.md` 참조.

## 날개셋 IME 저작권

날개셋 입력기 프로그램 자체의 저작권은 제작자 **김용묵** 님께 있습니다
(http://moogi.new21.org). 본 데이터에는 날개셋 IME 프로그램 코드가 **포함되어 있지
않으며**, 자판 정의 데이터(설정 XML)만을 변환한 것입니다.

## 세모이(모아치기) 구현 근거 (Implementation Basis)

**세모이(모아치기) 구현 근거.** 세모이 저장소의 자판 데이터(특히 `jamo_mix.xml`)와
날개셋이 제공하는 `한글자모참고표.txt`(낱자↔코드 정본)를 바탕으로 단위코드 legend를
확정해 구현하였습니다. 날개셋 입력기 본체 코드는 포함하지 않으며, 공개된 자판 정의
데이터와 자모 참고표만 사용했습니다. 본 구현은 본가 동작과의 일치를 보증하지 않는
**베스트 에포트 유사 동작**입니다.

## 동작 면책 (Disclaimer of Warranties)

원본은 CC BY-SA 4.0 §5 에 따라 **"있는 그대로(AS-IS) / 가용한 대로(AS-AVAILABLE)"**
제공되며, 원저작자 및 NabiCloud 는 본 변환 데이터의 정확성·적합성·**동작을
보증하지 않습니다(동작 미보증, best-effort)**.

세모이는 날개셋 IME 의 모아치기(chord) 입력 엔진 — KeyDown/KeyUp 버퍼 + 강제종료
타이머(기본 40ms) + 자모 재정렬 상태머신(Automata) — 을 전제로 설계되었습니다.
NabiCloud 에 동등한 chord 엔진이 구현되기 전에는 본 데이터(특히 약어·자판)가 **동일하게
동작한다는 보장이 없습니다.** 변환 한계는 `../../docs/SEMOE_DATA_ACQUISITION.md` 를 보십시오.
