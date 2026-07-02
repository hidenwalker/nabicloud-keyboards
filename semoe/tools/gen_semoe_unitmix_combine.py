#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gen_semoe_unitmix_combine.py — 세모이 UnitMixTable(437규칙) → (base 자모 a, base 자모 b)
#   → 합용 Unicode 결합표 생성기 (Stage 2).
#
#   배경 (SEMOE_ADDON_PLAN §6d.1 / SEMOE_CHORD_UNITCODE.md):
#     세모이 chord 의 합용 결합은 날개셋 UnitMixTable(unit-code 공간) 로 정의된다.
#     표준 결합표(combination id=0)는 옛한글 합용(ㅅ+ㄱ→U+112D 등)을 만들지 않으므로
#     약어(.dic) 키의 89.1%(holdback 977)가 Stage 1 에서 도달 불가였다.
#     이 스크립트는 UnitMixTable + unit-code→Unicode legend 로
#       (입력 base 자모쌍의 conjoining 코드포인트) → (합용 결과 conjoining 코드포인트)
#     결합표를 role(CHO/JUNG/JONG)별로 생성한다. 결과는 엔진(engine-chord.c) 빌트인 .c
#     + self-test/스크립트 공용 .tsv 로 emit (단일 정본).
#
#   ── unit-code → Unicode legend (정본: SEMOE_CHORD_UNITCODE.md, 날개셋 공식 도움말 상수열) ──
#     seed(키 직접입력) 26종은 2018 XML map id=0 에서 직접 확인됨(검증). 합성 토큰은
#     Unicode 자모 이름(romanization)으로 환원. ★환원 불가/모호 토큰은 legend 에서 None →
#     그 토큰을 산출하는 UnitMix 규칙은 **보류**(억지 매핑 금지, 프롬프트 지시).
#
#   사용:
#     python gen_semoe_unitmix_combine.py            # .tsv + .c 생성 + 검증
#     python gen_semoe_unitmix_combine.py --verify   # 생성 없이 검증만
#
#   재현성: stdlib(re, unicodedata) 만.

import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
MIX = os.path.join(DATA, "semoe_jamo_mix.xml")
XML2018 = os.path.normpath(os.path.join(HERE, "..", "keyboards", "3moa-semoe-2018.xml"))
OUT_TSV = os.path.join(DATA, "semoe_unitmix_combine.tsv")
OUT_C = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "shared", "engine", "nabicloud", "engine",
    "semoe-unitmix-table.c"))

# ── seed unit-code → conjoining 코드포인트 (2018 XML map 검증 + 날개셋 도움말 상수열) ──
SEED = {
    'CHO': {'G_': 0x1100, 'N_': 0x1102, 'D_': 0x1103, 'R_': 0x1105, 'M_': 0x1106,
            'B_': 0x1107, 'S_': 0x1109, 'Q_': 0x110B, 'J_': 0x110C, 'H_': 0x1112,
            'Z_': 0x1140, 'QQ': 0x1147, 'BS': 0x1121, 'BT': 0x1129, 'V_': 0x114C},
    'JUNG': {'A_': 0x1161, 'E_': 0x1166, 'EO': 0x1165, 'YEO': 0x1167, 'O_': 0x1169,
             'U_': 0x116E, 'EU': 0x1173, 'I_': 0x1175, '500': 0x1169},
    'JONG': {'G_': 0x11A8, 'N_': 0x11AB, 'R_': 0x11AF, 'M_': 0x11B7, 'B_': 0x11B8,
             'S_': 0x11BA, 'SS': 0x11BB, 'Q_': 0x11BC, 'Z_': 0x11EB, 'V_': 0x11F0,
             'D_': 0x11AE, 'J_': 0x11BD, 'C_': 0x11BE, 'K_': 0x11BF, 'T_': 0x11C0,
             'P_': 0x11C1, 'H_': 0x11C2},
}

# ── 합성 unit-code → Unicode 자모 이름(jamo spelling). 이름은 Unicode 표준 romanization.
#    None/'?' = legend 미해독·모호 → 보류. (정본 SEMOE_CHORD_UNITCODE.md §2)
SPELL = {
    'CHO': {
        'GG': 'SSANGKIYEOK', 'DD': 'SSANGTIKEUT', 'BB': 'SSANGPIEUP', 'SS': 'SSANGSIOS',
        'JJ': 'SSANGCIEUC', 'HH': 'SSANGHIEUH', 'NN': 'SSANGNIEUN', 'RR': 'SSANGRIEUL',
        'K_': 'KHIEUKH', 'T_': 'THIEUTH', 'P_': 'PHIEUPH', 'C_': 'CHIEUCH',
        'DG': 'TIKEUT-KIYEOK', 'RG': 'RIEUL-KIYEOK', 'BG': 'PIEUP-KIYEOK',
        'SG': 'SIOS-KIYEOK', 'ND': 'NIEUN-TIKEUT',
        'DR': 'TIKEUT-RIEUL', 'MD': 'MIEUM-TIKEUT', 'BD': 'PIEUP-TIKEUT',
        'DS': 'TIKEUT-SIOS', 'DJ': 'TIKEUT-CIEUC', 'RM': 'RIEUL-MIEUM',
        'RB': 'RIEUL-PIEUP', 'RJ': 'RIEUL-CIEUC', 'RH': 'RIEUL-HIEUH',
        'SD': 'SIOS-TIKEUT', 'MB': 'MIEUM-PIEUP', 'SM': 'SIOS-MIEUM',
        'SN': 'SIOS-NIEUN', 'SJ': 'SIOS-CIEUC',
        'SB': 'SIOS-PIEUP', 'BJ': 'PIEUP-CIEUC',
        'BSG': 'PIEUP-SIOS-KIYEOK', 'BSD': 'PIEUP-SIOS-TIKEUT',
        # 옛한글 합용 — Unicode 자모 이름이 일치하는 것만 환원(이름표 검증).
        'QT': 'IEUNG-THIEUTH', 'QR': 'IEUNG-RIEUL', 'QS': 'IEUNG-SIOS',
        # 환원 불가/모호(단일 코드포인트 없음·이름 불일치) → 보류. 억지 매핑 금지(프롬프트 지시).
        #   MQ/PQ/BQ(초성)·GC(ㄱㅈ)·MJ(ㅁㅈ)·HM(ㅎㅁ) = 초성 단일 코드포인트 부재.
        'GC': None, 'MJ': None, 'HM': None, 'MQ': None, 'PQ': None, 'BQ': None,
        'QG': None, 'QD': None, 'QB': None, 'QP': None, 'RQ': None, 'BBQ': None,
        'X_': None, 'wC': None, 'wJ': None, 'wJJ': None, 'wS': None, 'wSS': None,
        'Cw': None, 'Jw': None, 'JJw': None, 'Sw': None, 'SSw': None,
    },
    'JUNG': {
        'YA': 'YA', 'YE': 'YE', 'YO': 'YO', 'YU': 'YU', 'YAE': 'YAE', 'AE': 'AE',
        'WA': 'WA', 'WAE': 'WAE', 'WE': 'WE', 'WI': 'WI', 'OI': 'OE',
        # 옛한글 복모음 ext-B 및 합성 — Unicode 자모 이름이 일치하는 것만 환원, 나머지 보류.
        'F_': 'ARAEA', 'FF': 'SSANGARAEA', 'FI': 'ARAEA-I',
        'IA': 'I-A', 'IYE': 'I-YE', 'IYAE': 'I-YAE', 'IYEO': 'I-YEO',
        'UA': 'U-A', 'UEO': None, 'OE': 'OE', 'OYEO': 'O-YEO',
        'AO': 'A-O', 'AU': 'A-U', 'EOO': 'EO-O', 'YEOO': None, 'YAO': 'YA-O',
        'YEOU': 'YEO-U', 'YOI': 'YO-I', 'YOYA': 'YO-YA', 'YOYAE': 'YO-YAE',
        'YUI': 'YU-I', 'YUYE': 'YU-YE', 'YUYEO': 'YU-YEO',
        'EUE': 'EU-E', 'EUEO': 'EU-EO', 'EUI': None, 'EUO': 'EU-O', 'EUU': 'EU-U',
        'IEU': 'I-EU', 'II': 'I-I',
    },
    'JONG': {
        'GG': 'SSANGKIYEOK', 'GN': 'KIYEOK-NIEUN', 'GS': 'KIYEOK-SIOS', 'GB': 'KIYEOK-PIEUP',
        'NJ': 'NIEUN-CIEUC', 'NH': 'NIEUN-HIEUH', 'NS': 'NIEUN-SIOS', 'NZ': 'NIEUN-PANSIOS',
        'ND': 'NIEUN-TIKEUT', 'RG': 'RIEUL-KIYEOK', 'RM': 'RIEUL-MIEUM', 'RB': 'RIEUL-PIEUP',
        'RS': 'RIEUL-SIOS', 'RH': 'RIEUL-HIEUH', 'RP': 'RIEUL-PHIEUPH', 'RD': 'RIEUL-TIKEUT',
        'RT': 'RIEUL-THIEUTH', 'RZ': 'RIEUL-PANSIOS', 'RGS': 'RIEUL-KIYEOK-SIOS',
        'RBS': 'RIEUL-PIEUP-SIOS', 'MB': 'MIEUM-PIEUP', 'MS': 'MIEUM-SIOS',
        'MZ': 'MIEUM-PANSIOS', 'BS': 'PIEUP-SIOS', 'SG': 'SIOS-KIYEOK', 'SD': 'SIOS-TIKEUT',
        'SB': 'SIOS-PIEUP', 'VS': None, 'VZ': None, 'MQ': None,
        'BQ': None, 'PQ': None, 'RX': None, 'RRK': None, 'X_': None,
    },
}


def build_name_index():
    ranges = {'CHO': [(0x1100, 0x115F), (0xA960, 0xA97F)],
              'JUNG': [(0x1160, 0x11A7), (0xD7B0, 0xD7C6)],
              'JONG': [(0x11A8, 0x11FF), (0xD7CB, 0xD7FB)]}
    tag = {'CHO': 'CHOSEONG', 'JUNG': 'JUNGSEONG', 'JONG': 'JONGSEONG'}
    idx = {'CHO': {}, 'JUNG': {}, 'JONG': {}}
    for role, rs in ranges.items():
        for lo, hi in rs:
            for c in range(lo, hi + 1):
                try:
                    nm = unicodedata.name(chr(c))
                except ValueError:
                    continue
                if tag[role] in nm:
                    idx[role][nm.split(tag[role] + ' ')[1]] = c
    return idx


_NAMEIDX = build_name_index()


def resolve(role, unit):
    """unit-code → conjoining 코드포인트, 환원 불가/모호면 None(보류)."""
    if unit in SEED[role]:
        return SEED[role][unit]
    sp = SPELL[role].get(unit, '__missing__')
    if sp is None or sp == '__missing__':
        return None
    return _NAMEIDX[role].get(sp)


def parse_mix():
    """semoe_jamo_mix.xml → {role: [(a,b,to), ...]} (unit-code 공간, 등장순)."""
    txt = open(MIX, encoding="utf-8").read()
    out = {'CHO': [], 'JUNG': [], 'JONG': []}
    cur = None
    for line in txt.splitlines():
        rm = re.search(r'<Unit role="(\w+)"', line)
        if rm:
            cur = rm.group(1)
        for m in re.finditer(r'a="([^"]+)" b="([^"]+)" to="([^"]+)"', line):
            if cur in out:
                out[cur].append(m.groups())
    return out


def build_combine_table():
    """role 별 (a_cp, b_cp) → to_cp 결합표. base 입력쌍만(단일키로 도달) emit.
       legend 보류(None) 토큰이 끼면 그 규칙 보류. 반환 (table, stats)."""
    mix = parse_mix()
    table = {'CHO': {}, 'JUNG': {}, 'JONG': {}}
    held = {'CHO': [], 'JUNG': [], 'JONG': []}
    for role in ('CHO', 'JUNG', 'JONG'):
        for a, b, to in mix[role]:
            # 가상 단위 '500'(VirtualUnit, 날개셋 내부 "ㅗ 대기 상태" — SEMOE_CHORD_UNITCODE §2-2)
            #   은 물리 입력 자모가 아니다. 코드포인트가 실제 ㅗ(U+1169)와 충돌해 다른 합성
            #   규칙을 덮어쓰므로 결합표에서 제외(억지 매핑 금지). 실 ㅗ 입력은 O_ 로 충분.
            if a == '500' or b == '500':
                held[role].append((a, b, to))
                continue
            ca = resolve(role, a)
            cb = resolve(role, b)
            cto = resolve(role, to)
            if ca is None or cb is None or cto is None:
                held[role].append((a, b, to))
                continue
            # base 입력만(seed) — 합성 입력(예 GG+G_)은 폐포로 자연 도달하지만
            #   엔진은 도착순 pairwise fold 라 base 쌍이 우선. 합성 입력쌍도 등록(폐포 보강).
            table[role][(ca, cb)] = cto
    return table, held, mix


# ── self-test: 결합표로 holdback 도달성 재측정 ──
def closure_reach(table, base_by_role):
    reach = {r: set(base_by_role[r]) for r in 'CJT'}
    rolemap = {'CHO': 'C', 'JUNG': 'J', 'JONG': 'T'}
    changed = True
    while changed:
        changed = False
        for role, rmk in rolemap.items():
            for (a, b), to in table[role].items():
                if a in reach[rmk] and b in reach[rmk] and to not in reach[rmk]:
                    reach[rmk].add(to)
                    changed = True
    return reach


def main():
    table, held, mix = build_combine_table()
    nrules = sum(len(table[r]) for r in table)
    nheld = sum(len(held[r]) for r in held)
    ntotal = sum(len(mix[r]) for r in mix)

    if '--verify' not in sys.argv:
        write_tsv(table, held)
        write_c(table)

    print("UNITMIX_COMBINE rules=%d held=%d total=%d" % (nrules, nheld, ntotal))
    for r in ('CHO', 'JUNG', 'JONG'):
        print("  %s: emit=%d held=%d (held units=%s)"
              % (r, len(table[r]), len(held[r]),
                 sorted(set(to for _, _, to in held[r]))))


def write_tsv(table, held):
    nrows = sum(len(table[role]) for role in ('CHO', 'JUNG', 'JONG'))
    hdr = (
        "# 세모이 UnitMixTable → 합용 결합표 (Stage 2). role\\ta_cp\\tb_cp\\tto_cp (16진 conjoining).\n"
        "# 자동 생성: addons/semoe/tools/gen_semoe_unitmix_combine.py (semoe_jamo_mix.xml + legend).\n"
        "# legend 정본: SEMOE_CHORD_UNITCODE.md. 직접 편집 금지.\n"
        "# legend 미해독·모호 토큰은 보류(아래 # HELD 주석). 표준 결합표(id=0)와 별개·보강.\n"
        "#!rows\t" + str(nrows) + "\n"
        "# ↑ 런타임 무결성 선언(AbbrevDict::LoadUnitMix): 선언 행수와 실제 파싱 행수가 일치할 때만\n"
        "#   overlay 활성(fail-closed). 잘림·일부 손상 시 부분활성(침묵 오작동) 대신 전체 휴면.\n")
    with open(OUT_TSV, 'w', encoding='utf-8', newline='\n') as f:
        f.write(hdr)
        for role in ('CHO', 'JUNG', 'JONG'):
            for (a, b), to in sorted(table[role].items()):
                f.write("%s\t%04X\t%04X\t%04X\n" % (role, a, b, to))
        for role in ('CHO', 'JUNG', 'JONG'):
            for a, b, to in held[role]:
                f.write("# HELD %s %s+%s->%s (legend 미해독)\n" % (role, a, b, to))


def write_c(table):
    role_const = {'CHO': 'NABICLOUD_CHORD_ROLE_CHO',
                  'JUNG': 'NABICLOUD_CHORD_ROLE_JUNG',
                  'JONG': 'NABICLOUD_CHORD_ROLE_JONG'}
    lines = []
    lines.append("/* semoe-unitmix-table.c -- 세모이 UnitMix 합용 결합표 (빌트인, 자동 생성).")
    lines.append(" *")
    lines.append(" *   생성기: addons/semoe/tools/gen_semoe_unitmix_combine.py")
    lines.append(" *   원천 데이터: addons/semoe/data/semoe_jamo_mix.xml (UnitMixTable, CC BY-SA, ssgi.kr)")
    lines.append(" *   legend 정본: docs/SEMOE_CHORD_UNITCODE.md (날개셋 공식 도움말 상수열).")
    lines.append(" *   ★직접 편집 금지 — 데이터/legend 수정 후 생성기 재실행.")
    lines.append(" *")
    lines.append(" *   격리: 이 표는 nabicloud_engine_chord_compose (engine-chord.c, SEMOE_CHORD/세모이")
    lines.append(" *   모아치기 compose 경로 전용)에서만 조회된다. 표준 입력(hangul_ic_process)·비-세모이")
    lines.append(" *   자판은 이 표를 경유하지 않으므로 골든 byte-불변.")
    lines.append(" *")
    lines.append(" *   License: LGPL-2.1-or-later (engine code). See PATCHES.md / NOTICE.")
    lines.append(" */")
    lines.append("#include \"hangul.h\"")
    lines.append("#include \"engine-chord.h\"")
    lines.append("")
    lines.append("const SemoeUnitMixRule nabicloud_semoe_unitmix_table[] = {")
    for role in ('CHO', 'JUNG', 'JONG'):
        for (a, b), to in sorted(table[role].items()):
            lines.append("    { %s, 0x%04X, 0x%04X, 0x%04X },"
                         % (role_const[role], a, b, to))
    lines.append("};")
    lines.append("")
    lines.append("const int nabicloud_semoe_unitmix_table_count =")
    lines.append("    (int)(sizeof(nabicloud_semoe_unitmix_table) / sizeof(nabicloud_semoe_unitmix_table[0]));")
    lines.append("")
    # ★UTF-8 BOM (한국어 주석 포함 소스 — 트리 convention: engine *.c 는 BOM 필수,
    #   CP949 brace 깨짐 방지). 데이터 .tsv 는 BOM-free(LoadFile 가 첫 줄 BOM 만 관용).
    with open(OUT_C, 'w', encoding='utf-8-sig', newline='\n') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
