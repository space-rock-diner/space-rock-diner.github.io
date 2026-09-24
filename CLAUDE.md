# CLAUDE.md — space-rock-diner.github.io

ポッドキャスト「オダキンカワヤンの宇宙ロック食堂」の**公開ウェブサイト**（Cloudflare Pages、2026-09-14 に GitHub Pages から引っ越し）。

- 公開 URL: https://space-rock-diner.pages.dev/ （番組用アカウントの Cloudflare Pages。`main` に push すると自動で公開）
- 旧 URL https://space-rock-diner.github.io/ は `gh-pages` ブランチの転送ページ（GitHub Pages）。サイト本体をそこに置かない
- **このリポは public**。企画・収録素材・台本は所有者が別の非公開リポで管理しており、
  ここには公開してよいもの（サイト本体とエピソード一覧データ）だけを置く。

## 構造

| path | 役割 |
|---|---|
| `data/episodes.yaml` | エピソード一覧の SoT（+ `show_links` = 各配信先の番組ページ URL） |
| `data/site.yaml` | サイト全体の設定（`mark_style` = 絵の画風 / `otayori` = お便りの有効化と Turnstile のサイトキー） |
| `art/marks.py` | 絵（UFO / ベース / カレー）を SVG 文字列で返す。画風 3 つ（line / sticker / neon） |
| `build.py` | `docs/index.html` を生成（PyYAML のみ依存、`--check` で同期検査） |
| `static/` | 手で置く画像（SNS のカード = 番組のアートワーク、ホーム画面のアイコン）。`build.py` が `docs/` に写す |
| `functions/api/otayori.js` | お便りの受け口（Cloudflare Pages Functions、POST `/api/otayori` → D1） |
| `schema.sql` | お便りを溜める D1 の表 |
| `wrangler.toml` | Cloudflare Pages の設定（配信するのは `docs/`、D1 の結び付け） |
| `docs/` | GitHub Pages 公開物（生成物、手編集禁止） |

## 更新手順

1. `data/episodes.yaml` にエピソードを追記（schema はファイル冒頭コメント）
2. `python3 build.py` → `docs/index.html` 再生成
3. commit + push（生成物も commit する = Cloudflare Pages は docs/ を配信、ビルドはしない）

**エピソードの追記はふだん自動**: 所有者の非公開の配信の道具が、配信先で公開されたのを確かめた時点で 1〜3 を行う
（常時動くマシンの定期実行）。手で直すときも同じ手順。各回の区画には `id="ep<番号>"` の目印が付き、配信先の紹介文からそこへ飛ぶ。

**2026-09-24〜 回ごとのページ**: `build.py` はトップ `docs/index.html` に加えて回ごとのページ `docs/ep/<番号>/index.html`・
`favicon.svg`・`static/` の写しを作る（data に無い回のページは消す）。上の表と手順の `docs/index.html` は `docs/` 全体と読み替え、
commit も `docs/` ごと（回を足すと新しいファイルができる）。`data/site.yaml` に `site_url`（公開 URL）と `listen_player`
（LISTEN の埋め込みプレーヤー）が増えた。配信先の紹介文の古い形 `/#ep<番号>` は、トップがその回のページへ移す。
設計と理由 = DESIGN.md §回ごとのページ。

## 作業ルール

- **出演者は通称（オダキン / カワヤン）のみ。実名・所属・連絡先は一切書かない**
  （file 本文だけでなく commit message も含む）
- `docs/` は生成物 — 直接編集せず `build.py` / `data/` を直す
- エピソード紹介文などの公開文面の文体運用は所有者側で別管理
  （このリポの範囲では「description に入っている文をそのまま表示する」だけでよい）
