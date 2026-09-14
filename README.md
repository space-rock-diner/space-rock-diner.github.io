# gh-pages — 旧 URL の転送ページ

サイトは 2026-09-14 に Cloudflare Pages（https://space-rock-diner.pages.dev/ ）へ引っ越した。
このブランチは、旧 URL の https://space-rock-diner.github.io/ を開いた人を新しい URL の同じ場所へ移すためだけにある。
GitHub Pages はこのブランチの `docs/` を配信する（`index.html` と、存在しない場所用の `404.html` が同じ転送ページ）。

サイト本体は `main` ブランチ。ここは触らなくてよい。
`wrangler.toml` は、Cloudflare がこのブランチをプレビューとして組むときに失敗しないためのもの。
