#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gen_dubeol_abbrev.py — 두겹이/두줄이 약어(UserCompoTable) .dic 생성 (데이터 전용, 독립 재유도)
#
#   ★정본 입력 = 본가 "부가기능 포함" XML 의 <UserCompoTable> 상태머신(날개셋 IME 자판 설정).
#     references/dugyeob-e/부가기능 포함/두벌식 겹받침 e (두겹이) (부가기능 포함).xml
#     references/dujul-e /부가기능 포함/두벌식 줄맞춤 e (두줄이) (부가기능 포함).xml
#   교차검증 입력 = 같은 폴더의 "약어 (빈도순).xlsx"(표시글자/품사/조합키) — 사람이 읽는 표.
#
#   ── 본가 약어 메커니즘(전사 대상) ───────────────────────────────────────────────
#   본가 약어는 **두 개의 기호(Shift+빈글쇠로 입력되는 □ … ↔ 등)를 연속 입력 → 단어** 인
#   상태머신이다. <UserCompoTable> 의 구조:
#     · state=0  + key=<기호> + newstate=S + interim=<기호>  : 첫 기호 입력 → 상태 S 전이(기호 preedit)
#     · state=S  + key=<기호2> + result=<단어>               : 둘째 기호 입력 → 단어 확정·commit
#   이 표는 **완전 대칭**이다(기호A→기호B = 기호B→기호A = 같은 단어). 즉 약어는
#   **순서무관 기호쌍 → 단어** 사상이며, 자판당 정확히 70개다(빈도순).
#
#   기호는 표준 두벌식 Shift 층에서 "된소리/이중모음이 없는 빈 자리"(ㅁㄹㄴㅎㅋ… 자음·
#   ㅗㅜㅡㅕ… 모음의 Shift 위치)에만 의도적으로 배치된다 → 약어 트리거 글쇠 집합은
#   된소리(ㄸㄲㅃㅉ)·이중모음(ㅒㅖ)·단키겹받침(fill-jong) 글쇠와 **서로소(disjoint)** 다.
#   (이 생성기가 그 서로소 성질을 assert 로 검증한다.)
#
#   ── 산출 .dic 포맷 ─────────────────────────────────────────────────────────────
#     <기호1><기호2>:<단어>
#     · 기호1<기호2 = 코드포인트 오름차순 정렬(순서무관 쌍의 정규형).
#     · 단어 = 본가 result 그대로(끝공백 보존 — "으로 "·"입니다. "·"사람"). xlsx 'v'=공백.
#     · 파일 순서 = 빈도 순위. # 주석은 무시.
#   런타임(트리거 단계, 후속)은 자판별 "기호 레이어"(Shift+글쇠→기호)로 입력 기호를 얻어
#   이 .dic 에서 정렬 기호쌍으로 조회한다. 기호 레이어 표는 헤더 주석 + DUBEOL_ABBREV_DESIGN.md.
#
#   출처: ssgi.kr / Sinseiki · CC BY-SA 4.0 (addons/dubeol/NOTICE-dubeol.md). 날개셋 IME 코드 비차용.
#   사용:  python gen_dubeol_abbrev.py            # references/ → .dic 재생성 + 검증 보고
#          python gen_dubeol_abbrev.py --verify   # 재생성 없이 파싱·대칭·충돌·xlsx 교차검증만
#
#   재현성: 표준 라이브러리만(zipfile + re). openpyxl 불요. (gen_chord_abbr_from_xlsx.py 와 동형)

import os, re, sys, zipfile, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))   # addons/dubeol/tools → repo root
DATA = os.path.normpath(os.path.join(HERE, '..', 'data'))

# 약어 기호 코드포인트 → 표시 문자
SYMBOL = {0xB7:'·', 0xD7:'×', 0x3A:':', 0x3B:';', 0x2026:'…', 0x203B:'※', 0x2190:'←',
          0x2191:'↑', 0x2192:'→', 0x2193:'↓', 0x2194:'↔', 0x25A1:'□', 0x25B3:'△',
          0x25BD:'▽', 0x25CB:'○', 0x25CE:'◎', 0x2661:'♡'}

# 조합형(초/중) → 호환 자모 (조합키/자모 주석 표기용)
_CHO = {0x1100:'ㄱ',0x1101:'ㄲ',0x1102:'ㄴ',0x1103:'ㄷ',0x1104:'ㄸ',0x1105:'ㄹ',0x1106:'ㅁ',
        0x1107:'ㅂ',0x1108:'ㅃ',0x1109:'ㅅ',0x110a:'ㅆ',0x110b:'ㅇ',0x110c:'ㅈ',0x110d:'ㅉ',
        0x110e:'ㅊ',0x110f:'ㅋ',0x1110:'ㅌ',0x1111:'ㅍ',0x1112:'ㅎ'}
_JUNG = {0x1161:'ㅏ',0x1162:'ㅐ',0x1163:'ㅑ',0x1164:'ㅒ',0x1165:'ㅓ',0x1166:'ㅔ',0x1167:'ㅕ',
         0x1168:'ㅖ',0x1169:'ㅗ',0x116a:'ㅘ',0x116b:'ㅙ',0x116c:'ㅚ',0x116d:'ㅛ',0x116e:'ㅜ',
         0x116f:'ㅝ',0x1170:'ㅞ',0x1171:'ㅟ',0x1172:'ㅠ',0x1173:'ㅡ',0x1174:'ㅢ',0x1175:'ㅣ'}
_CMP = {0x3131:'ㄱ',0x3132:'ㄲ',0x3134:'ㄴ',0x3137:'ㄷ',0x3138:'ㄸ',0x3139:'ㄹ',0x3141:'ㅁ',
        0x3142:'ㅂ',0x3143:'ㅃ',0x3145:'ㅅ',0x3146:'ㅆ',0x3147:'ㅇ',0x3148:'ㅈ',0x3149:'ㅉ',
        0x314a:'ㅊ',0x314b:'ㅋ',0x314c:'ㅌ',0x314d:'ㅍ',0x314e:'ㅎ',0x314f:'ㅏ',0x3150:'ㅐ',
        0x3151:'ㅑ',0x3152:'ㅒ',0x3153:'ㅓ',0x3154:'ㅔ',0x3155:'ㅕ',0x3156:'ㅖ',0x3157:'ㅗ',
        0x3158:'ㅘ',0x3159:'ㅙ',0x315a:'ㅚ',0x315b:'ㅛ',0x315c:'ㅜ',0x315d:'ㅝ',0x315e:'ㅞ',
        0x315f:'ㅟ',0x3160:'ㅠ',0x3161:'ㅡ',0x3162:'ㅢ',0x3163:'ㅣ'}

def jamo_name(cp):
    if 0x1100 <= cp <= 0x1112: return _CHO[cp]
    if 0x1161 <= cp <= 0x1175: return _JUNG[cp]
    return _CMP.get(cp, '?')

def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

# ── 본가 XML 파싱 ──────────────────────────────────────────────────────────────
def parse_keytable_shift(xml):
    """Shift 층(대문자 ASCII 0x41-0x5A 또는 기타) → 기호 코드포인트. <Key at=".." value="Z=0, 0xNNNN"/>."""
    out = {}
    for m in re.finditer(r'<Key at="(0x[0-9A-Fa-f]+)" value="([^"]*)"/>', xml):
        kc = int(m.group(1), 16); val = m.group(2)
        for hm in re.finditer(r'0x[0-9A-Fa-f]+', val):
            cp = int(hm.group(0), 16)
            if cp in SYMBOL:
                out.setdefault(kc, cp)
                break
    return out

def parse_usercompo(xml):
    """returns (sym2state, results): sym2state[기호cp]=상태, results=[(상태,기호cp,단어), ...]."""
    sym2state = {}; results = []
    pat = (r'<UserCompo state="(\d+)" key="(0x[0-9A-Fa-f]+)"'
           r'(?:\s+newstate="(\d+)")?(?:\s+interim="([^"]*)")?(?:\s+result="([^"]*)")?\s*/>')
    for m in re.finditer(pat, xml):
        st = int(m.group(1)); key = int(m.group(2), 16); ns = m.group(3); res = m.group(5)
        if st == 0 and ns is not None:
            sym2state[key] = int(ns)
        elif res is not None:
            results.append((st, key, res))
    return sym2state, results

def parse_our_keymap(path):
    """우리 자판 XML 의 keycode → 호환자모(base). 신포맷 <key code a=> + 구포맷 <item key value=> 모두."""
    xml = rd(path); up = {}; low = {}
    def put(kc, cp):
        cp = (0x3100 + 0) if False else cp
        name = jamo_name(cp)
        (up if kc < 0x60 else low)[kc] = name
    for m in re.finditer(r'<key code="(0x[0-9A-Fa-f]+)"[^>]*\sa="(0x[0-9A-Fa-f]+)"', xml):
        put(int(m.group(1), 16), int(m.group(2), 16))
    for m in re.finditer(r'<item key="(0x[0-9A-Fa-f]+)" value="(0x[0-9A-Fa-f]+)"', xml):
        put(int(m.group(1), 16), int(m.group(2), 16))
    return up, low

# ── XLSX(빈도순) 파싱: 단어 → (순위, 품사, 조합키 자모집합) ─────────────────────────
def parse_xlsx(path):
    z = zipfile.ZipFile(path); shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss = z.read('xl/sharedStrings.xml').decode('utf-8')
        for si in re.findall(r'<si>(.*?)</si>', ss, re.S):
            shared.append(html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si, re.S))))
    def col(c):
        n = 0
        for ch in c: n = n*26 + (ord(ch)-64)
        return n-1
    data = z.read('xl/worksheets/sheet1.xml').decode('utf-8'); out = {}
    jamoset = '|'.join(_CMP.values())
    for rowm in re.findall(r'<row[^>]*>(.*?)</row>', data, re.S):
        cells = {}
        for cm in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', rowm, re.S):
            ci = col(cm.group(1)); inner = cm.group(3)
            t = re.search(r't="([^"]+)"', cm.group(2)); vm = re.search(r'<v>(.*?)</v>', inner, re.S); v = ''
            if t and t.group(1) == 's' and vm: v = shared[int(vm.group(1))]
            elif vm: v = html.unescape(vm.group(1))
            cells[ci] = v
        if not cells: continue
        r = [cells.get(i, '') for i in range(max(cells)+1)]
        if len(r) < 2 or not re.match(r'^\d+$', r[0].strip()): continue
        rank = int(r[0].strip()); wkey = r[1].strip().replace('v', '').strip()
        pos = r[2].strip() if len(r) > 2 else ''
        cho = r[3] if len(r) > 3 else ''; jung = r[4] if len(r) > 4 else ''
        jamos = frozenset(re.findall(jamoset, cho) + re.findall(jamoset, jung))
        out[wkey] = (rank, pos, jamos)
    return out

# ── 한 자판 처리 ───────────────────────────────────────────────────────────────
def process(kbd_id, up_xml_path, our_xml_path, xlsx_path):
    xml = rd(up_xml_path)
    shift = parse_keytable_shift(xml)               # ascii → 기호cp
    sym2asc = {cp: kc for kc, cp in shift.items()}  # 기호cp → ascii(트리거 글쇠)
    sym2state, results = parse_usercompo(xml)
    state2sym = {st: cp for cp, st in sym2state.items()}
    up, low = parse_our_keymap(our_xml_path)
    xl = parse_xlsx(xlsx_path)

    # 순서무관 기호쌍 → 단어 + 대칭/충돌 검증
    pair_word = {}; directed = {}
    for st, keycp, word in results:
        if st not in state2sym:
            continue   # 도달불가 상태(빈사슬) — 다른 쌍이 같은 단어를 덮으므로 무해
        pr = frozenset((state2sym[st], keycp))
        directed.setdefault(pr, 0)
        directed[pr] += 1
        if pr in pair_word and pair_word[pr] != word:
            raise SystemExit(f"[{kbd_id}] CONFLICT 기호쌍 {pr} → {pair_word[pr]!r} vs {word!r}")
        pair_word[pr] = word
    asym = [pr for pr, n in directed.items() if n < 2]
    if asym:
        raise SystemExit(f"[{kbd_id}] 비대칭(단방향) 쌍 {len(asym)}: {asym}")

    # 기호 레이어(트리거 글쇠 → 기호) + 된소리/이중모음 서로소 검증
    def keylabel(asc):
        if asc is None: return '??'
        if 0x41 <= asc <= 0x5A: return f"Shift+{chr(asc)}"
        if asc == 0x3A: return "Shift+;"   # ':' = 세미콜론 글쇠의 Shift(우리 base ㅜ)
        return f"Shift+{chr(asc)}"
    # base 글쇠 문자(.dic/sym 키). 소문자 a-z + 세미콜론은 '~'(★AbbrevDict 가 ';' 시작 줄을 주석
    #   처리하므로 세미콜론 키는 '~'로 인코딩 — 런타임 VK_OEM_1↔'~' 매핑과 1:1). '#'·':'·';' 회피.
    def base_ch(asc):
        if asc is None: return '?'
        if 0x41 <= asc <= 0x5A: return chr(asc + 0x20)   # Shift+letter → 소문자
        if asc == 0x3B: return '~'                       # 세미콜론 키(':' 기호) → '~'
        return chr(asc)

    # 기호 레이어 = 쌍에 실제 쓰이는 기호만(KeyTable 미사용 기호 제외) {기호cp: base 글쇠}. trig_keys 도.
    used_syms = set()
    for pr in pair_word:
        used_syms |= set(pr)
    sym_layer = {cp: base_ch(sym2asc[cp]) for cp in used_syms if cp in sym2asc}
    trig_keys = set()
    for pr in pair_word:
        for cp in pr:
            asc = sym2asc.get(cp)
            if asc is not None: trig_keys.add(asc)
    occupied = set()
    for kc in range(0x41, 0x5B):
        u = up.get(kc); l = low.get(kc + 0x20)
        if u and l and u != l: occupied.add(kc)   # 대문자≠소문자 자모 = 된소리/이중모음
    clash = {k for k in trig_keys if k in occupied}
    if clash:
        raise SystemExit(f"[{kbd_id}] 트리거∩된소리 충돌 {sorted(clash)}")

    # .dic 키 = base 글쇠쌍(위 base_ch — 소문자 a-z + 세미콜론='~'). ★기호가 아니라 물리 base 글쇠로
    #   키잉 = (1) ':' 기호·구분자 충돌 회피, (2) 셸이 VK에서 직접 계산, (3) AbbrevDict(골든씰) 재사용.
    # xlsx 교차검증: 기호쌍의 자모(우리 base) == xlsx 조합키 자모집합
    rows = []   # (rank, base_key, word, pos, jamo, sym, keys)
    for pr, word in pair_word.items():
        a, b = sorted(pr)
        wkey = word.replace('　', '').strip()
        rank, pos, xljamo = xl.get(wkey, (999, '', frozenset()))
        ka, kb = sym2asc.get(a), sym2asc.get(b)
        def base_jamo(asc):
            if asc is None: return '?'
            lk = asc + 0x20 if 0x41 <= asc <= 0x5A else asc
            return low.get(lk) or up.get(asc) or '?'
        ja, jb = base_jamo(ka), base_jamo(kb)
        if xljamo and frozenset((ja, jb)) != xljamo:
            raise SystemExit(f"[{kbd_id}] xlsx 자모 불일치 #{rank} {wkey!r}: "
                             f"XML={sorted((ja,jb))} XLSX={sorted(xljamo)}")
        base_key = ''.join(sorted((base_ch(ka), base_ch(kb))))
        sym_key = SYMBOL[a] + SYMBOL[b]
        rows.append((rank, base_key, word, pos, f"{ja}+{jb}", sym_key,
                     f"{keylabel(ka)}+{keylabel(kb)}"))
    # base_key 중복(같은 글쇠쌍 다른 단어) 검사 — 물리쌍이 유일 키여야 함
    seen = {}
    for r in rows:
        if r[1] in seen and seen[r[1]] != r[2]:
            raise SystemExit(f"[{kbd_id}] base_key 충돌 {r[1]!r}: {seen[r[1]]!r} vs {r[2]!r}")
        seen[r[1]] = r[2]
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows, sym_layer, sorted(trig_keys), sorted(occupied), xl

def emit_dic(kbd_id, kbd_name, rows, sym_layer, trig_keys, out_path):
    # 기호 레이어: base 글쇠(소문자/'~'=세미콜론) → 기호. 표시(preedit)·감사용.
    #   sym_layer = {기호cp: base 글쇠}.
    layer_items = sorted((base, SYMBOL[cp]) for cp, base in sym_layer.items())
    layer_str = ' '.join(f"{ch}={sym}" for ch, sym in layer_items)
    hdr = [
        f"# {kbd_name} 약어 (본가 UserCompoTable 전사) — ★단일 사전(기호 레이어 + 글쇠쌍→단어)",
        f"# 형식(키 길이로 구분, 같은 AbbrevDict 1벌):",
        f"#   1글쇠:기호    = 기호 레이어(트리거 멤버십 + 첫 글쇠 preedit 표시).  예 d:♡  ~:: (세미콜론)",
        f"#   2글쇠:단어    = 순서무관 글쇠쌍 → 단어(끝공백 보존).               예 df:으로 ",
        f"# 글쇠 = 물리 base(소문자 a-z + 세미콜론='~'), Shift와 함께 입력. 코드포인트 오름차순 정렬.",
        f"#   ★기호가 아니라 base 글쇠로 키잉 = ':' 기호·구분자 충돌 회피 + 셸이 VK에서 직접 계산.",
        f"# 약어 = 두 글쇠(Shift+빈글쇠) 연속 입력 → 단어 commit(순서무관). 글쇠쌍은 빈도순.",
        f"# 트리거 글쇠는 된소리(ㄸㄲㅃㅉ)·이중모음(ㅒㅖ)·단키겹받침 글쇠와 서로소(충돌 없음, 생성기 assert).",
        f"# 기호 레이어 요약: {layer_str}",
        f"# 출처: ssgi.kr / Sinseiki (github.com/Sinseiki) · CC BY-SA 4.0 · 정본=본가 '부가기능 포함' XML.",
        f"#   라이선스·면책 = addons/dubeol/NOTICE-dubeol.md · 설계 = docs/DUBEOL_ABBREV_DESIGN.md.",
        f"# 자동 생성: addons/dubeol/tools/gen_dubeol_abbrev.py — 직접 편집 금지(본가 XML 수정 후 재생성).",
    ]
    sym_lines = [f"{base}:{SYMBOL[cp]}" for cp, base in sorted(sym_layer.items(), key=lambda kv: kv[1])]
    pair_lines = [f"{r[1]}:{r[2]}" for r in rows]   # base_key:word
    text = ('\n'.join(hdr) + '\n'
            + "# ── 기호 레이어(1글쇠:기호) ──\n" + '\n'.join(sym_lines) + '\n'
            + "# ── 약어(2글쇠쌍:단어, 빈도순) ──\n" + '\n'.join(pair_lines) + '\n')
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return len(sym_lines), len(pair_lines)

KEYBOARDS = [
    dict(id='dugyeobe', name='두겹이 (두벌식 겹받침)',
         up=REPO + '/references/dugyeob-e/부가기능 포함/두벌식 겹받침 e (두겹이) (부가기능 포함).xml',
         our=REPO + '/addons/dubeol/keyboards/dugyeobe.xml',
         xlsx=REPO + '/references/dugyeob-e/부가기능 포함/두겹이 자판 약어 (빈도순).xlsx',
         dic=DATA + '/dugyeobe_abbrev.dic'),
    dict(id='dujul-e', name='두줄이 (두벌식 줄맞춤)',
         up=REPO + '/references/dujul-e/부가기능 포함/두벌식 줄맞춤 e (두줄이) (부가기능 포함).xml',
         our=REPO + '/addons/dubeol/keyboards/dujul-e.xml',
         xlsx=REPO + '/references/dujul-e/부가기능 포함/두줄이 자판 약어 목록 (빈도순).xlsx',
         dic=DATA + '/dujul-e_abbrev.dic'),
]

def main():
    verify_only = '--verify' in sys.argv
    os.makedirs(DATA, exist_ok=True)
    total = 0
    for kb in KEYBOARDS:
        rows, sym_layer, trig, occ, xl = process(kb['id'], kb['up'], kb['our'], kb['xlsx'])
        print(f"== {kb['name']} ==")
        print(f"   약어 {len(rows)}개 | 트리거 글쇠 {len(trig)} | 된소리/이중모음 Shift {len(occ)} | "
              f"교차검증(XLSX 자모쌍) OK")
        assert len(rows) == 70, f"{kb['id']}: 기대 70, 실제 {len(rows)}"
        if not verify_only:
            nsym, npair = emit_dic(kb['id'], kb['name'], rows, sym_layer, trig, kb['dic'])
            print(f"   → {os.path.relpath(kb['dic'], REPO)} (기호 {nsym} + 약어 {npair} = 단일 사전)")
        total += len(rows)
    print(f"총 {total} 약어 ({'검증만' if verify_only else '생성 완료'}).")

if __name__ == '__main__':
    main()
