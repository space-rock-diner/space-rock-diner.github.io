# CLAUDE.md — space-rock-diner-web

ポッドキャスト「オダキンカワヤンの宇宙ロック食堂」の**公開ウェブサイト**（GitHub Pages）。

- 公開 URL: https://odakin.github.io/space-rock-diner-web/
- **このリポは public**。企画・収録素材・台本は所有者が別の非公開リポで管理しており、
  ここには公開してよいもの（サイト本体とエピソード一覧データ）だけを置く。

## 構造

| path | 役割 |
|---|---|
| `data/episodes.yaml` | エピソード一覧の SoT（+ `show_links` = 各配信先の番組ページ URL） |
| `build.py` | `docs/index.html` を生成（PyYAML のみ依存、`--check` で同期検査） |
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
