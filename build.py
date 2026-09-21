#!/usr/bin/env python3
"""data/ から docs/index.html を生成する静的サイトビルダー。

使い方:
    python3 build.py        # docs/index.html を再生成
    python3 build.py --check  # 生成物が data と同期しているか検査 (CI / 手元確認用)

設計 (DESIGN.md 参照): 外部依存は PyYAML のみ、テンプレートは本 file 内に持つ
(サイト 1 ページ + 将来もエピソード一覧が伸びるだけなので、フレームワークは使わない)。
絵は art/marks.py が SVG 文字列で返し、ここでページに埋め込む (外部ファイルを読み込まない)。
公開ページの文面を変えるときは所有者の文体運用に従う。
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "index.html"
sys.path.insert(0, str(ROOT / "art"))
import marks  # noqa: E402

PLATFORMS = [
    ("listen", "LISTEN"),
    ("spotify", "Spotify"),
    ("apple", "Apple Podcasts"),
    ("amazon", "Amazon Music"),
    ("youtube", "YouTube"),
]

# お便りの切手に出す絵 (開くたびにどれか 1 つ)
STAMP_ART = ["ufo", "bass", "curry"]

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>オダキンカワヤンの宇宙ロック食堂</title>
<meta name="description" content="素粒子・宇宙・ロック・カレーのポッドキャスト。専門家に素人が聞き、素人に専門家が聞く。">
<meta property="og:title" content="オダキンカワヤンの宇宙ロック食堂">
<meta property="og:description" content="素粒子・宇宙・ロック・カレーのポッドキャスト">
<meta property="og:type" content="website">
<style>
:root {
  --bg: #faf6ec;
  --bg2: #f1e9d6;
  --text: #33302b;
  --dim: #85806f;
  --dim-strong: #6b6657;
  --accent: #d9731a;
  --accent-ink: #b4540f;
  --accent2: #1f7a70;
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
.ep-meta { color: var(--dim); font-size: .85rem; letter-spacing: .08em; }
.ep-title { font-size: 1.15rem; font-weight: 700; margin: .2rem 0 .5rem; }
.ep-desc { color: var(--text); font-size: .95rem; }
.ep-links { margin-top: .6rem; font-size: .88rem; }
.ep-links a { margin-right: 1.1em; }
.ep-refs { margin-top: .6rem; font-size: .86rem; color: var(--dim); line-height: 1.8; }
.ep-refs a { margin-right: .9em; white-space: nowrap; }
.empty { color: var(--dim); text-align: center; padding: 1.5rem 0; letter-spacing: .1em; }
.platforms { display: flex; flex-wrap: wrap; gap: .7rem; }
.platform {
  border: 1px solid var(--line); border-radius: 999px; padding: .35rem 1.1rem;
  font-size: .9rem; color: var(--dim); background: var(--card);
}
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
  .stamp { width: 66px; height: 78px; }
  .stamp-art { width: 44px; }
  .postmark { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; }
}
</style>
</head>
<body>
<main>
  <header>
    <div class="mark">%%MARK%%</div>
    <h1>オダキンカワヤンの<br>宇宙ロック食堂</h1>
    <p class="tagline">素粒子・宇宙・ロック・カレーのポッドキャスト</p>
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
    <h2>エピソード</h2>
%%EPISODES%%
  </section>

  <section id="otayori" aria-labelledby="otayori-h">
    <h2 id="otayori-h">お便り</h2>
    <p class="lead">聞きたいこと、言いたいこと、どうでもいいこと。<br>ふたりで読んで、ふたりで考えます。</p>
    <form class="postcard" id="otayori-form" %%FORM_ATTRS%% novalidate>
      <div class="postcard-inner">
        <div class="postcard-head">
          <p class="address"><small>TO</small><b>宇宙ロック食堂</b><span>オダキン・カワヤン</span></p>
          <div class="stamp-wrap" aria-hidden="true">
            <div class="postmark">宇宙<br>ロック<br>食堂</div>
            <div class="stamp"><div class="stamp-face">
%%STAMPS%%
              <span class="stamp-price">ロック便</span>
            </div></div>
          </div>
        </div>
        <div class="field">
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
%%TURNSTILE%%
        <div class="actions">
          <p class="status" id="otayori-status" role="status">%%STATUS%%</p>
          <button type="submit" class="send"%%DISABLED%%>ポストに入れる
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12 20 4l-4 16-4-6-8-2Z"/><path d="m12 14 8-10"/></svg>
          </button>
        </div>
      </div>
    </form>
  </section>

  <section>
    <h2>配信先</h2>
    <div class="platforms">
%%PLATFORMS%%
    </div>
  </section>

  <footer>© 2026 オダキンカワヤンの宇宙ロック食堂<br><span class="credit">文責　クロード</span></footer>
</main>
<script>
(() => {
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
</script>
</body>
</html>
"""


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


def render() -> str:
    data = load("episodes.yaml")
    site = load("site.yaml")
    style = site.get("mark_style") or "sticker"
    if style not in {k for k, _, _ in marks.STYLES}:
        raise SystemExit(f"❌ data/site.yaml の mark_style が不明: {style}")
    episodes = sorted(data.get("episodes") or [], key=lambda e: e.get("number", 0), reverse=True)

    if not episodes:
        eps_html = '    <p class="empty">ただいま仕込み中。</p>'
    else:
        blocks = []
        for e in episodes:
            links = "".join(
                f'<a href="{esc(e["links"][key])}">{label}</a>'
                for key, label in PLATFORMS if key in (e.get("links") or {})
            )
            refs = "".join(
                f'<a href="{esc(r["url"])}">{esc(r["label"])}</a>'
                for r in (e.get("references") or [])
            )
            blocks.append(
                f'    <div class="episode" id="ep{e["number"]}">\n'
                f'      <div class="ep-meta">#{e["number"]} ・ {esc(str(e.get("date", "")))}</div>\n'
                f'      <div class="ep-title">{esc(e["title"])}</div>\n'
                f'      <div class="ep-desc">{esc(e.get("description", ""))}</div>\n'
                + (f'      <div class="ep-links">{links}</div>\n' if links else "")
                + (f'      <div class="ep-refs">この回に出てきたもの: {refs}</div>\n' if refs else "")
                + "    </div>"
            )
        eps_html = "\n".join(blocks)

    # 配信先: episodes に 1 つでも URL があればリンク化、無ければ「準備中」表示
    all_links: dict[str, str] = {}
    for e in episodes:
        for key, url in (e.get("links") or {}).items():
            all_links.setdefault(key, url)
    all_links = {**all_links, **(data.get("show_links") or {})}

    plat_html = "\n".join(
        (f'      <a class="platform" href="{esc(all_links[key])}">{label}</a>'
         if key in all_links else
         f'      <span class="platform">{label}（準備中）</span>')
        for key, label in PLATFORMS
    )

    # お便り
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
                     ' theme: "light", size: "flexible" }); };</script>\n'
                     '        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&amp;onload=otayoriTurnstileReady" async defer></script>')
    if ot.get("enabled") is True:
        form_attrs = 'data-ready="1" action="/api/otayori" method="post"'
        status, disabled = "", ""
    else:
        form_attrs, status, disabled = 'data-ready="0"', "ただいま準備中。もうすぐポストを置きます。", " disabled"

    return (TEMPLATE
            .replace("%%MARK%%", marks.scoped(marks.mark(style), "mark"))
            .replace("%%EPISODES%%", eps_html)
            .replace("%%STAMPS%%", stamps)
            .replace("%%FORM_ATTRS%%", form_attrs)
            .replace("%%TURNSTILE%%", turnstile)
            .replace("%%STATUS%%", status)
            .replace("%%DISABLED%%", disabled)
            .replace("%%PLATFORMS%%", plat_html))


def main() -> int:
    html = render()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != html:
            print("❌ docs/index.html が data と非同期 — python3 build.py で再生成してください")
            return 1
        print("✅ docs/index.html は data と同期済み")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✅ generated {OUT.relative_to(ROOT)} ({len(html)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
