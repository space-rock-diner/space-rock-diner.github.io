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

`data/episodes.yaml` の `show_links`（番組ページ URL）が空の配信先は「準備中」と表示。
URL が入り次第、自動でリンクに変わる。
