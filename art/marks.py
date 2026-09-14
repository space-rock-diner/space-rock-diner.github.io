#!/usr/bin/env python3
"""サイトの絵 (UFO / ベース / カレー) を SVG 文字列で返す。build.py が読み込んでページに埋め込む。

3 つの画風 (STYLES) があり、どれを使うかは data/site.yaml の mark_style。
ベースはリッケンバッカー 4003、カレーは黒い丸皿のあいがけスパイスカレーを参考に描いている。
"""
import re
from pathlib import Path

HERE = Path(__file__).parent


def _xf(path, fx, fy):
    toks = re.findall(r"[MCLQZ]|-?[\d.]+", path)
    out, nums = [], []
    for t in toks:
        if t.isalpha():
            out.append(t)
        else:
            nums.append(float(t))
            if len(nums) == 2:
                out.append(f"{fx(nums[0]):.2f} {fy(nums[1]):.2f}")
                nums = []
    return " ".join(out)


# ---- UFO ----
UFO_DOME = "M35 47 C35 28 65 28 65 47 Z"
UFO_BEAM = "M40 57 L26 92 L74 92 L60 57 Z"
UFO_LIGHTS = [(24, 52.5), (37, 55), (50, 56), (63, 55), (76, 52.5)]

# ---- ベース: リッケンバッカー 4003 (縦に描く。首は x=50、ヘッド上) ----
# 長いホーンは右 (= 横に構えたときの上側)、波形に尖る。左の短いホーンは丸い
RB_BODY = ("M54 100 C58 90 64 78 70 70 C72 67 74 64 75 63 C77 67 77 74 79 82 "
           "C81 90 88 100 89 116 C90 134 80 154 54 159 C32 162 16 150 13 130 "
           "C11 116 16 100 20 92 C22 88 24 86 26 86 C30 88 36 98 46 102 Z")
RB_BIND = "translate(51 114) scale(.93) translate(-51 -114)"     # 白い縁取り = ボディを少し縮めた線
RB_GUARD_UP = "M47 102 C52 101 58 96 64 88 C68 96 70 106 69 117 L41 119 C40 110 42 104 47 102 Z"
RB_GUARD_LO = "M30 121 C37 117 63 115 72 120 C76 132 70 146 60 152 C50 154 40 151 34 145 C28 137 27 127 30 121 Z"
RB_HEAD = "M46 26 L42 10 C41 4 44 1 49 1.5 C53 2 55 6 58 4 C61 2 64 3 63 8 L55 26 Z"
RB_TUNERS = [(37.5, 9), (39, 18.5), (65.5, 9), (62.5, 18.5)]      # 2 + 2
RB_STRINGS = [48.2, 49.4, 50.6, 51.8]
RB_NE = 101
RB_NECK_PU = 109
RB_BRIDGE = (126, 138)        # ブリッジ側ピックアップの金属カバー
RB_TAIL = 149
RB_INLAYS = [36, 48, 58, 67, 75, 83, 90]
BASS_FIT = "translate(50 50) rotate(34) scale(.56) translate(-51 -81)"

# ---- カレー: 黒い丸皿、真ん中にご飯、左右にあいがけ、彩りの野菜 ----
PLATE = 'cx="50" cy="64" rx="47" ry="19"'
PLATE_IN = 'cx="50" cy="63" rx="40" ry="14.5"'
RICE = "M35 61 C33 47 44 40 53 41.5 C63 43 69 51 67 60 C61 67 41 68 35 61 Z"
CURRY_L = "M9 66 C9 57 21 53 34 56 C35 61 38 65 45 68 C40 77 17 78 9 66 Z"
CURRY_R = "M65 58 C74 52 91 55 91 65 C90 75 71 78 56 71 C62 67 66 63 65 58 Z"
CURRY_STEAM = ["M36 32 C31 26 41 22 36 14", "M50 34 C45 28 55 24 50 16", "M64 32 C59 26 69 22 64 14"]
CHICKEN = [(18, 64, 4.2, 3.2), (28, 69, 3.8, 2.8), (21, 71.5, 3, 2.3)]
KEEMA_DOTS = [(71, 62), (77, 60), (83, 63), (74, 68), (80, 69), (86, 67), (68, 66), (78, 64.5)]

INK = "#1d2b3a"


def j(items):
    return "".join(items)


def ufo(style):
    if style == "line":
        c = "var(--c1)"
        return f'''<g fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" transform="rotate(-10 50 50)">
  <path d="{UFO_BEAM}" stroke-dasharray="2 5" opacity=".6"/>
  <path d="{UFO_DOME}"/>
  <path d="M42 38 C44 34 48 33 51 33" stroke-width="2"/>
  <ellipse cx="50" cy="50" rx="36" ry="9"/>
  {j(f'<circle cx="{x}" cy="{y}" r="2" fill="{c}" stroke="none"/>' for x, y in UFO_LIGHTS)}
</g>'''
    if style == "sticker":
        return f'''<g transform="rotate(-10 50 50)">
  <path d="{UFO_BEAM}" fill="#ffe9a8" opacity=".85"/>
  <g stroke="#fff" stroke-width="6" stroke-linejoin="round" paint-order="stroke">
    <path d="{UFO_DOME}" fill="#8fd6e8"/>
    <ellipse cx="50" cy="50" rx="36" ry="9.5" fill="#c9ced6"/>
  </g>
  <path d="{UFO_DOME}" fill="#8fd6e8" stroke="{INK}" stroke-width="2.4"/>
  <path d="M42 39 C44 35 48 34 51 34" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>
  <ellipse cx="50" cy="50" rx="36" ry="9.5" fill="#c9ced6" stroke="{INK}" stroke-width="2.4"/>
  <ellipse cx="50" cy="47.5" rx="26" ry="4" fill="#e7eaee"/>
  {j(f'<circle cx="{x}" cy="{y}" r="2.4" fill="#ffcf3f" stroke="{INK}" stroke-width="1.2"/>' for x, y in UFO_LIGHTS)}
</g>'''
    c = "#5ff2ff"
    return f'''<g fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowC)" transform="rotate(-10 50 50)">
  <path d="{UFO_DOME}"/>
  <ellipse cx="50" cy="50" rx="36" ry="9"/>
  <path d="M38 62 L30 84 M50 63 L50 88 M62 62 L70 84" stroke-width="2.2" opacity=".7"/>
  {j(f'<circle cx="{x}" cy="{y}" r="1.6" fill="{c}"/>' for x, y in UFO_LIGHTS)}
</g>'''


def bass(style):
    T = RB_TUNERS
    b0, b1 = RB_BRIDGE
    strings = lambda col, w: (j(f'<path d="M{x} 26 L{x} {b0}" stroke="{col}" stroke-width="{w}"/>' for x in RB_STRINGS)
                              + j(f'<path d="M{x} {b1} L{x} {RB_TAIL-2}" stroke="{col}" stroke-width="{w}"/>' for x in RB_STRINGS))
    if style in ("line", "neon"):
        c = "var(--c2)" if style == "line" else "#ff4fb8"
        flt = ' filter="url(#glowM)"' if style == "neon" else ""
        return f'''<g transform="{BASS_FIT}"><g fill="none" stroke="{c}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round"{flt}>
  <path d="{RB_HEAD}"/>
  {j(f'<circle cx="{x}" cy="{y}" r="2.8" fill="{c}" stroke="none"/>' for x, y in T)}
  <path d="M46 26 L46 {RB_NE} M54 26 L54 {RB_NE}"/>
  <path d="{RB_BODY}"/>
  <path d="{RB_BODY}" transform="{RB_BIND}" stroke-width="1.6" opacity=".55"/>
  <path d="{RB_GUARD_LO}" stroke-width="2.4" opacity=".8"/>
  <rect x="38" y="{b0}" width="25" height="{b1-b0}" rx="5" stroke-width="3.4"/>
  <path d="M45 {RB_TAIL} L57 {RB_TAIL}" stroke-width="4.2"/>
  <g stroke-width="1.1">{strings(c, 1.1)}</g>
</g></g>'''
    # sticker: Fireglo (赤のサンバースト) + 白い縁取り + 2 段の白いピックガード + 金属のブリッジカバー
    return f'''<g transform="{BASS_FIT}">
  <defs>
    <radialGradient id="fireglo" cx="50%" cy="66%" r="60%">
      <stop offset="0" stop-color="#ff7043"/><stop offset=".5" stop-color="#d7261b"/><stop offset="1" stop-color="#5e0c0a"/>
    </radialGradient>
    <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f7f9fa"/><stop offset=".5" stop-color="#a7b0b9"/><stop offset="1" stop-color="#e6e9ec"/>
    </linearGradient>
    <linearGradient id="maple" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#e9c48c"/><stop offset="1" stop-color="#c9955a"/>
    </linearGradient>
  </defs>
  <g stroke="#fff" stroke-width="11" stroke-linejoin="round" paint-order="stroke">
    <path d="{RB_HEAD}" fill="#e9c48c"/>
    <rect x="45.5" y="22" width="9" height="{RB_NE-18}" fill="#e9c48c"/>
    <path d="{RB_BODY}" fill="#b81d16"/>
    {j(f'<circle cx="{x}" cy="{y}" r="3.6" fill="#d9dde1"/>' for x, y in T)}
  </g>
  {j(f'<path d="M{x} {y} L{50 + (x-50)*.45} {y}" stroke="{INK}" stroke-width="2.6"/><ellipse cx="{x}" cy="{y}" rx="3.6" ry="2.6" fill="url(#chrome)" stroke="{INK}" stroke-width="1.5"/>' for x, y in T)}
  <path d="{RB_HEAD}" fill="url(#maple)" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M48.5 14 L52.5 14 L53.5 21 L47.5 21 Z" fill="#1a1a1a"/>
  {j(f'<circle cx="{50 + (x-50)*.55}" cy="{y}" r="1.3" fill="#8b949c"/>' for x, y in T)}
  <path d="{RB_BODY}" fill="url(#fireglo)" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="{RB_BODY}" transform="{RB_BIND}" fill="none" stroke="#fdf6ea" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="{RB_GUARD_LO}" fill="#fbf8f2" stroke="#cbc3b4" stroke-width="1.2"/>
  <path d="{RB_GUARD_UP}" fill="#fffdf9" stroke="#b9b0a0" stroke-width="1.4"/>
  <rect x="45.5" y="22" width="9" height="{RB_NE-20}" fill="url(#maple)" stroke="{INK}" stroke-width="1.6"/>
  <rect x="46.8" y="24" width="6.4" height="{RB_NE-22}" fill="#3b2416"/>
  <path d="M46.8 24 L46.8 {RB_NE+2} M53.2 24 L53.2 {RB_NE+2}" stroke="#fdf6ea" stroke-width=".9"/>
  {j(f'<path d="M46.8 {y+2.6} L53.2 {y+2.6} L46.8 {y-3.2} Z" fill="#f4efe6"/>' for y in RB_INLAYS)}
  <rect x="42" y="{RB_NECK_PU-3.5}" width="16" height="7" rx="1.8" fill="url(#chrome)" stroke="{INK}" stroke-width="1.4"/>
  {strings("#eef1f3", .75)}
  <rect x="37.5" y="{b0}" width="26" height="{b1-b0}" rx="5.5" fill="url(#chrome)" stroke="{INK}" stroke-width="1.8"/>
  <path d="M41 {b0+3} L60 {b0+3}" stroke="#fff" stroke-width="1.4" stroke-linecap="round" opacity=".9"/>
  <path d="M44.5 {RB_TAIL-3.5} L57.5 {RB_TAIL-3.5} L55.5 {RB_TAIL+4.5} L46.5 {RB_TAIL+4.5} Z" fill="url(#chrome)" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>
</g>'''


def curry(style):
    if style in ("line", "neon"):
        c = "var(--c3)" if style == "line" else "#ffb627"
        flt = ' filter="url(#glowA)"' if style == "neon" else ""
        paper = "var(--paper, #fffdf7)" if style == "line" else "#14101f"
        return f'''<g fill="{paper}" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"{flt}>
  {j(f'<path d="{p}" fill="none" stroke-width="2.4" opacity=".75"/>' for p in CURRY_STEAM)}
  <ellipse {PLATE}/>
  <ellipse {PLATE_IN} fill="none" stroke-width="1.6" opacity=".5"/>
  <path d="{CURRY_L}"/>
  <path d="{CURRY_R}"/>
  {j(f'<circle cx="{x}" cy="{y}" r="1.3" fill="{c}" stroke="none"/>' for x, y in KEEMA_DOTS[:6])}
  {j(f'<ellipse cx="{x}" cy="{y}" rx="{rx*.8}" ry="{ry*.8}" stroke-width="1.8"/>' for x, y, rx, ry in CHICKEN[:2])}
  <path d="{RICE}"/>
  <path d="M55 45 C58 40 64 40 66 43 C63 47.5 58 48 55 45 Z" stroke-width="2"/>
  <path d="M40 50 L46 47.5 M41 53.5 L47 50.5" stroke-width="1.8"/>
</g>'''
    return f'''<g>
  <defs>
    <radialGradient id="roux" cx="45%" cy="40%" r="70%">
      <stop offset="0" stop-color="#b5601f"/><stop offset=".7" stop-color="#8a3f12"/><stop offset="1" stop-color="#5e2a0c"/>
    </radialGradient>
    <radialGradient id="keema" cx="50%" cy="40%" r="70%">
      <stop offset="0" stop-color="#a3451a"/><stop offset="1" stop-color="#5a200b"/>
    </radialGradient>
    <linearGradient id="rice" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#fbf5e8"/><stop offset="1" stop-color="#e8dcc2"/>
    </linearGradient>
  </defs>
  {j(f'<path d="{p}" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".95"/>' for p in CURRY_STEAM)}
  <ellipse {PLATE} fill="#2b2b2e" stroke="#fff" stroke-width="6"/>
  <ellipse {PLATE} fill="#2b2b2e" stroke="{INK}" stroke-width="2.4"/>
  <ellipse {PLATE_IN} fill="#1f1f22"/>
  <path d="M14 58 C30 50 70 49 86 57" fill="none" stroke="#4a4a50" stroke-width="1.6" stroke-linecap="round"/>
  <path d="{CURRY_L}" fill="url(#roux)" stroke="#e08a2e" stroke-width="2.2" stroke-linejoin="round"/>
  {j(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#d9a066" stroke="#7a3a10" stroke-width=".9"/>' for x, y, rx, ry in CHICKEN)}
  <path d="M13 61 C17 58 23 57 28 58" fill="none" stroke="#e9a35a" stroke-width="1.8" stroke-linecap="round" opacity=".9"/>
  <path d="{CURRY_R}" fill="url(#keema)" stroke="#d4581f" stroke-width="2.2" stroke-linejoin="round"/>
  {j(f'<circle cx="{x}" cy="{y}" r="1.5" fill="#3f1506" opacity=".8"/>' for x, y in KEEMA_DOTS)}
  <path d="M72 58 C77 56.5 83 57 87 59.5" fill="none" stroke="#d98a4e" stroke-width="1.6" stroke-linecap="round" opacity=".9"/>
  <path d="{RICE}" fill="url(#rice)" stroke="#d9ccb0" stroke-width="1.2"/>
  <circle cx="49" cy="44.5" r="1.3" fill="#f2b705"/><circle cx="52.5" cy="43.5" r="1.1" fill="#e89c00"/><circle cx="50.5" cy="47" r="1" fill="#f2b705"/>
  <path d="M38 50 L45 47 M39 53 L46 49.5 M41 55.5 L47 52" stroke="#ff7417" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M55 45 C58 40 64 40 66 43 C63 47.5 58 48 55 45 Z" fill="#4caf50" stroke="#2e7d32" stroke-width=".9"/>
  <path d="M59 47 C62 45 66 46 68 48 C65 51 61 50.5 59 47 Z" fill="#7cc242" stroke="#2e7d32" stroke-width=".9"/>
  <path d="M58 58 C62 51 68 51 69 55 L66 60 Z" fill="#f59e0b" stroke="#2f6b2a" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M30 56 C33 53 37 53 38 55.5 C35 58 32 58.5 30 56 Z" fill="#e53935" stroke="#9b1c1c" stroke-width=".8"/>
</g>'''


def glow(id_):
    return (f'<filter id="{id_}" x="-40%" y="-40%" width="180%" height="180%">'
            '<feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="b1"/>'
            '<feGaussianBlur in="SourceGraphic" stdDeviation="6" result="b2"/>'
            '<feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def mark(style):
    W, H = 360, 120
    icons = [ufo(style), bass(style), curry(style)]
    defs, bg, wrap = "", "", ""
    if style == "line":
        wrap = 'style="--c1:#1f7a70;--c2:#c2410c;--c3:#d9731a"'
        groups = j(f'<g transform="translate({10 + i*118} 10)">{g}</g>' for i, g in enumerate(icons))
    elif style == "sticker":
        cols = ["#1d3557", "#2a9d8f", "#e5b85c"]
        stars = j(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".85"/>'
                  for x, y, r in [(22, 28, 1.4), (78, 20, 1.1), (86, 72, 1.3), (16, 70, 1)])
        defs = '<clipPath id="circ"><circle cx="50" cy="50" r="62"/></clipPath>'
        bg = j(f'<g transform="translate({10 + i*118} 6)"><circle cx="52" cy="56" r="50" fill="{INK}"/>'
               f'<circle cx="49" cy="53" r="50" fill="{cols[i]}"/>{stars if i == 0 else ""}</g>' for i in range(3))
        groups = j(f'<g transform="translate({10 + i*118} 6)"><g transform="translate(49 53) scale({1.0 if i == 1 else .8}) translate(-50 -50)">'
                   f'<g clip-path="url(#circ)">{g}</g></g></g>' for i, g in enumerate(icons))
    else:
        defs = glow("glowC") + glow("glowM") + glow("glowA")
        bg = ('<rect x="2" y="2" width="356" height="116" rx="58" fill="#14101f"/>'
              '<rect x="8" y="8" width="344" height="104" rx="52" fill="none" stroke="#2c2540" stroke-width="2"/>'
              + j(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{o}"/>' for x, y, r, o in
                  [(40, 30, 1, .7), (120, 18, .8, .5), (205, 100, 1, .6), (300, 24, .9, .6), (330, 92, .7, .5), (70, 96, .8, .4)]))
        groups = j(f'<g transform="translate({10 + i*118} 10)">{g}</g>' for i, g in enumerate(icons))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="UFO とベースとカレー" {wrap}><defs>{defs}</defs>{bg}{groups}</svg>')


STYLES = [("line", "A. モノライン", "線 1 本で描く。今のサイトの軽さに合わせた、いちばん静かな案。"),
          ("sticker", "B. レトロ・ステッカー", "70 年代スペースエイジのワッペン風。白フチと影で、ラップトップに貼りたくなる方向。"),
          ("neon", "C. ネオンサイン", "夜の食堂の看板。暗い背景に光る管で、ヘッダーの主役になる案。")]



def scoped(svg: str, prefix: str) -> str:
    """SVG 内の id と url(#id) に接頭辞を付ける。1 ページに同じ絵を何枚も埋め込むと id が重複し、
    非表示の SVG にある定義を参照した絵が描かれなくなるため。"""
    for i in set(re.findall(r'id="([^"]+)"', svg)):
        svg = svg.replace(f'id="{i}"', f'id="{prefix}-{i}"').replace(f"url(#{i})", f"url(#{prefix}-{i})")
    return svg


ICONS = {"ufo": ufo, "bass": bass, "curry": curry}
STICKER_BG = {"ufo": "#1d3557", "bass": "#2a9d8f", "curry": "#e5b85c"}
LINE_VARS = 'style="--c1:#1f7a70;--c2:#c2410c;--c3:#d9731a"'


def _frame(style: str, inner: str, bg_color: str, defs: str = "") -> str:
    if style == "sticker":
        return (f'<defs>{defs}</defs><circle cx="52" cy="53" r="46" fill="{INK}"/>'
                f'<circle cx="49" cy="50" r="46" fill="{bg_color}"/>{inner}')
    if style == "neon":
        return (f'<defs>{glow("glowC")}{glow("glowM")}{glow("glowA")}{glow("glowL")}{defs}</defs>'
                f'<rect x="2" y="2" width="96" height="96" rx="22" fill="#14101f"/>{inner}')
    return f"<defs>{defs}</defs>{inner}"


def icon(style: str, name: str) -> str:
    """1 つだけの絵 (100x100、装飾扱い)。お便りの選択肢や切手に使う。"""
    g = ICONS[name](style)
    if style == "sticker":
        s = (1.0 if name == "bass" else .8) * .92
        inner = f'<g transform="translate(49 50) scale({s}) translate(-50 -50)"><g clip-path="url(#circ)">{g}</g></g>'
        body = _frame(style, inner, STICKER_BG[name], '<clipPath id="circ"><circle cx="50" cy="50" r="62"/></clipPath>')
    elif style == "neon":
        body = _frame(style, f'<g transform="translate(50 50) scale(.86) translate(-50 -50)">{g}</g>', "")
    else:
        body = _frame(style, g, "")
    wrap = LINE_VARS if style == "line" else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" aria-hidden="true" {wrap}>{body}</svg>'

