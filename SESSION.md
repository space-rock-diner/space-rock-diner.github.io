# SESSION.md — space-rock-diner-web

## Status

公開中 = https://space-rock-diner.pages.dev/ （Cloudflare Pages。旧 github.io は転送ページ）。エピソードは配信先で公開されると
自動で追記される（CLAUDE.md §更新手順）。 2026-09-25〜 トップ（聴く・最新の回・これまでの回・お便り）+ 回ごとのページ `/ep/<番号>/`
（LISTEN の埋め込みプレーヤー・この回に出てきたもの・その回へのお便り）。古い `/#ep<番号>` はトップが回のページへ移す（DESIGN.md §回ごとのページ）。
配信先 = LISTEN・Spotify・Amazon Music。お便りコーナー稼働中（Turnstile つき）。過去の状態と更新記録 = [`SESSION-archive.md`](SESSION-archive.md)。

## 次にやること

- [ ] Apple Podcasts と YouTube の番組ページが開くようになったら `data/episodes.yaml` の `show_links` に足す（所有者側の TODO が知らせる）
- [ ] 最初の「第N回について」のお便りで、受け口が D1 に `episode` 欄を足す（手元の古い表では確かめ済み、本番はまだ 1 通も来ていない）。
      届いたら所有者側の `read-otayori.py` で「第N回へ」と出るかを見る

## 最終更新

2026-09-25 — 回ごとのページを公開（所有者 OK）。配信先のボタンを見出しの下へ、LISTEN の埋め込みプレーヤー、SNS のカード、
小さい字のコントラスト、狭いスマホではがきがはみ出していたのを修正。本番で `/#ep1` → `/ep/1/` の転送と 390px 幅の表示を確認。
2026-09-22 — 第 1 回の「この回に出てきたもの」、各回の目印、Spotify・Amazon Music の番組リンク。SESSION を縮めて旧分は SESSION-archive.md へ。
