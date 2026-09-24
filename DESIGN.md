# DESIGN.md — space-rock-diner-web

## なぜ独立した public リポか（2026-08-18）

企画リポは出演者の PII を含みうるため private。サイトは公開物なので、
**clean なファイルだけの独立リポ・独立履歴**として切り出した（同 owner の
`wc2026` = private 正本 + public 静的サイトミラー、と同じパターン）。
GitHub Free の Pages は public リポのみ、という制約とも整合（金はかけない方針）。
2026-08-18: 二人の番組なので個人名 URL を避け、org `space-rock-diner` へ移管し
apex repo (`space-rock-diner.github.io`) に改名 → https://space-rock-diner.github.io/

## なぜフレームワークなしの Python 生成か

- サイトはトップ + 回ごとのページ（2026-09-24〜、下の §回ごとのページ）だけで、伸びるのは回の数だけ → Eleventy 等の
  Node toolchain は過剰。依存は PyYAML のみ
- `data/episodes.yaml`（SoT）→ `build.py` → `docs/`（生成物 commit）
  の一方向。データ駆動にしておくことで、一話追加 = YAML 1 entry + rebuild で済む
- 生成物を commit するのは GitHub Pages（docs/ 配信、build 環境なし）のため。
  同期ズレは `build.py --check` で検査できる

## RSS を自作しない

ポッドキャストの RSS feed はホスティングサービス（LISTEN）が生成するものを正とする。
サイトはそこへのリンクを置くだけ（feed の二重管理をしない）。

## 絵は SVG をページに埋め込む（2026-09-14）

一般則（描いて見て直す・特徴の取り方・id の接頭辞）= [claude-config `inline-svg-illustration.md`](https://github.com/odakin/claude-config/blob/main/conventions/inline-svg-illustration.md)。

ヘッダーの 🛸🎸🍛 は、絵文字の 🎸 がギター（6 弦）でベースを描けないので、自前の絵に替えた。
ベースはリッケンバッカー 4003（波形に伸びる長いホーン、2+2 のペグ、白い縁取りと 2 段のピックガード、
ブリッジの金属カバー、三角のインレイ）、カレーは黒い丸皿のあいがけスパイスカレーを参考にしている。

- `art/marks.py` が SVG 文字列を返し、`build.py` がページに直接埋め込む。画像ファイルを別に
  置かないので、読み込み待ちも配信漏れも起きない
- 画風は 3 つ持ち、`data/site.yaml` の `mark_style` で切り替える
- 同じ絵を 1 ページに何枚も入れるので、`marks.scoped()` で SVG 内の id に接頭辞を付ける
  （id が重複すると、非表示の SVG にあるグラデーション定義を参照した絵が描かれなくなる）

## Cloudflare Pages へ引っ越した（2026-09-14）

一般則（受け口の選択肢の壊れ方・Pages と D1・Turnstile・GitHub Pages の転送）= [claude-config `static-site-form-backend.md`](https://github.com/odakin/claude-config/blob/main/conventions/static-site-form-backend.md)。ここにはこのサイトで決めたことだけを書く。

GitHub Pages は置いたファイルを配るだけで、お便りを受け取るプログラムを動かせない。Cloudflare Pages なら
同じサイトに受け口の関数を置けるので、サイトごと引っ越す（所有者判断。URL は `space-rock-diner.pages.dev`）。

- **Workers でなく Pages で作る**: Cloudflare の作成画面は既定で Workers に誘導するが、Workers の URL には
  アカウント名が入る。Pages の URL は `<プロジェクト名>.pages.dev` だけ
- 配信するのは commit 済みの `docs/` で、Cloudflare 側ではビルドしない（`wrangler.toml` の `pages_build_output_dir`）
- 費用: 無料枠に収まる（静的ファイルは無制限、関数は 1 日 10 万リクエスト、D1 は 1 日 10 万行の書き込み）
- アカウントは番組用（所有者判断）。プロジェクトは GitHub 連携で作った = `main` への push で自動公開
- 旧 URL（github.io）: GitHub Pages はサーバー側で転送できないので、配信元を `gh-pages` ブランチに切り替え、
  開いた瞬間に新しい URL の同じ場所へ移すページを置いた（`index.html` と `404.html` が同じ転送ページ）

## お便りコーナー: 見た目も受け口も同じサイト（2026-09-14）

- 画面: `build.py` のはがき。入力はラジオネーム（任意）と本文だけ。宛先のメールアドレスはページに出さない（所有者判断）
- 受け口: `functions/api/otayori.js`（POST `/api/otayori`）→ D1 の `letters` 表（`schema.sql`）。
  IP やメールアドレスは保存しない
- 同じサイト内の通信なので、届いたか失敗したかを画面に正しく出せる（Google フォーム方式を試したときは、
  別ドメインゆえ受け口がエラーでも「届いた」と出てしまった = 実測で却下）
- 機械よけ: 人には見えない欄（埋まっていたら保存せず成功を返す）+ Cloudflare Turnstile（2026-09-15 有効化、
  番組用アカウントのウィジェット「宇宙ロック食堂 お便り」、managed）。受け口は Cloudflare 公式の手順どおり
  **成功・動作名 `otayori`・送信元ホスト名（`wrangler.toml` の `TURNSTILE_HOSTNAMES`）がすべて合うときだけ**通し、
  確認できないとき（秘密鍵が無い・通信失敗）は拒否する。ページは確認欄を明示描画し、送るたびにリセット（トークンは 1 回きり）。
  サイトキーは `data/site.yaml`、秘密鍵は Pages の Secret `TURNSTILE_SECRET`（リポに書かない）
- 本文の上限は 20,000 字 = 400 字詰め原稿用紙 50 枚（所有者判断）。上限は長さの目安ではなく、いたずらの 1 通を
  大きくさせないための蓋（D1 の 1 行は 2 MB まで、無料枠の保存は全体で 5 GB）。当初の 65535 字（約 164 枚）から下げた
- JavaScript が無い送信には、JSON でなくトップページへの転送を返す（ただし Turnstile を有効にすると JS 必須）
- `data/site.yaml` の `otayori.enabled` が false のあいだは「準備中」で送信不可（2026-09-14 に true）
- メール通知は無い: Cloudflare からメールを送るには独自ドメイン（有料）が要る。溜まったお便りは読みに行く

ローカルでの確かめ方: `npm i -D wrangler` → `npx wrangler d1 execute otayori --local --file=schema.sql`
→ `npx wrangler pages dev`（`wrangler.toml` の D1 の行を有効にしておく）。

## 配信先の表示

配信先はトップの見出しのすぐ下（と回のページの紹介文の下）にボタンで並べる（ポッドキャストのサイトで最初に探されるのは「どこで聴けるか」）。
`data/episodes.yaml` の `show_links`（番組ページ URL）が空の配信先はボタンにせず、「… は準備中」の 1 行にまとめる
（押せないものをボタンの形で並べない）。URL が入り次第、自動でボタンに変わる。
回のページでは、その回の URL がある配信先（今は LISTEN）はその回へ、無い配信先は番組ページへ飛ぶ。

## 回ごとのページ（2026-09-24、所有者判断）

週 2 回配信なので 1 年で約 100 回になる。全回を紹介文つきで 1 ページに縦に並べていたので、回が増えるたびに
お便りの欄が下へ沈んでいた。そこで次の形にした。

- **トップ** = 聴く（配信先のボタン）/ この番組 / 出演 / 最新の回（全文）/ これまでの回 / お便り。
  これまでの回は 1 行ずつ、新しい 5 回だけ見せてそれより前はたたむ（`build.py` の `PAST_SHOWN`）。
  最新の回のすぐ下に置いて回の一覧をひとかたまりにし、何回まで増えてもお便りの欄の位置が変わらないようにした
- **回のページ** `/ep/<番号>/` = 紹介文 / 聴く / この回に出てきたもの / お便り / 前後の回。
  各ページがその回の題と紹介文を og:title・og:description に持つので、SNS に回のリンクを貼るとその回のカードが出る
  （カードの画像は番組のアートワーク = `static/artwork-1200.jpg`）
- **古いリンク**: 第 1〜7 回の配信先の紹介文には `/#ep<番号>` の形でトップを指すリンクが入っている（公開済み・予約済みで
  書き換えない）。トップの head の小さな script が、知っている番号ならその回のページへ移す。第 8 回からは
  所有者の配信の道具がサイトの `docs/ep/` を見て `/ep/<番号>/` を直接書く
- **聴く**: `data/site.yaml` の `listen_player` が true なら、最新の回と回のページに LISTEN の埋め込みプレーヤーを出す
  （LISTEN の oEmbed が返す `<回の URL>/player`。選べるのは色だけで、LISTEN がその回に出す文 = 紹介文か文字起こしの
  抜粋 も表示される）
- **回ごとのお便り**: 回のページのはがきには「どれへのお便り？」の 2 択（最初は「第N回について」、もう 1 つは
  「番組へ（回は決めない）」）。選んだ回の番号が `episode` として受け口に届き、D1 の `letters.episode` に入る。
  回を決めないお便りは NULL。トップのはがきは回を決めない
- **episode 欄の足し方**: 2026-09-14 に作った D1 には欄が無い。受け口が、最初の回つきのお便りのときに
  `ALTER TABLE letters ADD COLUMN episode INTEGER` で足してから入れ直す（wrangler の使えるマシンに作業を頼らない。
  手元の wrangler + 古い表で 2026-09-24 に確かめた）
- **見た目の点検（2026-09-24）**: 小さい字の色を背景のいちばん濃いところでも 4.5:1 に（WCAG AA）、押す所は 44px 以上、
  見出しは文節で改行して行の長さを揃える（`word-break: auto-phrase` + `text-wrap: balance`。長い本文には使わない =
  行末がそろわなくなる）。はがきの中の確認欄（Turnstile の flexible は幅 300px 以上が要る）が、幅 375〜390px の
  画面ではがきを押し広げていたのを直した（中身の最小幅で広げない + 狭い画面は余白を詰め、それでも入らなければ compact）
