#!/usr/bin/env python3
"""data/episodes.yaml から docs/index.html を生成する静的サイトビルダー。

使い方:
    python3 build.py        # docs/index.html を再生成
    python3 build.py --check  # 生成物が data と同期しているか検査 (CI / 手元確認用)

設計 (DESIGN.md 参照): 外部依存は PyYAML のみ、テンプレートは本 file 内に持つ
(サイト 1 ページ + 将来もエピソード一覧が伸びるだけなので、フレームワークは使わない)。
公開ページの文面を変えるときは所有者の文体運用に従う。
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "index.html"

PLATFORMS = [
    ("listen", "LISTEN"),
    ("spotify", "Spotify"),
    ("apple", "Apple Podcasts"),
    ("amazon", "Amazon Music"),
    ("youtube", "YouTube"),
]

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
  --accent: #d9731a;
  --accent2: #1f7a70;
  --line: #e0d7c0;
  --card: #fffdf7;
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
.mark { font-size: 2.6rem; letter-spacing: .1em; }
h1 { font-size: 1.9rem; font-weight: 700; letter-spacing: .12em; margin-top: .6rem; }
.tagline { color: var(--accent); margin-top: .8rem; letter-spacing: .18em; font-size: .95rem; }
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
.host b { color: var(--accent); font-size: 1.1rem; letter-spacing: .08em; }
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
</style>
</head>
<body>
<main>
  <header>
    <div class="mark">🛸🎸🍛</div>
    <h1>オダキンカワヤンの<br>宇宙ロック食堂</h1>
    <p class="tagline">素粒子・宇宙・ロック・カレーのポッドキャスト</p>
  </header>

  <section>
    <h2>この番組</h2>
    <blockquote class="intro">
      <p>素粒子って何ですか？宇宙はどこまで続くんですか？<br>
      カレー屋でありベーシストでもあるカワヤンが、物理研究者のオダキンに聞きます。</p>
      <p>逆に、このギターリフの気持ちよさって何ですか？スパイスってなんであんなに合わさるんですか？<br>
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

  <section>
    <h2>配信先</h2>
    <div class="platforms">
%%PLATFORMS%%
    </div>
  </section>

  <footer>© 2026 オダキンカワヤンの宇宙ロック食堂</footer>
</main>
</body>
</html>
"""


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render() -> str:
    data = yaml.safe_load((ROOT / "data" / "episodes.yaml").read_text(encoding="utf-8")) or {}
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
                '    <div class="episode">\n'
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
    show_links = yaml.safe_load((ROOT / "data" / "episodes.yaml").read_text(encoding="utf-8")).get("show_links") or {}
    all_links = {**all_links, **show_links}

    plat_html = "\n".join(
        (f'      <a class="platform" href="{esc(all_links[key])}">{label}</a>'
         if key in all_links else
         f'      <span class="platform">{label}（準備中）</span>')
        for key, label in PLATFORMS
    )

    return TEMPLATE.replace("%%EPISODES%%", eps_html).replace("%%PLATFORMS%%", plat_html)


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
