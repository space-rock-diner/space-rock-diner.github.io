# CLAUDE.md — space-rock-diner.github.io

ポッドキャスト「オダキンカワヤンの宇宙ロック食堂」の**公開ウェブサイト**（GitHub Pages → Cloudflare Pages へ引っ越し中、DESIGN.md）。

- 公開 URL: https://space-rock-diner.github.io/
- **このリポは public**。企画・収録素材・台本は所有者が別の非公開リポで管理しており、
  ここには公開してよいもの（サイト本体とエピソード一覧データ）だけを置く。

## 構造

| path | 役割 |
|---|---|
| `data/episodes.yaml` | エピソード一覧の SoT（+ `show_links` = 各配信先の番組ページ URL） |
| `data/site.yaml` | サイト全体の設定（`mark_style` = 絵の画風 / `otayori` = お便りの有効化と Turnstile のサイトキー） |
| `art/marks.py` | 絵（UFO / ベース / カレー）を SVG 文字列で返す。画風 3 つ（line / sticker / neon） |
| `build.py` | `docs/index.html` を生成（PyYAML のみ依存、`--check` で同期検査） |
| `functions/api/otayori.js` | お便りの受け口（Cloudflare Pages Functions、POST `/api/otayori` → D1） |
| `schema.sql` | お便りを溜める D1 の表 |
| `wrangler.toml` | Cloudflare Pages の設定（配信するのは `docs/`、D1 の結び付け） |
| `docs/` | GitHub Pages 公開物（生成物、手編集禁止） |

## 更新手順

1. `data/episodes.yaml` にエピソードを追記（schema はファイル冒頭コメント）
2. `python3 build.py` → `docs/index.html` 再生成
3. commit + push（生成物も commit する = Pages は docs/ を配信）

## 作業ルール

- **出演者は通称（オダキン / カワヤン）のみ。実名・所属・連絡先は一切書かない**
  （file 本文だけでなく commit message も含む）
- `docs/` は生成物 — 直接編集せず `build.py` / `data/` を直す
- エピソード紹介文などの公開文面の文体運用は所有者側で別管理
  （このリポの範囲では「description に入っている文をそのまま表示する」だけでよい）
