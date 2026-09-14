# space-rock-diner.github.io

ポッドキャスト「オダキンカワヤンの宇宙ロック食堂」の公式サイト。

**→ https://space-rock-diner.pages.dev/**

（旧 URL の https://space-rock-diner.github.io/ は、開くと新しい URL へ移ります）

素粒子・宇宙・ロック・カレーのポッドキャスト。専門家に素人が聞き、素人に専門家が聞く。

## 仕組み

`data/episodes.yaml`（エピソード一覧）から `build.py` が `docs/index.html` を生成し、
Cloudflare Pages が `docs/` を配信する（`main` に push すると自動で公開）。お便りの受け口は `functions/`。詳細は [`DESIGN.md`](DESIGN.md)。
