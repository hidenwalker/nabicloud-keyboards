# 세벌식 3-18Na (318Na) 자판 데이터 — 출처·라이선스 고지 (NOTICE)

이 디렉터리(`addons/318na/`)의 자판 데이터(`keyboards/318na.xml`)와 엔진 측 종성-순환
전처리는 **공개 동작 명세에서 독립 재유도** 한 나비구름(NabiCloud)
저작물이다. 재유도 로그·출처→데이터 대응·표현 비복제 선언은
[`PROVENANCE-318na.md`](PROVENANCE-318na.md) 를 보라.

## 자판 설계 사실의 출처 (Attribution)

- **이름**: 세벌식 3-18Na (318Na) keyboard layout
- **설계 공개**: **navilera** — navilera.com '318Na 세벌식 자판' 정본 페이지,
  KLDP node/160815·node/165195 (공개 설명 글).
  - https://github.com/navilera/NavilIME
  - https://github.com/navilera/318Na_HangulKeyboard
- 인용한 것은 자판의 **동작 사실**(키→자모 매핑, 종성 순환 규칙)뿐이며,
  navilera/NavilIME·OHI 등 GPL 코드의 **표현**(자료구조·식별자·함수 본문·직렬화
  포맷·주석 문장)은 복제하지 않았다.

## 본 데이터의 작성 방식 (독립 재유도)

- `keyboards/318na.xml` 은 위 공개 명세의 동작 사실을 나비구름 **자체 직렬화**(섹션
  구조·항목 순서·주석 전부 독립 표현)로 적은 것이다. 기존 전사본과 **byte-비동치**이며,
  검증 기준은 **기능 동치**(키시퀀스 → 유니코드 정규화 음절 회귀)다.
- 엔진의 `nabicloud_engine_jongseong_cycle` 도 navilera 함수 포팅이 아니라 범용
  데이터주도 전처리로 독립 재작성했다(2후보 고정, 순차-if 의미 보존).

## 라이선스 (License)

- 본 데이터(`keyboards/318na.xml`)는 **CC BY-SA 4.0** 으로 배포한다(데이터 © 나비구름).
  navilera 코드의 *표현*을 복제하지 않고 공개 명세에서 독립 구현한 저작물이며, 자판 배열
  *설계 사실*의 출처 표시로 위 navilera/NavilIME·KLDP 글을 명시한다. (저작권 대상이 아닌
  배열 사실은 누구나 재구현 가능 — 본 라이선스는 이 파일의 표현에 적용.)
  - CC BY-SA 4.0 전문: <https://creativecommons.org/licenses/by-sa/4.0/legalcode>
    (한국어 <https://creativecommons.org/licenses/by-sa/4.0/legalcode.ko>).
- 종전 NOTICE(전사본·byte-동치 충실본 주장)는 폐기되었다 — 이 데이터는 더 이상
  navilera C 배열의 전사본이 아니다.

## 검증 (Verification)

- 기능 골든: `shared/engine/tests/build_and_verify_318na.bat` → `318NA_PASS`
  (12 케이스, 키시퀀스 → NFC 음절). 동작 오라클(전사본)과도 12/12 동일 결과 대조 완료.
- 타 26 빌트인 자판 byte-골든: `build_and_verify_all.bat` → `ALL_PASS` (불변).
