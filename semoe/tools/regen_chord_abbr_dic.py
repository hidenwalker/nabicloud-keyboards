#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# regen_chord_abbr_dic.py — 세모이 chord 약어(HanSubst) .dic 재생성 + 도달성 게이트 (Stage 1)
#
#   목적: addons/semoe/data/semoe_chord_abbr_raw.tsv (코드포인트 표기·정본) 로부터
#         addons/semoe/data/semoe_chord_abbr.dic (conjoining 자모 U+11xx 리터럴 키) 를
#         재생성하되, **현 Stage(엔진 무수정)에서 실제 도달 가능한 약어만** emit 한다.
#
#   ── 도달성 게이트 (진단 wfpx5ejhl / SEMOE_ADDON_PLAN §6d.1) ──────────────────
#   .dic 키(=HanSubst from)는 **합성-후 "음절 시그니처 자모"** 다. 셸이 chord 로 모으는
#   자모는 활성 자판 map id=0 의 single-key 26종(초10·중8·종8) base 자모뿐이고, 이들이
#   결합 경로로 접혀(fold) 합성형이 된다. Stage 2 부터 결합 경로 = **세모이 UnitMix 합용표
#   (우선) + 표준 결합표(id=0, fallback)** — 엔진 chord_combine(engine-chord.c) 과 동일 순서.
#   따라서 약어가 실제 도달 가능하려면 그 키의 모든 자모가
#     reach[role] = closure(single-key base 자모, UnitMix∪표준 결합표)
#   안에 있어야 한다. 분류:
#     baseReachable    : 전 자모가 single-key base (현 형태로 바로 매칭)
#     composeReachable : 전 자모가 base 또는 base 쌍을 결합 경로로 접어 만든 합성형
#                        (Stage 2: 표준 결합표 + UnitMix 합용 폐포)
#     needsEngineExt   : UnitMix legend 미해독·모호(보류) 토큰 필요 — 여전히 도달 불가 (격리)
#     impossible(PUA)  : 세모이 PUA 트리거(F809/F852/F8BC 등) — 표준 경로 없음, Stage 3 (격리)
#   .dic 에는 base+composeReachable 만 emit. 잔여 needsEngineExt 는 holdback.tsv,
#   PUA 는 pua.tsv 로 격리(보류, 폐기 아님). raw.tsv 는 정본 그대로 유지.
#
#   ★디싱크 방지(단일 정본): 결합표 시뮬레이터는 두 정본을 직접 파싱한다 —
#   (1) 표준 결합표: addons/semoe/keyboards/3moa-semoe-2018.xml <combine table=cho/jung/jong>.
#   (2) UnitMix 합용표: addons/semoe/data/semoe_unitmix_combine.tsv
#       (gen_semoe_unitmix_combine.py 가 semoe_jamo_mix.xml+legend 로 생성, 엔진 빌트인
#        semoe-unitmix-table.c 와 동일 데이터). 셸 런타임도 엔진 chord_combine(UnitMix→표준)
#        을 거치므로 스크립트·셸·self-test·엔진이 **같은 결합 규칙**을 참조한다.
#
#   raw.tsv 형식 : "<KEY>\t<단어>"  (각 줄)
#     KEY = "U+XXXX+U+YYYY+..." 코드포인트열. 이미 canonical 순서(초성→중성→종성)이며,
#           모음 없고 종성 있으면 중성 슬롯에 U+1160(채움)이 들어 있다.
#     단어 = 확장 문자열. ★끝/앞 공백이 의미를 가진다(자동 띄어쓰기) — 절대 trim 금지.
#
#   .dic 형식    : "<conjoining키>:<단어>"  (BOM-free UTF-8)
#
#   사용:
#     python regen_chord_abbr_dic.py            # raw.tsv → .dic(245) + holdback/pua 격리 재생성
#     python regen_chord_abbr_dic.py --verify   # 재생성 없이 self-test(도달성 분류·빌더 정합)
#
#   재현성: stdlib 만 사용.

import os
import re
import sys

_CP_RE = re.compile(r'U\+([0-9A-Fa-f]+)')

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
RAW = os.path.join(DATA, "semoe_chord_abbr_raw.tsv")
DIC = os.path.join(DATA, "semoe_chord_abbr.dic")
HOLDBACK = os.path.join(DATA, "semoe_chord_abbr_holdback.tsv")
PUA = os.path.join(DATA, "semoe_chord_abbr_pua.tsv")
XML = os.path.normpath(os.path.join(HERE, "..", "keyboards", "3moa-semoe-2018.xml"))
UNITMIX = os.path.join(DATA, "semoe_unitmix_combine.tsv")  # Stage 2 합용 결합표(정본)

JUNG_FILL = 0x1160  # 중성 채움(모음 없음·종성 있음 표시)

# ── Stage 3 재소싱(데이터 전용): holdback 합용 초성 → base 초성쌍 ──────────────────
#   holdback 67건의 첫 자모는 5종의 합용 옛초성(KAPYEOUN*·YEORINHIEUH)이다. 이들은
#   UnitMix 규칙으로 만들어지나 그 결과 unit-code(X_/RQ/MQ/BQ/PQ)가 legend 미해독(단일
#   유니코드 부재)이라 Stage 2 합용표에 없다 → 셸 fold 가 그 base 쌍을 **결합 못 함(0 반환)**
#   → un-folded base 두 초성으로 남는다. 따라서 .dic 에 그 **base 초성쌍**(canonical, 합용
#   미적용)을 emit 하면 런타임 fold 결과(=2-초성 base 키)와 정확히 매칭된다(엔진/셸 무수정).
#
#   base 쌍의 근거(SEMOE_CHORD_UNITCODE §1-B 약어표 자모식 + §2-1 합용 unit-code + 단어 첫소리):
#     U+1159 YEORINHIEUH    = X_ = ㅎ+ㄴ (학년·하늘·하나님 …)      → (U+1112, U+1102)
#     U+111B KAPYEOUNRIEUL  = RQ = ㄴ+ㄹ (노력·논리·나라 …)        → (U+1102, U+1105)
#     U+111D KAPYEOUNMIEUM  = MQ = ㄴ+ㅁ (논문·눈물·농민 …)        → (U+1102, U+1106)
#     U+112B KAPYEOUNPIEUP  = BQ = ㄴ+ㅂ (남편·농부·비난 …)        → (U+1102, U+1107)
#     U+1157 KAPYEOUNPHIEUPH= PQ = ㄴ+ㅈ (작년·주님·나중 …)        → (U+1102, U+110C)
#   두 base 모두 map id=0 single-key 초성(ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎ)이라 물리키로 직접 도달.
#   ★중성/종성은 raw 합성형 그대로 둔다 — 그 합성형은 Stage 2 폐포로 이미 도달가능(base 중/종성
#     쌍을 fold 하면 재현). 즉 재소싱은 **합용 초성만** base 쌍으로 치환한다.
#   ★초성 입력 순서 양립: 모아치기는 물리키 도착순이 비결정적이고 BuildCanonicalChordKey 는
#     초성을 도착순 그대로(정렬 없이) 둔다. 두 base 가 결합 안 되므로(NOFOLD) [a,b]·[b,a]
#     두 순서가 서로 다른 키가 된다 → **양 순서를 모두 emit**(충돌 없을 때)해 입력 순서 무관 매칭.
#   PUA(F809/F852/F8BC)는 재소싱 불가(아래 §pua 주석) — pua.tsv 잔류.
HOLD_CHO_BASE = {
    0x1159: (0x1112, 0x1102),
    0x111B: (0x1102, 0x1105),
    0x111D: (0x1102, 0x1106),
    0x112B: (0x1102, 0x1107),
    0x1157: (0x1102, 0x110C),
}


def classify(cp):
    """conjoining 자모 코드포인트를 'L'(초성)/'V'(중성)/'T'(종성)/'?'(미지) 으로 분류."""
    if 0x1100 <= cp <= 0x115F:
        return 'L'
    if 0x1160 <= cp <= 0x11A7 or 0xD7B0 <= cp <= 0xD7C6:
        return 'V'
    if 0x11A8 <= cp <= 0x11FF or 0xD7CB <= cp <= 0xD7FB:
        return 'T'
    # 확장-A(0xA960~0xA97F) = 초성 확장. PUA(0xE000~0xF8FF) = 세모이 초성 변형(도달성에서 별도 취급).
    if 0xA960 <= cp <= 0xA97F or 0xE000 <= cp <= 0xF8FF:
        return 'L'
    return '?'


def is_pua(cp):
    return 0xE000 <= cp <= 0xF8FF


# ── 단일정본 파서 (V2 <jaso-map> single-key 자모 + <combine> 결합표: UnitMix 우선 + 표준 fallback) ──
def load_unitmix_rules():
    """semoe_unitmix_combine.tsv → {(a,b): result}. 파일 부재면 빈 dict(Stage 1 호환)."""
    rules = {}
    if not os.path.exists(UNITMIX):
        return rules
    with open(UNITMIX, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) != 4:
                continue
            _role, a, b, to = parts
            rules[(int(a, 16), int(b, 16))] = int(to, 16)
    return rules


def load_keyboard_tables():
    """결합 경로(엔진 chord_combine 과 동일 순서: UnitMix 우선, 표준 fallback) 적재.
       반환: (singlekeys:set[int], rules:dict[(a,b)->result])."""
    txt = open(XML, encoding="utf-8").read()
    singlekeys = set()
    # ★V2 확장 XML(<jaso-map>/<combine>, f5de938b 이관) 파싱 — 옛 <map id=0>/<combination id=0>
    #   포맷은 은퇴(2026-06-26 전수정리). <jaso-map> 의 <key ... a="0x.."> = single-key base 자모.
    jmap = re.search(r'<jaso-map>(.*?)</jaso-map>', txt, re.S)
    if jmap:
        for m in re.finditer(r'<key\b[^>]*\ba="0x([0-9a-fA-F]+)"', jmap.group(1)):
            v = int(m.group(1), 16)
            if 0x1100 <= v <= 0x11FF:   # MapKeyToJamo 와 동일: 한글 자모 영역만 chord 자모
                singlekeys.add(v)
    rules = {}
    # <combine table="cho|jung|jong"> 의 <item have add result> = 표준 결합표.
    for cb in re.finditer(r'<combine\b[^>]*>(.*?)</combine>', txt, re.S):
        for m in re.finditer(
                r'<item\b[^>]*\bhave="0x([0-9a-fA-F]+)"[^>]*\badd="0x([0-9a-fA-F]+)"[^>]*\bresult="0x([0-9a-fA-F]+)"',
                cb.group(1)):
            a, b, r = [int(x, 16) for x in m.groups()]
            rules[(a, b)] = r
    # ★UnitMix 우선(엔진 chord_combine 과 동일): UnitMix 가 같은 쌍을 다르게 정의하면 덮어쓴다.
    rules.update(load_unitmix_rules())
    return singlekeys, rules


def role_closure(singlekeys, rules):
    """role 별 도달집합 = single-key base 에서 결합표를 고정점까지 적용한 폐포."""
    byrole = {'L': set(), 'V': set(), 'T': set()}
    for c in singlekeys:
        r = classify(c)
        if r in byrole:
            byrole[r].add(c)
    reach = {r: set(byrole[r]) for r in 'LVT'}
    changed = True
    while changed:
        changed = False
        for (a, b), res in rules.items():
            rc = classify(res)
            if rc in reach and a in reach[rc] and b in reach[rc] and res not in reach[rc]:
                reach[rc].add(res)
                changed = True
    return byrole, reach


def decompose(target, rules, byrole, _seen=None):
    """합성형 자모 target → 그것으로 접히는 single-key base 시퀀스(self-test 의 물리키 역매핑).
       못 풀면 None. role 동질·결합표 역추적(DFS).
       ★refold 검증: 여러 규칙이 같은 target 을 낼 수 있고 fold 는 우선순위(UnitMix>표준)
       에 민감하므로, 후보 base 열을 fold_run 으로 다시 접어 [target] 과 일치할 때만 채택한다
       (디싱크 회귀 방지). 일치 안 하면 다음 분해 분기로 백트랙."""
    role = classify(target)
    if role in byrole and target in byrole[role]:
        return [target]
    if _seen is None:
        _seen = set()
    if target in _seen:
        return None
    _seen = _seen | {target}
    for (a, b), res in rules.items():
        if res == target and classify(res) == role:
            da = decompose(a, rules, byrole, _seen)
            db = decompose(b, rules, byrole, _seen)
            if da is not None and db is not None:
                cand = da + db
                if fold_run(cand, rules) == [target]:   # refold 왕복 확인
                    return cand
    return None


def fold_run(run, rules):
    """role-run(같은 부류 자모열) 을 결합표로 도착순 pairwise 접기(셸 빌더와 동일 의미).
       접히지 않는 쌍은 그대로 남긴다(길이>1 가능 = 비합성)."""
    if not run:
        return []
    acc = [run[0]]
    for c in run[1:]:
        r = rules.get((acc[-1], c))
        if r is not None and classify(r) == classify(acc[-1]):
            acc[-1] = r
        else:
            acc.append(c)
    return acc


def reachability(cps, byrole, reach):
    """raw KEY 코드포인트열 → ('base'|'compose'|'ext'|'pua')."""
    sig = [c for c in cps if c != JUNG_FILL]
    if any(is_pua(c) for c in sig):
        return 'pua'
    all_base = True
    for c in sig:
        rc = classify(c)
        if rc == '?' or c not in reach.get(rc, ()):
            return 'ext'
        if c not in byrole.get(rc, ()):
            all_base = False
    return 'base' if all_base else 'compose'


def build_canonical_key(cps):
    """도착순(순서무관) 코드포인트 리스트 → canonical conjoining 키 문자열(채움규칙 적용).
       (합성은 안 함 — 이미 합성된 시그니처 cps 의 정렬·채움만. 셸 BuildCanonicalChordKey 와 동일.)
       ★두-초성 매칭 버그(런타임 테스트로 확정): 같은-클래스 다중 자모(자음쌍 초성 등)는 동시타
         도착순이 비결정이므로, 클래스 내부를 codepoint 오름차순 정렬해 도착순과 무관한 단일 키로
         수렴시킨다. 셸 BuildCanonicalChordKey 도 같은 오름차순 정렬을 하므로 키가 byte-동일하다."""
    cho, jung, jong = [], [], []
    for cp in cps:
        if cp == JUNG_FILL:
            continue
        c = classify(cp)
        if c == 'L':
            cho.append(cp)
        elif c == 'V':
            jung.append(cp)
        elif c == 'T':
            jong.append(cp)
        # '?' 는 무시(매칭 실패로 안전).
    # ★클래스 내 codepoint 오름차순 정렬(도착순 무관). 단일 자모면 무영향.
    cho.sort()
    jung.sort()
    jong.sort()
    out = list(cho)
    if jung:
        out.extend(jung)
    else:
        out.append(JUNG_FILL)   # 실모음 없음 → 채움 1개(종성 유무 무관)
    out.extend(jong)
    return ''.join(chr(c) for c in out)


def resource_holdback_keys(cps):
    """holdback 행 cps → 재소싱 키 후보 리스트. 첫 자모가 HOLD_CHO_BASE 에 없으면 None
       (재소싱 불가). 합용 초성만 base 쌍으로 치환, 중/종성은 raw 합성형 유지.
       ★canonical 정렬 도입(두-초성 버그 수정) 이후: 두 초성을 build_canonical_key 로 통과시키면
         codepoint 오름차순 정렬돼 도착순 (a,b)/(b,a) 가 같은 단일 키로 수렴한다 → 양 입력순서를
         따로 emit 할 필요가 없다(순열·도착순 폐기). 런타임 BuildCanonicalChordKey 와 byte-동일."""
    first = cps[0]
    base = HOLD_CHO_BASE.get(first)
    if base is None:
        return None
    rest = cps[1:]
    jung = [c for c in rest if classify(c) == 'V' and c != JUNG_FILL]
    jong = [c for c in rest if classify(c) == 'T']
    a, b = base
    # build_canonical_key 가 클래스 내 정렬을 담당 — 단일 키(도착순 무관).
    key = build_canonical_key([a, b] + jung + jong)
    return [key]


def parse_raw_key(keytext):
    cps = [int(m.group(1), 16) for m in _CP_RE.finditer(keytext)]
    if not cps:
        raise ValueError("코드포인트 없음: %r" % keytext)
    rebuilt = '+'.join('U+%04X' % c for c in cps)
    if rebuilt.upper() != keytext.upper():
        raise ValueError("키 파싱 불완전: %r != %r" % (keytext, rebuilt))
    return cps


def read_raw():
    rows = []
    with open(RAW, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            if not line or line.startswith('#'):
                continue
            tab = line.find('\t')
            if tab < 0:
                raise ValueError("탭 없음: %r" % line)
            keytext = line[:tab]
            word = line[tab + 1:]
            cps = parse_raw_key(keytext)
            rows.append((keytext, cps, word))
    return rows


def regen():
    singlekeys, rules = load_keyboard_tables()
    byrole, reach = role_closure(singlekeys, rules)
    rows = read_raw()

    emit, hold, pualist = [], [], []
    for keytext, cps, word in rows:
        cat = reachability(cps, byrole, reach)
        if cat in ('base', 'compose'):
            emit.append((keytext, cps, word))
        elif cat == 'ext':
            hold.append((keytext, cps, word))
        else:
            pualist.append((keytext, cps, word))

    # ── Stage 1/2 도달분의 folded 키(충돌 기준 a). ──
    emit_keys = {}   # key → set(words)
    for keytext, cps, word in emit:
        emit_keys.setdefault(build_canonical_key(cps), set()).add(word)

    # ── Stage 3 재소싱(데이터 전용): holdback 합용 초성 → base 초성쌍, 충돌 게이트. ──
    #   2단계: (1) 후보 키 산출(양 초성순서) (2) 전수 충돌검사 — 기존 emit 키·다른 재소싱 키와
    #   같은 키·다른 단어면 그 약어 전체를 재소싱 불가로 보류(임의 우선순위 덮어쓰기 금지).
    resourced = []      # (key, word) — .dic 에 추가할 재소싱분
    hold_remain = []    # 재소싱 못한 holdback(보류 잔류)
    resourced_keys = {} # key → set(words) (재소싱 내부 충돌 검사)
    n_collide = 0
    collide_samples = []
    for keytext, cps, word in hold:
        cand = resource_holdback_keys(cps)
        if cand is None:
            hold_remain.append((keytext, cps, word, "재소싱불가(합용 초성 base 미상)"))
            continue
        # 이 약어의 후보 키들이 (기존 emit 의 다른 단어) 또는 (다른 재소싱의 다른 단어)와 충돌?
        conflict = None
        for k in cand:
            if k in emit_keys and word not in emit_keys[k]:
                conflict = ("기존 .dic", k, sorted(emit_keys[k]))
                break
            if k in resourced_keys and word not in resourced_keys[k]:
                conflict = ("재소싱", k, sorted(resourced_keys[k]))
                break
        if conflict is not None:
            n_collide += 1
            if len(collide_samples) < 8:
                collide_samples.append((word, conflict))
            hold_remain.append((keytext, cps, word,
                                "충돌로 보류(%s 키 중복·다른 단어)" % conflict[0]))
            continue
        for k in cand:
            resourced.append((k, word))
            resourced_keys.setdefault(k, set()).add(word)

    dic_header = (
        "# 세모이 약어 (HanSubstTable) — chord 자모열(conjoining U+11xx) → 확장 단어  "
        "[Stage 1/2 도달분 + Stage 3 재소싱분]\n"
        "# 형식: <conjoining 자모열>:<단어>   (자모열 = canonical 초성→중성→종성, "
        "모음 없고 종성 있으면 U+1160 채움)\n"
        "# 키는 합성-후 음절 시그니처 자모. 셸은 chord base 자모(<jaso-map> single-key)를 결합표\n"
        "#   (세모이 UnitMix 합용표 우선 + 3moa-semoe-2018.xml <combine> fallback)로 접어\n"
        "#   이 키와 매칭한다 — 단일 정본(엔진 chord_combine 과 동일 순서).\n"
        "# ★Stage 3 재소싱: 일부 합용 옛초성(KAPYEOUN*·YEORINHIEUH)은 그 합용 결과 unit-code 가\n"
        "#   legend 미해독(단일 유니코드 부재)이라 fold 가 base 쌍을 결합 못 함(0) → un-folded base\n"
        "#   2-초성으로 남는다. 그 base 초성쌍을 키로 emit(합용 미적용, 양 입력순서)해 매칭한다.\n"
        "#   PUA(F809/F852/F8BC)는 표준 입력경로 없어 재소싱 불가 → pua.tsv 잔류.\n"
        "# 단어 끝/앞 공백은 의미(자동 띄어쓰기)이므로 보존된다 — 로더(LoadAddonFile)도 공백 보존.\n"
        "# 출처: ssgi.kr 세모이(세벌식 모아치기 e) · CC BY-SA 4.0 · 원본 날개셋 IME XML HanSubst.\n"
        "# 자동 생성: addons/semoe/tools/regen_chord_abbr_dic.py "
        "(semoe_chord_abbr_raw.tsv 에서). 직접 편집 금지 — raw.tsv 수정 후 재생성.\n"
    )
    n_emit_lines = 0
    with open(DIC, 'w', encoding='utf-8', newline='\n') as f:
        f.write(dic_header)
        for keytext, cps, word in emit:
            f.write(build_canonical_key(cps) + ':' + word + '\n')
            n_emit_lines += 1
        if resourced:
            f.write("# ── Stage 3 재소싱분(합용 초성 → base 초성쌍, 양 입력순서) ──\n")
        for key, word in resourced:
            f.write(key + ':' + word + '\n')
            n_emit_lines += 1

    hold_header = (
        "# [격리·보류] 세모이 약어 needsEngineExt(잔여) — UnitMix 합용 결과 unit-code 가 legend\n"
        "#   미해독이라 base 쌍 또는 도달 경로가 없는 약어. Stage 3 재소싱에서 매핑 미상 또는\n"
        "#   키 충돌로 보류된 분. 폐기 아님(raw.tsv 정본 유지).\n"
        "# 형식: raw.tsv 와 동일(<U+...코드포인트열>\\t<단어>)  # <보류사유>. 정본은 semoe_chord_abbr_raw.tsv.\n"
    )
    with open(HOLDBACK, 'w', encoding='utf-8', newline='\n') as f:
        f.write(hold_header)
        for keytext, cps, word, why in hold_remain:
            f.write(keytext + '\t' + word + '\t# ' + why + '\n')

    pua_header = (
        "# [격리·보류·재소싱불가] 세모이 약어 impossible(PUA) — 키가 세모이 PUA(U+E000~F8FF,\n"
        "#   날개셋 HanSubst 트리거 식별자 F809/F852/F8BC)를 포함.\n"
        "# Stage 3 판정: 재소싱 불가. PUA 는 chord 출력 자모가 아니라 '약어 클래스 트리거 식별자'\n"
        "#   (SEMOE_CHORD_UNITCODE §3)라 표준 입력 자모 경로가 없다. 한 PUA 초성 아래 단어들의\n"
        "#   첫소리가 여러 초성으로 흩어져(예 F809=ㄱ53·ㅈ35·ㅊ9·ㄲ2·ㅇ1) 단일 base 쌍으로 환원\n"
        "#   불가 → 억지 매핑 금지(프롬프트 지시). 영구 보류(폐기 아님, raw.tsv 정본 유지).\n"
        "# 형식: raw.tsv 와 동일(<U+...코드포인트열>\\t<단어>). 정본은 semoe_chord_abbr_raw.tsv.\n"
    )
    with open(PUA, 'w', encoding='utf-8', newline='\n') as f:
        f.write(pua_header)
        for keytext, cps, word in pualist:
            f.write(keytext + '\t' + word + '\n')

    return {
        'total': len(rows), 'stage12_rows': len(emit), 'stage12_keys': len(emit_keys),
        'resourced_words': len(set(w for _, w in resourced)),
        'resourced_keys': len(resourced),
        'hold_remain': len(hold_remain), 'collide': n_collide,
        'pua': len(pualist), 'emit_lines': n_emit_lines,
        'collide_samples': collide_samples,
    }


def verify():
    """self-test(스크립트측): 도달성 분류·빌더 정합·결합표 폐포 무결.
         (1) 분류 합계가 raw 전체와 일치(손실 0).
         (2) emit(base+compose) 의 각 키: 합성형 시그니처를 base 로 역분해(decompose) →
             결합표 fold 로 다시 접으면 원 시그니처와 동일(셸 매칭 가능 입증).
         (3) build_canonical_key 가 도착순 역순 셔플에도 동일 키 산출(순서무관).
       (셸 C++ BuildCanonicalChordKey + CombineChordJamo 는 별도 콘솔 self-test 로 같은 데이터 입증.)"""
    singlekeys, rules = load_keyboard_tables()
    byrole, reach = role_closure(singlekeys, rules)
    rows = read_raw()

    nbase = ncompose = next_ = npua = 0
    for keytext, cps, word in rows:
        cat = reachability(cps, byrole, reach)
        if cat == 'base':
            nbase += 1
        elif cat == 'compose':
            ncompose += 1
        elif cat == 'ext':
            next_ += 1
        else:
            npua += 1

    if nbase + ncompose + next_ + npua != len(rows):
        print("PY-SELFTEST FAIL 분류 손실")
        return False

    # emit 분의 fold 왕복 + 빌더 순서무관 검증.
    for keytext, cps, word in rows:
        cat = reachability(cps, byrole, reach)
        if cat not in ('base', 'compose'):
            continue
        sig = [c for c in cps if c != JUNG_FILL]
        # role 별 합성형을 base 로 역분해.
        base_by_role = {'L': [], 'V': [], 'T': []}
        ok = True
        for c in sig:
            rc = classify(c)
            seq = decompose(c, rules, byrole)
            if seq is None:
                ok = False
                break
            base_by_role[rc].extend(seq)
        if not ok:
            print("PY-SELFTEST FAIL decompose key=%s" % keytext)
            return False
        # base 자모 전부 single-key 인지(물리키 도달 가능) 확인.
        for rc in 'LVT':
            for c in base_by_role[rc]:
                if c not in byrole[rc]:
                    print("PY-SELFTEST FAIL non-singlekey base U+%04X key=%s" % (c, keytext))
                    return False
        # base 를 결합표로 다시 접으면 원 시그니처와 일치해야 한다(셸 매칭 토대).
        folded = {rc: fold_run(base_by_role[rc], rules) for rc in 'LVT'}
        exp = {'L': [c for c in sig if classify(c) == 'L'],
               'V': [c for c in sig if classify(c) == 'V'],
               'T': [c for c in sig if classify(c) == 'T']}
        for rc in 'LVT':
            if folded[rc] != exp[rc]:
                print("PY-SELFTEST FAIL fold mismatch key=%s role=%s folded=%s exp=%s"
                      % (keytext, rc, [hex(x) for x in folded[rc]], [hex(x) for x in exp[rc]]))
                return False
        # build_canonical_key 순서무관(역순 셔플) 입증.
        expected_key = ''.join(chr(c) for c in cps)
        jamoset = [c for c in cps if c != JUNG_FILL]
        if build_canonical_key(list(reversed(jamoset))) != expected_key:
            print("PY-SELFTEST FAIL builder order key=%s" % keytext)
            return False

    print("PY-SELFTEST PASS rows=%d base=%d compose=%d emit=%d holdback=%d pua=%d"
          % (len(rows), nbase, ncompose, nbase + ncompose, next_, npua))
    return True


def verify_resourcing():
    """Stage 3 재소싱 키의 fold-일치 입증(가설 검증). .dic 의 모든 키를 읽어:
       (a) 각 키의 초성을 base 로 역분해(decompose) → 전부 single-key 인지.
       (b) base 자모를 role 별 fold_run(UnitMix→표준) 으로 다시 접으면 .dic 키와 일치(셸 매칭 토대).
       이로써 재소싱(2-초성 NOFOLD)·Stage 1/2(합성형) 키가 모두 런타임 fold 경로와 일치함을 확인.
       (b) 가 실패하면 그 쌍이 311/표준표로 *결합돼버려* base 키가 안 나온다는 뜻 → 재소싱 불가."""
    singlekeys, rules = load_keyboard_tables()
    byrole, reach = role_closure(singlekeys, rules)
    if not os.path.exists(DIC):
        print("PY-RESOURCE FAIL .dic 없음")
        return False
    n = ok = 0
    with open(DIC, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            key, _word = line.split(':', 1)
            n += 1
            keycps = [ord(c) for c in key]
            base_by_role = {'L': [], 'V': [], 'T': []}
            good = True
            for c in keycps:
                if c == JUNG_FILL:
                    continue
                rc = classify(c)
                seq = decompose(c, rules, byrole)
                if seq is None:
                    print("PY-RESOURCE FAIL decompose key=%s cp=U+%04X" % (key, c))
                    good = False
                    break
                base_by_role[rc].extend(seq)
            if not good:
                return False
            for rc in 'LVT':
                for c in base_by_role[rc]:
                    if c not in byrole[rc]:
                        print("PY-RESOURCE FAIL non-singlekey base U+%04X key=%s" % (c, key))
                        return False
            folded = {rc: fold_run(base_by_role[rc], rules) for rc in 'LVT'}
            exp = {'L': [c for c in keycps if classify(c) == 'L'],
                   'V': [c for c in keycps if classify(c) == 'V' and c != JUNG_FILL],
                   'T': [c for c in keycps if classify(c) == 'T']}
            for rc in 'LVT':
                if folded[rc] != exp[rc]:
                    print("PY-RESOURCE FAIL fold 불일치 key=%s role=%s folded=%s exp=%s"
                          % (key, rc, [hex(x) for x in folded[rc]], [hex(x) for x in exp[rc]]))
                    return False
            ok += 1
    print("PY-RESOURCE PASS dic_keys=%d fold일치=%d" % (n, ok))
    return True


def main():
    if '--verify' in sys.argv:
        sys.exit(0 if (verify() and verify_resourcing()) else 1)
    r = regen()
    print("regenerated %s : Stage1/2행=%d (키%d) + 재소싱 단어=%d (키%d, 양순서) "
          "→ .dic 줄=%d | 보류=%d (그중 충돌%d) | pua=%d | raw총=%d"
          % (os.path.basename(DIC), r['stage12_rows'], r['stage12_keys'],
             r['resourced_words'], r['resourced_keys'], r['emit_lines'],
             r['hold_remain'], r['collide'], r['pua'], r['total']))
    reached = r['stage12_rows'] + r['resourced_words']
    split = r['stage12_rows'] + r['resourced_words'] + r['hold_remain'] + r['pua']
    print("  도달 단어 = %d/%d = %.1f%%  (무손실 분할 합 = Stage1/2 %d + 재소싱 %d + 보류 %d + pua %d = %d)"
          % (reached, r['total'], 100.0 * reached / r['total'],
             r['stage12_rows'], r['resourced_words'], r['hold_remain'], r['pua'], split))
    if r['collide_samples']:
        print("  충돌 표본:")
        for w, (where, k, words) in r['collide_samples']:
            print("    '%s' %s 키=%s ↔ %s" % (w, where, '+'.join('%04X' % ord(x) for x in k), words))
    if not (verify() and verify_resourcing()):
        sys.exit(1)


if __name__ == '__main__':
    main()
