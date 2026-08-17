# space-rock-diner-web

ポッドキャスト「オダキンカワヤンの宇宙ロック食堂」の公式サイト。

**→ https://odakin.github.io/space-rock-diner-web/**

素粒子・宇宙・ロック・カレーのポッドキャスト。専門家に素人が聞き、素人に専門家が聞く。

## 仕組み

`data/episodes.yaml`（エピソード一覧）から `build.py` が `docs/index.html` を生成し、
GitHub Pages が `docs/` を配信する。詳細は [`DESIGN.md`](DESIGN.md)。
