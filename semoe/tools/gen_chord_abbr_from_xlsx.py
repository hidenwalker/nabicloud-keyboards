#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gen_chord_abbr_from_xlsx.py — 세모이 chord 약어(HanSubst) .dic 권위 재키잉 (데이터 전용)
#
#   ★정본 입력 = addons/semoe/reference/세모이 자판 약어 (가나다순).xlsx 의 "조합키" 컬럼.
#     이 컬럼은 사용자가 실제로 치는 base 자모(호환자모 표기, 합용은 "ㄱ+ㅈ")를 슬롯별로
#     (초성 D·중성 E·종성 F) 직접 적은 **공개 legend**(SEMOE_CHORD_UNITCODE §1-B)다.
#     → 역추론 raw.tsv 시그니처(합성-후·PUA)에 의존하지 않고, 사용자 입력에서 런타임과
#       동일한 fold 규칙으로 .dic 키를 재도출한다. (raw.tsv 는 교차검증용으로 강등.)
#
#   파이프라인(런타임 동일):
#     (1) xlsx 행 → (단어, 초성토큰열, 중성토큰열, 종성토큰열). 단어의 'v' = 공백(xlsx 범례).
#     (2) 호환자모 토큰 → 슬롯별 conjoining base 자모(초성 U+11xx / 중성 / 종성).
#         "ㄱ+ㅈ" = 두 base 초성 [U+1100,U+110C]. 합성형 단일 토큰(ㄲ·ㅐ·ㅘ·ㄶ…)도
#         그 conjoining 코드로 매핑(런타임 fold 폐포로 도달가능).
#     (3) 각 슬롯의 base 자모열을 fold_run(UnitMix 합용표 우선 → 표준 결합표 fallback)으로
#         도착순 pairwise 접어 합성 시그니처 생성 = 사용자가 그 키를 칠 때 셸이 만드는 시그니처.
#         (regen_chord_abbr_dic.py 의 fold_run 과 동일 — 단일정본 재사용.)
#     (4) build_canonical_key(초성→중성→종성, 실모음 없으면 U+1160 채움 1개) → .dic 키.
#     (5) 충돌검사: 같은 키 다른 단어 = 충돌 → 보류(임의 덮어쓰기 금지). 충돌없는 전건 emit.
#         매핑 불가 토큰(슬롯-역할 불일치 등)도 보류(자판미도달) — 추측 매핑 금지.
#
#   ★fold 규칙·결합표는 regen_chord_abbr_dic.py 에서 재사용(load_keyboard_tables/fold_run/
#     build_canonical_key/classify). 디싱크 방지 단일정본.
#
#   사용:
#     python gen_chord_abbr_from_xlsx.py            # xlsx → .dic 재도출 + 보고
#     python gen_chord_abbr_from_xlsx.py --verify   # 재생성 없이 self-test(파싱·fold·충돌)
#     python gen_chord_abbr_from_xlsx.py --crosscheck  # raw.tsv 역추론 .dic 과 교차대조
#
#   재현성: stdlib 만 사용(zipfile + xml.etree). openpyxl 불요.

import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
REF = os.path.normpath(os.path.join(HERE, "..", "reference"))
XLSX = os.path.join(REF, "세모이 자판 약어 (가나다순).xlsx")
DIC = os.path.join(DATA, "semoe_chord_abbr.dic")
HOLDBACK = os.path.join(DATA, "semoe_chord_abbr_holdback.tsv")
PUA = os.path.join(DATA, "semoe_chord_abbr_pua.tsv")
RAW = os.path.join(DATA, "semoe_chord_abbr_raw.tsv")

# regen 도구의 결합표·fold·빌더 재사용(단일정본·디싱크 방지).
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "regen_chord_abbr_dic", os.path.join(HERE, "regen_chord_abbr_dic.py"))
_regen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_regen)

JUNG_FILL = 0x1160

# ── 호환자모 → conjoining 슬롯 매핑 (표준 유니코드 자모 블록 오프셋) ──────────────
# 초성 19종 / 중성 21종 / 종성 27종(빈칸 제외). 합용 단일 토큰(ㄲ·ㅐ·ㅘ·ㄶ…)도 포함 —
# 그 conjoining 코드는 런타임 fold 폐포로 base 자모에서 도달가능(reachability 로 확인).
_CHO = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ',
        'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
_JUNG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ',
         'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
_JONG = ['ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ',
         'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ',
         'ㅌ', 'ㅍ', 'ㅎ']
CHO_MAP = {c: 0x1100 + i for i, c in enumerate(_CHO)}
JUNG_MAP = {c: 0x1161 + i for i, c in enumerate(_JUNG)}
JONG_MAP = {c: 0x11A8 + i for i, c in enumerate(_JONG)}


def _slot_map(slot):
    return {'CHO': CHO_MAP, 'JUNG': JUNG_MAP, 'JONG': JONG_MAP}[slot]


# ── xlsx 파싱 (zipfile + sharedStrings + sheet1, stdlib) ──────────────────────
_NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def read_xlsx_rows():
    """가나다순.xlsx → [(word, 초성str, 중성str, 종성str)] (데이터 행만)."""
    z = zipfile.ZipFile(XLSX)
    ss = ET.fromstring(z.read('xl/sharedStrings.xml'))
    strings = [''.join(t.text or '' for t in si.iter(_NS + 't'))
               for si in ss.findall(_NS + 'si')]
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    sheetdata = sheet.find(_NS + 'sheetData')
    out = []
    for r in sheetdata.findall(_NS + 'row'):
        cells = {}
        for c in r.findall(_NS + 'c'):
            col = re.match(r'[A-Z]+', c.get('r')).group(0)
            t = c.get('t')
            v = c.find(_NS + 'v')
            if v is None:
                cells[col] = ''
            else:
                cells[col] = strings[int(v.text)] if t == 's' else v.text
        b = cells.get('B', '')
        d = cells.get('D', '')
        e = cells.get('E', '')
        f = cells.get('F', '')
        # 데이터 행 판정: 초성(D) 있고 헤더 아님.
        if not d.strip() or d.strip() == '조합키(초성)':
            continue
        out.append((b, d, e, f))
    return out


def word_from_cell(b):
    """xlsx 범례: 'v' = 공백. 단어 셀의 v 를 공백으로 치환(끝/앞/중간 공백 의미 보존)."""
    return b.replace('v', ' ')


def tokens(slotval):
    """슬롯 셀 'ㄱ+ㅈ' → ['ㄱ','ㅈ']. 빈칸 → []."""
    s = slotval.strip()
    if not s:
        return []
    return [t.strip() for t in s.split('+') if t.strip()]


def map_slot_tokens(slot, toks):
    """슬롯 토큰열 → conjoining base 자모열. 매핑 불가 토큰 있으면 (None, 사유)."""
    smap = _slot_map(slot)
    out = []
    for tk in toks:
        if tk in smap:
            out.append(smap[tk])
        else:
            return None, "매핑불가 토큰 %r(슬롯 %s)" % (tk, slot)
    return out, None


# fold 결과가 슬롯 역할을 벗어나면(예: 중성 슬롯에 자음 base) build_canonical_key 가
# 역할 재분류하면서 키가 왜곡될 수 있다 → 슬롯-역할 정합 검증.
def slot_role_ok(cho_b, jung_b, jong_b, rules):
    for c in _regen.fold_run(cho_b, rules):
        if _regen.classify(c) != 'L':
            return False
    for c in _regen.fold_run(jung_b, rules):
        if _regen.classify(c) != 'V':
            return False
    for c in _regen.fold_run(jong_b, rules):
        if _regen.classify(c) != 'T':
            return False
    return True


def build_key_checked(d, e, f, rules):
    """xlsx 슬롯 → canonical 키 1개. 실패 시 (None, 사유).
    ★같은-클래스 다중 자모(자음쌍 초성 ㅈ+ㄱ 등)는 build_canonical_key 가 클래스 내부를
      codepoint 오름차순 정렬하므로 도착순과 무관하게 단일 키로 수렴한다(순열 폭발 없음).
      셸 런타임 BuildCanonicalChordKey 도 같은 정렬을 하므로 키가 byte-동일하다 — 단일정본.
      (정렬 도입 전에는 도착순 보존이라 순열을 모두 emit 했으나, canonical 정렬로 폐기.)"""
    cho_b, err = map_slot_tokens('CHO', tokens(d))
    if err:
        return None, err
    jung_b, err = map_slot_tokens('JUNG', tokens(e))
    if err:
        return None, err
    jong_b, err = map_slot_tokens('JONG', tokens(f))
    if err:
        return None, err
    if not slot_role_ok(cho_b, jung_b, jong_b, rules):
        return None, "슬롯-역할 불일치(중/종성 슬롯에 비-역할 자모)"
    cho_sig = _regen.fold_run(cho_b, rules)
    jung_sig = _regen.fold_run(jung_b, rules)
    jong_sig = _regen.fold_run(jong_b, rules)
    cps = list(cho_sig) + list(jung_sig) + list(jong_sig)
    if not cps:
        return None, "빈 조합키"
    return _regen.build_canonical_key(cps), None


def regen():
    _sk, rules = _regen.load_keyboard_tables()
    rows = read_xlsx_rows()

    emit_keys = {}      # key -> set(words)
    word_key = {}       # word -> key (성공)
    holdback = []       # (word, d,e,f, 사유)
    pua_recovered = []  # 정보용 — PUA 회복(이 경로엔 PUA 없음, base 입력만)
    conflicts = []      # (word, key, 기존단어들)

    # 1차: 키 산출.
    pending = []        # (word, key)
    for b, d, e, f in rows:
        word = word_from_cell(b)
        key, err = build_key_checked(d, e, f, rules)
        if key is None:
            holdback.append((word, d, e, f, err))
            continue
        pending.append((word, key))

    # 2차: 충돌검사(같은 키·다른 단어). 충돌나는 단어는 보류(임의 덮어쓰기 금지).
    key_words = {}
    for word, key in pending:
        key_words.setdefault(key, []).append(word)
    conflict_keys = {k for k, ws in key_words.items() if len(set(ws)) > 1}

    emit = []           # (key, word)
    seen_word = set()
    for word, key in pending:
        if key in conflict_keys:
            holdback.append((word, '', '', '',
                             "키 충돌(키=%s, 단어들=%s)"
                             % ('+'.join('U+%04X' % ord(c) for c in key),
                                sorted(set(key_words[key])))))
            conflicts.append((word, key, sorted(set(key_words[key]))))
            continue
        # 같은 (word,key) 중복 방지(혹시 동일행 중복).
        if (key, word) in seen_word:
            continue
        seen_word.add((key, word))
        emit.append((key, word))
        emit_keys.setdefault(key, set()).add(word)
        word_key[word] = key

    return {
        'rows': rows, 'emit': emit, 'emit_keys': emit_keys, 'word_key': word_key,
        'holdback': holdback, 'conflicts': conflicts, 'rules': rules,
    }


_DIC_HEADER = (
    "# 세모이 약어 (HanSubstTable) — chord 자모열(conjoining U+11xx) → 확장 단어\n"
    "# ★권위 재키잉(2026-06-19): 정본 입력 = reference/세모이 자판 약어 (가나다순).xlsx 의\n"
    "#   '조합키(초성/중성/종성)' 컬럼(사용자가 실제로 치는 base 자모). 역추론 raw.tsv 시그니처가\n"
    "#   아니라 이 공개 legend 에서 런타임 동일 fold 로 키를 재도출한다.\n"
    "# 형식: <conjoining 자모열>:<단어>  (자모열 = canonical 초성→중성→종성, "
    "모음 없고 종성 있으면 U+1160 채움)\n"
    "# fold = 세모이 UnitMix 합용표(우선) + 3moa-semoe-2018.xml <combine>(fallback) —\n"
    "#   엔진 chord_combine 과 동일 순서(단일정본). 단어 'v'=공백(xlsx 범례) 치환, 공백 의미 보존.\n"
    "# 출처: ssgi.kr 세모이(세벌식 모아치기 e) · CC BY-SA 4.0 · 약어표 xlsx 조합키 정본.\n"
    "# 자동 생성: addons/semoe/tools/gen_chord_abbr_from_xlsx.py. 직접 편집 금지 — xlsx 수정 후 재생성.\n"
)

_HOLD_HEADER = (
    "# [격리·보류] 세모이 약어 — xlsx 권위 재키잉에서 자판미도달 또는 키 충돌로 보류된 분.\n"
    "#   자판미도달 = 조합키 토큰이 슬롯-역할에 안 맞거나(중성 슬롯에 자음 등) 매핑 불가.\n"
    "#   충돌 = 같은 canonical 키가 다른 단어로 중복 → 임의 우선순위 덮어쓰기 금지(둘 다 보류).\n"
    "# 폐기 아님(xlsx 정본 유지, raw.tsv 역추론은 교차검증용). 추측 매핑 금지.\n"
    "# ★본가 문의(2026-06-19): 이 5건 조합키 표기(슬롯-역할 불일치)의 입력 의도를 세모이 본가에 문의 →\n"
    "#   https://github.com/Sinseiki/Semo-e_keyboard/issues/1 . 회신 시 반영(그때까지 추측 매핑 금지·보류 유지).\n"
    "# 형식: <단어>\\t조합키[D|E|F]\\t# <보류사유>\n"
)


def write_outputs(r):
    emit = r['emit']
    n = 0
    with open(DIC, 'w', encoding='utf-8', newline='\n') as fp:
        fp.write(_DIC_HEADER)
        for key, word in emit:
            fp.write(key + ':' + word + '\n')
            n += 1
    with open(HOLDBACK, 'w', encoding='utf-8', newline='\n') as fp:
        fp.write(_HOLD_HEADER)
        for word, d, e, f, why in r['holdback']:
            combo = 'D=%s|E=%s|F=%s' % (d, e, f)
            fp.write('%s\t%s\t# %s\n' % (word, combo, why))
    # PUA: 이 경로는 base 입력만 다루므로 PUA 출력 자모가 없다 → pua.tsv 는 비운다(헤더만).
    pua_header = (
        "# [권위 재키잉으로 해소] 세모이 약어 PUA(F809/F852/F8BC) 격리 보류는\n"
        "#   xlsx 조합키(base 자모 입력) 정본화로 자연 회복되어 .dic 으로 편입됨.\n"
        "#   PUA 는 합성-후 시그니처(역추론) 산물이었고, 사용자 입력 자체는 base 자모쌍이다.\n"
        "#   본 파일은 더 이상 보류분을 담지 않는다(빈 격리).\n"
    )
    with open(PUA, 'w', encoding='utf-8', newline='\n') as fp:
        fp.write(pua_header)
    return n


def crosscheck():
    """raw.tsv 역추론 .dic(과거) 과 xlsx-권위 키 교차대조.
       겹치는 단어의 키 일치/불일치 집계. xlsx 가 정본 — 불일치는 역추론 오류 표본."""
    r = regen()
    word_key = r['word_key']
    # raw.tsv 의 단어→키(역추론 시그니처를 build_canonical_key 로 접은 것 = 과거 .dic 키 규칙).
    raw_word_key = {}
    with open(RAW, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            if not line or line.startswith('#'):
                continue
            keytext, word = line.split('\t', 1)
            cps = _regen.parse_raw_key(keytext)
            raw_word_key[word] = _regen.build_canonical_key(cps)
    both = set(word_key) & set(raw_word_key)
    match = mismatch = 0
    samples = []
    for w in both:
        if word_key[w] == raw_word_key[w]:
            match += 1
        else:
            mismatch += 1
            if len(samples) < 12:
                samples.append((w,
                                '+'.join('U+%04X' % ord(c) for c in word_key[w]),
                                '+'.join('U+%04X' % ord(c) for c in raw_word_key[w])))
    only_xlsx = set(word_key) - set(raw_word_key)
    only_raw = set(raw_word_key) - set(word_key)
    print("CROSSCHECK: 겹치는 단어=%d 일치=%d 불일치=%d | xlsx만=%d raw만=%d"
          % (len(both), match, mismatch, len(only_xlsx), len(only_raw)))
    if samples:
        print("  불일치 표본(단어 | xlsx권위키 | raw역추론키):")
        for w, xk, rk in samples:
            print("    %r  %s  vs  %s" % (w, xk, rk))
    return True


def verify():
    """self-test(스크립트측): xlsx 파싱·fold·충돌·무손실 분류.
       (1) 데이터 행수 = emit단어 + holdback(자판미도달+충돌) (무손실).
       (2) emit 키 무충돌(같은 키·다른 단어 없음).
       (3) 각 emit 키: fold 왕복 — 키의 자모를 base 로 역분해(decompose) → 다시 fold 하면
           키와 일치(셸 매칭 토대). regen 의 verify_resourcing 과 동일 원리."""
    _sk, rules = _regen.load_keyboard_tables()
    byrole, _reach = _regen.role_closure(_sk, rules)
    r = regen()
    rows, emit, holdback = r['rows'], r['emit'], r['holdback']

    # (1) 무손실: distinct 단어 기준.
    emit_words = set(w for _, w in emit)
    hold_words = set(w for w, *_ in holdback)
    all_words = set(word_from_cell(b) for b, _, _, _ in rows)
    # emit + holdback 가 전체 단어를 덮어야 함(충돌 단어는 holdback 에 있음).
    covered = emit_words | hold_words
    if covered != all_words:
        missing = all_words - covered
        print("VERIFY FAIL 무손실 위반 누락=%d 예=%s" % (len(missing), list(missing)[:5]))
        return False

    # (2) 무충돌.
    seen = {}
    for key, word in emit:
        if key in seen and seen[key] != word:
            print("VERIFY FAIL 충돌 잔존 key=%s %r/%r"
                  % (key, seen[key], word))
            return False
        seen[key] = word

    # (3) fold 왕복.
    for key, word in emit:
        keycps = [ord(c) for c in key]
        base_by_role = {'L': [], 'V': [], 'T': []}
        for c in keycps:
            if c == JUNG_FILL:
                continue
            rc = _regen.classify(c)
            seq = _regen.decompose(c, rules, byrole)
            if seq is None:
                print("VERIFY FAIL decompose key=%s word=%r cp=U+%04X" % (key, word, c))
                return False
            base_by_role[rc].extend(seq)
        for rc in 'LVT':
            for c in base_by_role[rc]:
                if c not in byrole[rc]:
                    print("VERIFY FAIL non-singlekey base U+%04X key=%s" % (c, key))
                    return False
        folded = {rc: _regen.fold_run(base_by_role[rc], rules) for rc in 'LVT'}
        exp = {'L': [c for c in keycps if _regen.classify(c) == 'L'],
               'V': [c for c in keycps if _regen.classify(c) == 'V' and c != JUNG_FILL],
               'T': [c for c in keycps if _regen.classify(c) == 'T']}
        for rc in 'LVT':
            if folded[rc] != exp[rc]:
                print("VERIFY FAIL fold 불일치 key=%s role=%s folded=%s exp=%s"
                      % (key, rc, [hex(x) for x in folded[rc]], [hex(x) for x in exp[rc]]))
                return False

    print("VERIFY PASS xlsx행=%d emit단어=%d 보류=%d(충돌%d) fold왕복=OK"
          % (len(rows), len(emit_words), len(hold_words), len(r['conflicts'])))
    return True


def main():
    if '--verify' in sys.argv:
        sys.exit(0 if verify() else 1)
    if '--crosscheck' in sys.argv:
        sys.exit(0 if crosscheck() else 1)
    r = regen()
    n = write_outputs(r)
    distinct = len(set(w for _, w in r['emit']))
    total_words = len(set(word_from_cell(b) for b, *_ in r['rows']))
    print("재키잉 완료: xlsx 데이터행=%d → .dic emit 키=%d (distinct 단어=%d) | 보류=%d (충돌%d)"
          % (len(r['rows']), n, distinct, len(r['holdback']), len(r['conflicts'])))
    print("  도달률 = distinct 단어 %d / xlsx distinct 단어 %d = %.1f%%"
          % (distinct, total_words, 100.0 * distinct / total_words))
    if r['conflicts']:
        print("  충돌 표본:")
        for w, key, ws in r['conflicts'][:8]:
            print("    %r 키=%s ↔ %s"
                  % (w, '+'.join('U+%04X' % ord(c) for c in key), ws))
    if not verify():
        sys.exit(1)


if __name__ == '__main__':
    main()
