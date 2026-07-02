# addons/semoe/archive — 강등(은퇴) 세모이 산출물

이 디렉터리는 **더 이상 활성이 아닌 세모이 참고 산출물**을 보존한다.
셸이 로드하지 않고, 릴리스 인스톨러·dev 배포 어디에도 동봉되지 않는다.

| 파일 | 강등 사유 | 비고 |
|---|---|---|
| `semoe-chord.xml` | `type="semoe-chord"`(enum 1006) 모아치기 자판은 **2026-06-19 강등**(WU4) — 모아치기 활성화가 별도 1006 자판이 아니라 활성 자판의 `<flags loose-order="true">` + `[semoe] moachigi` 게이트로 바뀌면서 불요해졌다. 또 날개셋 KeyTable 의 *기본 레이어 default 값만* best-effort 추출한 것이라 chord 엔진·기호 레이어·상태전이 미반영 = 동작 미보증. | 옛 경로 `addons/semoe/data/keyboards/semoe-chord.xml`(셸 스캔 경로 `<DLL>\keyboards`·`<DLL>\addons\semoe\keyboards` 둘 다 아님 → 미로드). 2026-06-26 여기로 이동(릴리스 인스톨러 `File /r data\*.*` 과배포 시 동봉되던 것 차단). CC BY-SA 4.0(출처 Sinseiki/Semo-e). 설계 서술 = `docs/SEMOE_CHORD_DESIGN.md`(옛 경로로 참조 — 역사 기록). |

> 정리 근거: Codex V2 이식 재점검(2026-06-26) 후속 — 릴리스 애드온 인스톨러가 런타임 불요 dev 소스·강등본을 동봉하지 않도록 `data\` 글로브를 런타임 2파일(`.dic`·`.tsv`) 명시 배치로 좁히면서, 강등본을 active `data/` 트리에서 분리.
