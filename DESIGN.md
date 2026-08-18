# DESIGN.md — space-rock-diner-web

## なぜ独立した public リポか（2026-08-18）

企画リポは出演者の PII を含みうるため private。サイトは公開物なので、
**clean なファイルだけの独立リポ・独立履歴**として切り出した（同 owner の
`wc2026` = private 正本 + public 静的サイトミラー、と同じパターン）。
GitHub Free の Pages は public リポのみ、という制約とも整合（金はかけない方針）。
2026-08-18: 二人の番組なので個人名 URL を避け、org `space-rock-diner` へ移管し
apex repo (`space-rock-diner.github.io`) に改名 → https://space-rock-diner.github.io/

## なぜフレームワークなしの Python 生成か

- サイトは実質 1 ページ + 伸びるのはエピソード一覧だけ → Eleventy 等の
  Node toolchain は過剰。依存は PyYAML のみ
- `data/episodes.yaml`（SoT）→ `build.py` → `docs/index.html`（生成物 commit）
  の一方向。データ駆動にしておくことで、一話追加 = YAML 1 entry + rebuild で済む
- 生成物を commit するのは GitHub Pages（docs/ 配信、build 環境なし）のため。
  同期ズレは `build.py --check` で検査できる

## RSS を自作しない

ポッドキャストの RSS feed はホスティングサービス（LISTEN）が生成するものを正とする。
サイトはそこへのリンクを置くだけ（feed の二重管理をしない）。

## 配信先の表示

`data/episodes.yaml` の `show_links`（番組ページ URL）が空の配信先は「準備中」と表示。
URL が入り次第、自動でリンクに変わる。
