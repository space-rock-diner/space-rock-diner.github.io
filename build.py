#!/usr/bin/env python3
"""data/ から公式サイト (docs/) を生成する静的サイトビルダー。

生成物:
    docs/index.html            トップ (聴く / この番組 / 出演 / 最新の回 / これまでの回 / お便り)
    docs/ep/<番号>/index.html  回ごとのページ (紹介文 / 聴く / この回に出てきたもの / その回へのお便り / 前後の回)
    docs/ep/index.html         すべての回 (年ごと)。トップからのリンクは回がトップに入りきらなくなってから出る
    docs/favicon.svg ほか      タブの絵と、static/ から写す画像 (SNS のカード・ホーム画面のアイコン)

使い方:
    python3 build.py          # docs/ を再生成 (data から消えた回のページも消す)
    python3 build.py --check  # 生成物が data と同期しているか検査 (CI / 手元確認用)

設計 (DESIGN.md 参照): 外部依存は PyYAML のみ、テンプレートは本 file 内に持つ。
絵は art/marks.py が SVG 文字列で返し、ここでページに埋め込む (外部ファイルを読み込まない)。
配信先の紹介文には過去に `/#ep<番号>` の形でリンクを書いたので、トップはその形を回のページへ転送する。
公開ページの文面を変えるときは所有者の文体運用に従う。
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "art"))
import marks  # noqa: E402

SITE_NAME = "オダキンカワヤンの宇宙ロック食堂"

PLATFORMS = [
    ("listen", "LISTEN"),
    ("spotify", "Spotify"),
    ("apple", "Apple Podcasts"),
    ("amazon", "Amazon Music"),
    ("youtube", "YouTube"),
]

# お便りの切手に出す絵 (開くたびにどれか 1 つ)
STAMP_ART = ["ufo", "bass", "curry"]

# 手で置く静的ファイル (static/ → docs/ にそのまま写す)。カバー画像は番組のアートワークを縮めたもの
STATIC = ROOT / "static"
OG_IMAGE = "artwork-1200.jpg"   # SNS のカード (og:image)

# トップの「これまでの回」で見せる数。これより多くなったら (= 回が増えたら自動で)、その下に「すべての回」ページへのリンクを出す
PAST_SHOWN = 5

STYLE = """:root {
  --bg: #faf6ec;
  --bg2: #f1e9d6;
  --text: #33302b;
  --dim: #6e6959;         /* 背景のいちばん濃いところでも 4.5:1 (WCAG AA、小さい字) */
  --dim-strong: #5c5749;
  --accent: #d9731a;
  --accent-ink: #b4540f;
  --accent2: #1b6d64;     /* リンク色。同上 */
  --line: #e0d7c0;
  --card: #fffdf7;
  --paper: #fffdf7;
  --air1: #d9731a;
  --air2: #1f7a70;
  --danger: #b42318;
  --ease: cubic-bezier(.2, .8, .2, 1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%);
  color: var(--text);
  font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Noto Sans JP", sans-serif;
  line-height: 1.9;
  min-height: 100vh;
}
main { max-width: 680px; margin: 0 auto; padding: 4rem 1.5rem 6rem; }
header { text-align: center; margin-bottom: 4rem; }
.mark { display: flex; justify-content: center; }
.mark svg { width: min(340px, 82vw); height: auto; }
h1 { font-size: 1.9rem; font-weight: 700; letter-spacing: .12em; margin-top: .6rem; }
.tagline { color: var(--accent-ink); margin-top: .8rem; letter-spacing: .18em; font-size: .95rem; }
section { margin-top: 3.5rem; }
h2 {
  font-size: 1.05rem; letter-spacing: .3em; color: var(--accent2);
  border-bottom: 1px solid var(--line); padding-bottom: .5rem; margin-bottom: 1.4rem;
  font-weight: 600;
}
blockquote.intro {
  border-left: 3px solid var(--accent); padding: .2rem 0 .2rem 1.2rem;
  color: var(--text); font-size: .98rem;
}
blockquote.intro p + p { margin-top: 1em; }
.hosts { display: grid; gap: 1rem; grid-template-columns: 1fr 1fr; }
@media (max-width: 520px) { .hosts { grid-template-columns: 1fr; } }
.host { border: 1px solid var(--line); border-radius: 10px; padding: 1.1rem 1.3rem; background: var(--card); box-shadow: 0 1px 3px rgba(80,60,20,.06); }
.host b { color: var(--accent-ink); font-size: 1.1rem; letter-spacing: .08em; }
.host p { color: var(--dim); font-size: .92rem; margin-top: .3rem; }
.episode { border-bottom: 1px dashed var(--line); padding: 1.2rem 0; }
.episode:last-child { border-bottom: none; }
.ep-desc { color: var(--text); font-size: .95rem; }
.empty { color: var(--dim); text-align: center; padding: 1.5rem 0; letter-spacing: .1em; }
a { color: var(--accent2); text-decoration: none; }
a:hover { text-decoration: underline; }
footer { text-align: center; color: var(--dim); font-size: .82rem; margin-top: 5rem; letter-spacing: .1em; }
.credit { font-size: .74rem; letter-spacing: .2em; }

/* ---- お便り: 航空便のはがき ---- */
.lead { font-size: .98rem; margin-bottom: 1.6rem; }
.postcard {
  --gap: clamp(1.1rem, 4vw, 1.9rem);
  padding: 9px; border-radius: 18px;
  background: repeating-linear-gradient(135deg,
    var(--air1) 0 16px, var(--paper) 16px 24px, var(--air2) 24px 40px, var(--paper) 40px 48px);
  box-shadow: 0 1px 2px rgba(80,60,20,.08), 0 12px 32px -12px rgba(80,60,20,.25);
}
.postcard-inner {
  position: relative; background: var(--paper); border-radius: 11px;
  padding: var(--gap); display: grid; gap: 1.35rem;
  grid-template-columns: minmax(0, 1fr);   /* 中身 (確認欄など) の最小幅で、はがきの外へ押し広げない */
}
.postcard-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.address { padding-top: .3rem; line-height: 1.5; }
.address small { display: block; font-size: .7rem; letter-spacing: .3em; color: var(--dim-strong); }
.address b { display: block; font-size: clamp(1.05rem, 3.6vw, 1.25rem); letter-spacing: .1em; margin-top: .25rem; }
.address span { display: block; font-size: .88rem; letter-spacing: .12em; margin-top: .1rem; }
.address span::after { content: "行"; margin-left: .6em; }
.stamp-wrap { position: relative; flex: none; }
.stamp {
  position: relative;
  width: 84px; height: 98px; padding: 7px; rotate: 4deg;
  background: radial-gradient(circle, transparent 3.2px, #fff 3.7px) -4.5px -4.5px / 9px 9px;
  filter: drop-shadow(0 1px 1.5px rgba(60,40,10,.25));
}
.stamp-face {
  height: 100%; background: #f6efe0; display: grid; place-items: center;
  grid-template-rows: 1fr auto; padding: 6px 4px 3px;
}
.stamp-art { display: none; width: 58px; }
.stamp-art:first-child { display: block; }
.stamp-art svg { width: 100%; height: auto; display: block; }
.stamp-price { font-size: .5rem; letter-spacing: .02em; color: var(--dim-strong); line-height: 1.2; white-space: nowrap; }
.postmark {
  position: absolute; top: 1.2rem; right: 3.9rem;
  width: 78px; height: 78px; border-radius: 50%; rotate: -16deg; pointer-events: none;
  border: 1.5px solid color-mix(in oklab, var(--accent2) 55%, transparent);
  display: grid; place-items: center; text-align: center;
  font-size: .55rem; line-height: 1.35; letter-spacing: .08em;
  color: color-mix(in oklab, var(--accent2) 75%, transparent);
}
.postmark::before {
  content: ""; position: absolute; inset: 22% -58% 22% auto; width: 58%;
  background: repeating-linear-gradient(180deg, transparent 0 5px,
    color-mix(in oklab, var(--accent2) 45%, transparent) 5px 6.5px);
  border-radius: 40%;
}
.field > label {
  font-weight: 700; font-size: .95rem; letter-spacing: .08em; margin-bottom: .55rem; display: block;
}
.field { display: grid; }
.opt { font-weight: 400; font-size: .76rem; color: var(--dim-strong); margin-left: .5em; letter-spacing: .04em; }
.postcard input[type="text"], .postcard textarea {
  font: inherit; color: var(--text); width: 100%;
  border: 1.5px solid var(--line); border-radius: 10px; background: #fff;
  padding: .6rem .85rem; transition: border-color .2s, box-shadow .2s;
}
.postcard textarea {
  line-height: 2; min-height: calc(7 * 2em + 1.3rem); resize: none; overflow: hidden; field-sizing: content;
  background: #fff linear-gradient(transparent calc(2em - 1px), #efe7d4 0) 0 .6rem / 100% 2em local;
}
.postcard input::placeholder, .postcard textarea::placeholder { color: #a9a393; }
.postcard input[type="text"]:focus-visible, .postcard textarea:focus-visible {
  outline: none; border-color: var(--accent2);
  box-shadow: 0 0 0 4px color-mix(in oklab, var(--accent2) 20%, transparent);
}
.postcard [aria-invalid="true"] { border-color: var(--danger); }
.hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
#otayori-turnstile { min-height: 65px; }
.field-foot { display: grid; gap: .25rem; margin-top: .35rem; font-size: .78rem; color: var(--dim-strong); }
#otayori-hint { line-height: 1.75; word-break: auto-phrase; }
#otayori-count { justify-self: end; white-space: nowrap; font-variant-numeric: tabular-nums; }
#otayori-count.low { color: var(--danger); font-weight: 700; }
.field-error { color: var(--danger); font-size: .82rem; margin-top: .3rem; }
.actions { display: flex; align-items: center; justify-content: flex-end; gap: 1rem; flex-wrap: wrap; }
.send {
  font: inherit; font-weight: 700; letter-spacing: .12em; color: #fff; cursor: pointer;
  display: inline-flex; align-items: center; gap: .6rem; min-height: 3rem; padding: .6rem 1.5rem .6rem 1.35rem;
  border: 0; border-radius: 999px; background: var(--accent-ink);
  box-shadow: 0 2px 0 #7c3a0a, 0 8px 18px -8px rgba(180,84,15,.7);
  transition: transform .15s var(--ease), box-shadow .15s var(--ease), background-color .2s;
}
.send svg { width: 1.2rem; height: 1.2rem; transition: transform .3s var(--ease); }
.send:hover { background: #9f4a0c; }
.send:hover svg { transform: translate(3px, -3px) rotate(-8deg); }
.send:active { transform: translateY(2px); box-shadow: 0 0 0 #7c3a0a, 0 4px 10px -6px rgba(180,84,15,.7); }
.send:focus-visible { outline: 3px solid var(--accent2); outline-offset: 3px; }
.send:disabled { background: #b9b2a2; box-shadow: none; cursor: not-allowed; }
.status { font-size: .86rem; color: var(--dim-strong); }
.status:empty { display: none; }
.postcard.sent .status { color: var(--accent2); font-weight: 700; }
.status code { font-family: inherit; color: var(--text); background: #f3ecdc; padding: .05rem .4rem; border-radius: 6px; user-select: all; }
@media (max-width: 480px) {
  main { padding-left: 1rem; padding-right: 1rem; }
  /* 確認欄 (Turnstile) の flexible は幅 300px 以上が要る。375px の画面でもそれが入る余白にする */
  .postcard { --gap: clamp(.75rem, 3.2vw, 1.9rem); }
  .stamp { width: 66px; height: 78px; }
  .stamp-art { width: 44px; }
  .postmark { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; }
}

/* ---- 見出しの改行 (日本語は文節で、行の長さは揃える) ---- */
h1, .tagline, .ep-h1, .ep-title, .past a { word-break: auto-phrase; text-wrap: balance; }
.lead { word-break: auto-phrase; }   /* <br> で切ってある短い文。balance すると短い行が生まれる。長い本文は文節で切らない (行末がそろわなくなる) */
p { text-wrap: pretty; }
a:focus-visible { outline: 3px solid var(--accent2); outline-offset: 2px; border-radius: 4px; }

/* ---- 聴く (配信先のボタン) ---- */
.listen { margin-top: 1.8rem; display: grid; justify-items: center; gap: .6rem; }
.listen-label { font-size: .8rem; letter-spacing: .3em; color: var(--dim-strong); }
.chips { display: flex; flex-wrap: wrap; justify-content: center; gap: .6rem; }
.chip {
  display: inline-flex; align-items: center; min-height: 44px; padding: .4rem 1.2rem;
  border: 1.5px solid var(--accent2); border-radius: 999px; background: var(--card);
  color: var(--accent2); font-size: .92rem; font-weight: 700; letter-spacing: .04em;
  transition: background-color .2s, color .2s;
}
.chip:hover { background: var(--accent2); color: #fff; text-decoration: none; }
.soon { font-size: .8rem; color: var(--dim); }
.ep-page .listen { justify-items: start; }
.ep-page .chips { justify-content: flex-start; }

/* ---- 最新の回・これまでの回 ---- */
.ep-date { color: var(--dim); font-size: .85rem; letter-spacing: .08em; font-variant-numeric: tabular-nums; }
h3.ep-title { font-size: 1.15rem; font-weight: 700; line-height: 1.6; margin: .2rem 0 .5rem; }
h3.ep-title a { color: inherit; }
.player { display: block; width: 100%; height: 178px; border: 0; margin-top: 1rem; border-radius: 12px; background: var(--card); }
.more { margin-top: .9rem; font-size: .92rem; }
.past { list-style: none; }
.past li { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; border-bottom: 1px dashed var(--line); }
.past li:last-child { border-bottom: none; }
.past a { flex: 1; padding: .7rem 0; font-size: .95rem; }
.past .ep-date { flex: none; }
.year-nav { display: flex; flex-wrap: wrap; gap: .4rem 1.1rem; margin: -.4rem 0 .6rem; font-size: .92rem; }
.year-nav a { display: inline-flex; align-items: center; min-height: 44px; }

/* ---- 回のページ ---- */
header.sub { margin-bottom: 2.5rem; }
header.sub a { display: inline-flex; align-items: center; gap: .9rem; color: var(--text); font-weight: 700; letter-spacing: .08em; line-height: 1.5; }
header.sub a:hover { text-decoration: none; }
header.sub svg { width: 110px; height: auto; flex: none; }
.ep-h1 { font-size: 1.45rem; line-height: 1.6; font-weight: 700; letter-spacing: .04em; margin: .3rem 0 1rem; }
.ep-page .ep-desc { font-size: 1rem; }
.refs-list { list-style: none; display: grid; gap: .5rem; font-size: .95rem; }
.refs-list li { padding-left: 1.1em; text-indent: -1.1em; }
.refs-list li::before { content: "・"; color: var(--dim); }
.ep-nav { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 3.5rem; font-size: .9rem; }
.ep-nav a { border: 1px solid var(--line); border-radius: 10px; padding: .8rem 1rem; background: var(--card); line-height: 1.6; }
.ep-nav a:hover { text-decoration: none; border-color: var(--accent2); }
.ep-nav small { display: block; color: var(--dim-strong); font-size: .76rem; letter-spacing: .1em; }
.ep-nav .next { grid-column: 2; text-align: right; }
.back { text-align: center; margin-top: 3rem; font-size: .9rem; }

/* ---- お便りの宛先 (回のページだけ) ---- */
fieldset.about { border: 0; display: grid; }
fieldset.about legend { font-weight: 700; font-size: .95rem; letter-spacing: .08em; margin-bottom: .55rem; }
.seg { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
.seg label {
  display: flex; align-items: center; justify-content: center; gap: .5rem; min-height: 44px; padding: .4rem .8rem;
  border: 1.5px solid var(--line); border-radius: 10px; background: #fff; cursor: pointer;
  font-size: .92rem; text-align: center; line-height: 1.4; transition: border-color .2s, background-color .2s;
}
.seg input { accent-color: var(--accent2); flex: none; }
.seg label:has(input:checked) { border-color: var(--accent2); background: color-mix(in oklab, var(--accent2) 8%, #fff); font-weight: 700; }
.seg label:has(input:focus-visible) { outline: 3px solid var(--accent2); outline-offset: 2px; }

@media (max-width: 480px) {
  .past li { flex-direction: column; gap: 0; }
  .past a { padding-bottom: 0; }
  .past .ep-date { padding-bottom: .6rem; }
  .ep-nav { grid-template-columns: 1fr; }
  .ep-nav .next { grid-column: 1; }
  .seg { grid-template-columns: 1fr; }
  .seg label { justify-content: flex-start; }
}
"""

SCRIPT = """(() => {
  const form = document.getElementById("otayori-form");
  const arts = form.querySelectorAll(".stamp-art");
  if (arts.length > 1) {
    const pick = Math.floor(Math.random() * arts.length);
    arts.forEach((el, i) => { el.style.display = i === pick ? "block" : "none"; });
  }
  const body = document.getElementById("otayori-body");
  const count = document.getElementById("otayori-count");
  const max = body.maxLength;
  const update = () => {
    const left = max - body.value.length;
    count.textContent = `あと ${left.toLocaleString("ja-JP")} 字`;
    count.classList.toggle("low", left < 1000);
    // 書いた分だけ欄を伸ばす (CSS の field-sizing が効かないブラウザ向け。効くブラウザでも害は無い)
    body.style.height = "auto";
    body.style.height = `${body.scrollHeight + 2}px`;
  };
  body.addEventListener("input", update);
  update();
  if (form.dataset.ready !== "1") return;
  const MESSAGES = {
    turnstile: "ロボットでない確認がまだのようです。確認の欄が済んでから、もう一度どうぞ。",
    too_long: "長すぎました。原稿用紙 50 枚分、20,000 字までにしてください。",
    empty: "ひとことだけでも書いてください。",
    other: "うまく送れませんでした。電波のいいところで、もう一度お願いします。",
  };
  const name = document.getElementById("otayori-name");
  const error = document.getElementById("otayori-error");
  const status = document.getElementById("otayori-status");
  const button = form.querySelector(".send");
  body.addEventListener("input", () => {
    if (body.value.trim()) { body.removeAttribute("aria-invalid"); error.hidden = true; }
  });
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!body.value.trim()) {
      body.setAttribute("aria-invalid", "true"); error.hidden = false; body.focus(); return;
    }
    button.disabled = true;
    status.textContent = "ポストに向かっています。";
    let out = {};
    try {
      const res = await fetch(form.action, {
        method: "POST", body: new FormData(form), headers: { accept: "application/json" },
      });
      out = await res.json().catch(() => ({}));
      if (!res.ok || !out.ok) throw new Error(out.error || String(res.status));
      form.classList.add("sent");
      status.textContent = "ポストに入りました。ありがとうございます。";
      body.value = ""; name.value = ""; update();
    } catch {
      form.classList.remove("sent");
      status.textContent = MESSAGES[out.error] || MESSAGES.other;
    } finally {
      button.disabled = false;
      // トークンは 1 回きりなので、送るたびに確認欄を新しくする
      if (window.turnstile && window.otayoriWidgetId !== undefined) window.turnstile.reset(window.otayoriWidgetId);
    }
  });
})();
"""

FOOTER = """  <footer>© 2026 オダキンカワヤンの宇宙ロック食堂<br><span class="credit">文責　クロード</span></footer>"""


def esc(s: str) -> str:
    # 属性値 context (href="...") にも入るので quote 2 種も escape する
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def load(name: str) -> dict:
    path = ROOT / "data" / name
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.exists() else {}


def art(style: str, key: str, uid: str) -> str:
    svg = marks.icon(style, key)
    return marks.scoped(svg, uid)


def ep_path(e: dict) -> str:
    return f"/ep/{int(e['number'])}/"


def archive_linked(episodes: list[dict]) -> bool:
    """「すべての回」ページへリンクするか = トップの「これまでの回」に入りきらなくなったか。ページ自体はいつも作る。"""
    return len(episodes) - 1 > PAST_SHOWN


def past_items(es: list[dict]) -> str:
    return "\n".join(f'      <li><a href="{ep_path(e)}">{esc(e["title"])}</a>'
                     f'<span class="ep-date">{ep_date(e)}</span></li>' for e in es)


def back_links(episodes: list[dict], on_archive: bool = False) -> str:
    """ページの下の戻り道。お便りはどのページからも 1 回で辿れるようにする。"""
    links = ['<a href="/">番組のトップへ</a>']
    if archive_linked(episodes) and not on_archive:
        links.append('<a href="/ep/">すべての回</a>')
    links.append('<a href="/#otayori">番組へのお便り</a>')
    return "　・　".join(links)


def render_archive(episodes: list[dict], style: str, base: str) -> str:
    """すべての回 (/ep/)。年ごとに見出しを立て、新しい順。年が 2 つ以上になったら上に年への飛び先を並べる。"""
    years: dict[str, list[dict]] = {}
    for e in episodes:
        years.setdefault(str(e.get("date", ""))[:4] or "—", []).append(e)
    nav = ""
    if len(years) > 1:
        nav = ('    <nav class="year-nav" aria-label="年">'
               + "".join(f'<a href="#y{y}">{y}年</a>' for y in years) + "</nav>\n")
    sections = "\n".join(
        f'  <section id="y{y}">\n    <h2>{y}年</h2>\n    <ol class="past">\n{past_items(es)}\n    </ol>\n  </section>'
        for y, es in years.items())
    title = f"すべての回（{len(episodes)} 回）"
    return (
        head(title=f"すべての回｜{SITE_NAME}", desc=f"{SITE_NAME}のすべての回", og_title=f"すべての回｜{SITE_NAME}",
             og_desc=f"{SITE_NAME}のすべての回", url=f"{base}ep/", og_type="website", base=base)
        + f"""<body>
<main>
  <header class="sub">
    <a href="/">{marks.scoped(marks.mark(style), "mark")}<span>オダキンカワヤンの<br>宇宙ロック食堂</span></a>
  </header>

  <h1 class="ep-h1">{title}</h1>
{nav}
{sections}

  <p class="back">{back_links(episodes, on_archive=True)}</p>

{FOOTER}
</main>
</body>
</html>
"""
    )


def ep_date(e: dict) -> str:
    """2026-09-23 → 2026年9月23日 (表示用)。"""
    d = str(e.get("date", ""))
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", d)
    return f"{m[1]}年{int(m[2])}月{int(m[3])}日" if m else d


def player(e: dict, site: dict) -> str:
    """LISTEN の埋め込みプレーヤー (LISTEN の oEmbed が返す形 = <回の URL>/player、高さ 178px)。
    ページを離れずに聴ける。site.yaml の listen_player が true のときだけ、LISTEN の URL がある回に出す。
    選べるのは色 (theme = auto / light / dark) だけで、プレーヤーには LISTEN の文字起こしの抜粋も出る。"""
    url = str((e.get("links") or {}).get("listen") or "")
    if site.get("listen_player") is not True or not re.fullmatch(r"https://listen\.style/p/[^/?#]+/[^/?#]+", url):
        return ""
    return (f'      <iframe class="player" src="{esc(url)}/player?theme=light" title="{esc(e["title"])}（LISTEN のプレーヤー）"'
            ' loading="lazy" scrolling="no"></iframe>\n')


def head(*, title: str, desc: str, og_title: str, og_desc: str, url: str, og_type: str, base: str,
         extra: str = "") -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(title)}</title>\n"
        f'<meta name="description" content="{esc(desc)}">\n'
        f'<link rel="canonical" href="{esc(url)}">\n'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
        f'<meta property="og:title" content="{esc(og_title)}">\n'
        f'<meta property="og:description" content="{esc(og_desc)}">\n'
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta property="og:url" content="{esc(url)}">\n'
        f'<meta property="og:site_name" content="{SITE_NAME}">\n'
        f'<meta property="og:image" content="{esc(base)}{OG_IMAGE}">\n'
        f'<meta property="og:image:alt" content="{SITE_NAME}のカバー画像">\n'
        '<meta name="twitter:card" content="summary">\n'
        f"{extra}"
        f"<style>\n{STYLE}</style>\n"
        "</head>\n"
    )


def show_links(episodes: list[dict], data: dict) -> dict[str, str]:
    # 番組ページの URL。show_links が無い配信先は、どれかの回にその配信先の URL があればそれを使う
    links: dict[str, str] = {}
    for e in episodes:
        for key, url in (e.get("links") or {}).items():
            links.setdefault(key, url)
    return {**links, **(data.get("show_links") or {})}


def listen_block(links: dict[str, str], label: str) -> str:
    """配信先のボタン。聴ける配信先だけをボタンにし、まだの配信先は 1 行の注記にまとめる
    (押せないものをボタンの形で並べない)。"""
    chips = "\n".join(f'        <a class="chip" href="{esc(links[k])}">{name}</a>'
                      for k, name in PLATFORMS if k in links)
    soon = "・".join(name for k, name in PLATFORMS if k not in links)
    return ('    <div class="listen">\n'
            f'      <span class="listen-label">{label}</span>\n'
            f'      <div class="chips">\n{chips}\n      </div>\n'
            + (f'      <span class="soon">{soon} は準備中</span>\n' if soon else "")
            + "    </div>")


def otayori_section(site: dict, style: str, ep: dict | None = None) -> str:
    """お便りのはがき。ep を渡すと宛先を 2 択で選べる (最初は「第N回について」)。
    「番組へ」を選ぶと回を決めずに届く = トップの欄と同じ。回の番号は name="episode" で受け口に渡る (番組へ = 空)。"""
    ot = site.get("otayori") or {}
    stamps = "\n".join(
        f'          <span class="stamp-art">{art(style, key, f"stamp-{key}")}</span>' for key in STAMP_ART
    )
    sitekey = str(ot.get("turnstile_sitekey") or "").strip()
    turnstile = ""
    if sitekey:
        # 明示描画: 描いた確認欄の ID を持っておき、送信のたびにその欄だけリセットする
        turnstile = (f'        <div id="otayori-turnstile" data-sitekey="{esc(sitekey)}"></div>\n'
                     '        <script>window.otayoriTurnstileReady = () => { const el = document.getElementById("otayori-turnstile");'
                     ' window.otayoriWidgetId = window.turnstile.render(el, { sitekey: el.dataset.sitekey, action: "otayori",'
                     ' theme: "light", size: el.clientWidth >= 300 ? "flexible" : "compact" }); };</script>\n'
                     '        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&amp;onload=otayoriTurnstileReady" async defer></script>\n')
    if ot.get("enabled") is True:
        form_attrs = 'data-ready="1" action="/api/otayori" method="post"'
        status, disabled = "", ""
    else:
        form_attrs, status, disabled = 'data-ready="0"', "ただいま準備中。もうすぐポストを置きます。", " disabled"
    about = ""
    if ep is not None:
        n = int(ep["number"])
        about = ('        <fieldset class="about">\n'
                 '          <legend>どれへのお便り？</legend>\n'
                 '          <div class="seg">\n'
                 f'            <label><input type="radio" name="episode" value="{n}" checked>第{n}回について</label>\n'
                 '            <label><input type="radio" name="episode" value="">番組へ（回は決めない）</label>\n'
                 '          </div>\n'
                 '        </fieldset>\n')
    return f"""  <section id="otayori" aria-labelledby="otayori-h">
    <h2 id="otayori-h">お便り</h2>
    <p class="lead">聞きたいこと、言いたいこと、どうでもいいこと。<br>ふたりで読んで、ふたりで考えます。</p>
    <form class="postcard" id="otayori-form" {form_attrs} novalidate>
      <div class="postcard-inner">
        <div class="postcard-head">
          <p class="address"><small>TO</small><b>宇宙ロック食堂</b><span>オダキン・カワヤン</span></p>
          <div class="stamp-wrap" aria-hidden="true">
            <div class="postmark">宇宙<br>ロック<br>食堂</div>
            <div class="stamp"><div class="stamp-face">
{stamps}
              <span class="stamp-price">ロック便</span>
            </div></div>
          </div>
        </div>
{about}        <div class="field">
          <label for="otayori-name">ラジオネーム<span class="opt">なくても大丈夫</span></label>
          <input type="text" id="otayori-name" name="radio_name" maxlength="40" autocomplete="off" placeholder="例：土星の輪でナンを焼く人">
        </div>
        <div class="field">
          <label for="otayori-body">お便り</label>
          <textarea id="otayori-body" name="body" required maxlength="20000" aria-describedby="otayori-hint otayori-count"></textarea>
          <p class="field-error" id="otayori-error" hidden>ひとことだけでも書いてください。</p>
          <div class="field-foot"><span id="otayori-count" aria-live="off">あと 20,000 字</span><p id="otayori-hint">本名や連絡先は書かなくて大丈夫です。<br>番組で読みあげることがあります。</p></div>
        </div>
        <div class="hp" aria-hidden="true"><label>空けておいてください<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
{turnstile}        <div class="actions">
          <p class="status" id="otayori-status" role="status">{status}</p>
          <button type="submit" class="send"{disabled}>ポストに入れる
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12 20 4l-4 16-4-6-8-2Z"/><path d="m12 14 8-10"/></svg>
          </button>
        </div>
      </div>
    </form>
  </section>"""


def render_index(episodes: list[dict], data: dict, site: dict, style: str, base: str) -> str:
    # 配信先の紹介文に書いた /#ep<番号> を、その回のページへ移す (描画の前に head で行う)
    nums = ",".join(str(int(e["number"])) for e in episodes)
    redirect = ("<script>(() => { const m = location.hash.match(/^#ep([0-9]+)$/);"
                f" if (m && [{nums}].includes(Number(m[1]))) location.replace(`/ep/${{m[1]}}/`); }})();</script>\n")

    if not episodes:
        latest_html = '    <p class="empty">ただいま仕込み中。</p>'
    else:
        e = episodes[0]
        latest_html = (
            f'    <article class="episode" id="ep{int(e["number"])}">\n'
            f'      <div class="ep-date">{ep_date(e)}</div>\n'
            f'      <h3 class="ep-title"><a href="{ep_path(e)}">{esc(e["title"])}</a></h3>\n'
            f'      <p class="ep-desc">{esc(e.get("description", ""))}</p>\n'
            + player(e, site)
            + f'      <p class="more"><a href="{ep_path(e)}">この回のページへ（出てきたもののリンク・この回へのお便り）</a></p>\n'
            + "    </article>"
        )

    # これまでの回: 新しい PAST_SHOWN 回だけ (最新の回のすぐ下に置き、回の一覧をひとかたまりにする)。
    # それより多ければ「すべての回」ページへのリンク = トップの長さは回が増えても変わらず、お便りの欄も沈まない
    past = episodes[1:]
    past_html = ""
    if past:
        past_html = ("\n\n  <section>\n"
                     "    <h2>これまでの回</h2>\n"
                     f'    <ol class="past">\n{past_items(past[:PAST_SHOWN])}\n    </ol>\n'
                     + (f'    <p class="more"><a href="/ep/">すべての回（{len(episodes)} 回）</a></p>\n'
                        if archive_linked(episodes) else "")
                     + "  </section>")

    return (
        head(title=SITE_NAME,
             desc="素粒子・宇宙・ロック・カレーのポッドキャスト。専門家に素人が聞き、素人に専門家が聞く。",
             og_title=SITE_NAME, og_desc="素粒子・宇宙・ロック・カレーのポッドキャスト",
             url=base, og_type="website", base=base, extra=redirect)
        + f"""<body>
<main>
  <header>
    <div class="mark">{marks.scoped(marks.mark(style), "mark")}</div>
    <h1>オダキンカワヤンの<br>宇宙ロック食堂</h1>
    <p class="tagline">素粒子・宇宙・ロック・カレーのポッドキャスト</p>
{listen_block(show_links(episodes, data), "聴く")}
  </header>

  <section>
    <h2>この番組</h2>
    <blockquote class="intro">
      <p>素粒子って何ですか？宇宙はどこまで続くんですか？<br>
      カレー屋でありベーシストでもあるカワヤンが、物理研究者のオダキンに聞きます。</p>
      <p>逆に、このベースラインの気持ちよさって何ですか？スパイスってなんであんなに合わさるんですか？<br>
      物理研究者のオダキンが、カワヤンに聞きます。</p>
      <p>専門家に素人が聞き、素人に専門家が聞く。<br>
      オダキンカワヤンの宇宙ロック食堂、はじまります。</p>
    </blockquote>
  </section>

  <section>
    <h2>出演</h2>
    <div class="hosts">
      <div class="host"><b>オダキン</b><p>素粒子・宇宙の物理研究者</p></div>
      <div class="host"><b>カワヤン</b><p>カレー屋、そしてベーシスト</p></div>
    </div>
  </section>

  <section>
    <h2>最新の回</h2>
{latest_html}
  </section>{past_html}

{otayori_section(site, style)}

{FOOTER}
</main>
<script>
{SCRIPT}</script>
</body>
</html>
"""
    )


def render_episode(i: int, episodes: list[dict], data: dict, site: dict, style: str, base: str) -> str:
    e = episodes[i]
    n = int(e["number"])
    newer = episodes[i - 1] if i > 0 else None
    older = episodes[i + 1] if i + 1 < len(episodes) else None
    # この回の URL がある配信先はその回へ、無い配信先は番組ページへ
    links = {**show_links(episodes, data), **(e.get("links") or {})}
    refs = e.get("references") or []
    refs_html = ""
    if refs:
        items = "\n".join(f'      <li><a href="{esc(r["url"])}">{esc(r["label"])}</a></li>' for r in refs)
        refs_html = ("\n\n  <section>\n"
                     "    <h2>この回に出てきたもの</h2>\n"
                     '    <ul class="refs-list">\n'
                     f"{items}\n"
                     "    </ul>\n"
                     "  </section>")
    nav = ""
    if older or newer:
        parts = []
        if older:
            parts.append(f'<a class="prev" href="{ep_path(older)}"><small>← 前の回</small>{esc(older["title"])}</a>')
        if newer:
            parts.append(f'<a class="next" href="{ep_path(newer)}"><small>次の回 →</small>{esc(newer["title"])}</a>')
        nav = f'\n\n  <nav class="ep-nav" aria-label="前後の回">{"".join(parts)}</nav>'
    desc = str(e.get("description", ""))
    return (
        head(title=f"{e['title']}｜{SITE_NAME}", desc=desc, og_title=str(e["title"]), og_desc=desc,
             url=f"{base}ep/{n}/", og_type="article", base=base)
        + f"""<body>
<main>
  <header class="sub">
    <a href="/">{marks.scoped(marks.mark(style), "mark")}<span>オダキンカワヤンの<br>宇宙ロック食堂</span></a>
  </header>

  <article class="ep-page">
    <div class="ep-date">{ep_date(e)}</div>
    <h1 class="ep-h1">{esc(e["title"])}</h1>
    <p class="ep-desc">{esc(desc)}</p>
{player(e, site)}{listen_block(links, "アプリで聴く")}
  </article>{refs_html}

{otayori_section(site, style, e)}{nav}

  <p class="back">{back_links(episodes)}</p>

{FOOTER}
</main>
<script>
{SCRIPT}</script>
</body>
</html>
"""
    )


def render() -> dict[Path, str | bytes]:
    """生成するファイルの path → 中身 (ページは str、static/ から写す画像は bytes)。"""
    data = load("episodes.yaml")
    site = load("site.yaml")
    style = site.get("mark_style") or "sticker"
    if style not in {k for k, _, _ in marks.STYLES}:
        raise SystemExit(f"❌ data/site.yaml の mark_style が不明: {style}")
    base = str(site.get("site_url") or "").strip()
    if not base.endswith("/"):
        raise SystemExit("❌ data/site.yaml の site_url が無いか、末尾が / でない")
    episodes = sorted(data.get("episodes") or [], key=lambda e: e.get("number", 0), reverse=True)
    nums = [int(e["number"]) for e in episodes]
    if len(set(nums)) != len(nums):
        raise SystemExit(f"❌ data/episodes.yaml に同じ number が 2 つある: {nums}")
    pages: dict[Path, str | bytes] = {DOCS / "index.html": render_index(episodes, data, site, style, base)}
    for i, e in enumerate(episodes):
        pages[DOCS / "ep" / str(int(e["number"])) / "index.html"] = render_episode(i, episodes, data, site, style, base)
    pages[DOCS / "ep" / "index.html"] = render_archive(episodes, style, base)
    # タブの小さな絵 = ヘッダーの 3 つの絵のうち UFO (小さくても形が分かる)
    pages[DOCS / "favicon.svg"] = marks.icon(style, "ufo") + "\n"
    for f in sorted(STATIC.iterdir()) if STATIC.is_dir() else []:
        if f.is_file() and not f.name.startswith("."):
            pages[DOCS / f.name] = f.read_bytes()
    return pages


def stale_episode_dirs(pages: dict[Path, str | bytes]) -> list[Path]:
    """docs/ep/ にあるが data に無い回のページ (回を消した・番号を直したときに残るもの)。"""
    root = DOCS / "ep"
    if not root.is_dir():
        return []
    keep = {p.parent for p in pages}
    return sorted(d for d in root.iterdir() if d.is_dir() and re.fullmatch(r"[0-9]+", d.name) and d not in keep)


def main() -> int:
    pages = render()
    stale = stale_episode_dirs(pages)
    if "--check" in sys.argv:
        bad = [p for p, body in pages.items()
               if not p.exists() or (p.read_bytes() if isinstance(body, bytes) else p.read_text(encoding="utf-8")) != body]
        if bad or stale:
            for p in bad:
                print(f"❌ {p.relative_to(ROOT)} が data と非同期")
            for d in stale:
                print(f"❌ {d.relative_to(ROOT)} は data に無い回のページ")
            print("   → python3 build.py で再生成してください")
            return 1
        print(f"✅ docs/ は data と同期済み ({len(pages)} ページ)")
        return 0
    for p, body in pages.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            p.write_bytes(body)
        else:
            p.write_text(body, encoding="utf-8")
    for d in stale:
        shutil.rmtree(d)
        print(f"🗑  {d.relative_to(ROOT)} (data に無い回)")
    print(f"✅ generated docs/ ({len(pages)} ページ)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
