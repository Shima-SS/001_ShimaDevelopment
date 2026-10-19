# 実装指示書：functions.php まわり（CPT・タクソノミー・カスタムフィールド）

> 置き場所：`docs/spec-functions.md`
> 進め方は `CLAUDE.md` の「1フェーズずつ止まる」ルールに必ず従うこと。
> **⭐マーク** のフェーズは、終了後にユーザーが外部レビューを挟む予定。報告を特に丁寧に。

---

## 0. このドキュメントの範囲

### やること
- テーマの骨組み（`style.css` / `functions.php` / 最小の `index.php`）
- カスタム投稿タイプ 2つ、タクソノミー 4つの登録
- SCF によるカスタムフィールド定義（PHP で登録）
- フィールド取得関数のレイヤー
- 一覧ページのクエリ制御（絞り込み・並べ替え・キーワード）

### やらないこと（別の指示書で扱う）
- 見た目のテンプレート（`archive-product.php` `single-app.php` 等）とCSSの作り込み
- 検索・絞り込みUIの部品（`template-parts/archive-filter.php`）
- ブログ一覧 `/blog/` のシリーズカード表示、記事の前後ナビ

---

## 1. 確定している設計

### 1-1. URL

WordPress のパーマリンク設定は **カスタム構造 `/blog/%postname%/`**（ユーザー設定済み）。
このため CPT・タクソノミーの rewrite には **必ず `'with_front' => false`** を付けること。
付け忘れると `/blog/products/` のようなURLになる。

| URL | 中身 |
|---|---|
| `/products/` `/products/{slug}/` | CPT `product` |
| `/product-type/{slug}/` | タクソノミー `product_type` |
| `/product-tag/{slug}/` | タクソノミー `product_tag` |
| `/apps/` `/apps/{slug}/` | CPT `app` |
| `/platform/{slug}/` | タクソノミー `platform` |
| `/series/{slug}/` | タクソノミー `series`（投稿用） |
| `/play/{slug}/` `/demo/{slug}/` | **WP外の実ディレクトリ。触らない** |

### 1-2. 投稿タイプ

| 内部名 | 管理画面名 | rewrite slug | has_archive | supports | menu_icon |
|---|---|---|---|---|---|
| `product` | 商品 | `products` | `products` | title, editor, thumbnail, excerpt, revisions | `dashicons-products` |
| `app` | アプリ | `apps` | `apps` | title, editor, thumbnail, excerpt, revisions | `dashicons-smartphone` |

共通：`public => true`, `show_in_rest => true`, `menu_position => 5`（product）/ `6`（app）

- **抜粋（excerpt）** を「対象業種・想定用途／誰のどんな場面を助けるか」の1〜2行リード文として使う
- **本文（editor）** は「このテーマについて」「このアプリについて」の自由記述欄として使う（空なら非表示にする想定）

### 1-3. タクソノミー

| 内部名 | 対象 | 管理画面名 | 階層 | rewrite slug | 初期ターム（slug：名前） |
|---|---|---|---|---|---|
| `product_type` | product | 商品種別 | あり | `product-type` | `wordpress-theme`：WPテーマ / `html-template`：HTMLテンプレ |
| `product_tag` | product | 商品タグ | なし | `product-tag` | なし |
| `platform` | app | プラットフォーム | あり | `platform` | `web`：Web / `android`：Android / `ios`：iOS |
| `series` | post | シリーズ | あり | `series` | なし |

共通：`public => true`, `show_in_rest => true`, `show_admin_column => true`, `with_front => false`

- 内部名はアンダースコア、URLはハイフン（意図的に分けている）
- `series` は「1記事1シリーズ」で運用する（今回は強制の仕組みは作らない）

---

## 2. カスタムフィールド定義（SCF）

- 登録は `inc/fields.php` で `acf_add_local_field_group()` を使う（`acf/include_fields` フックで）
- field key は `field_shima_{フィールド名}`、group key は `group_shima_{グループ名}` で統一
- 画像系の return_format は **ID**（テンプレート側で `wp_get_attachment_image()` を使うため）

### 2-1. グループ `product`（表示条件：post_type == product）

| name | 種類 | 設定・説明 |
|---|---|---|
| `product_plans` | repeater | 販売プラン。min 1 / max 3、layout: block、ボタン「プランを追加」 |
| └ `plan_name` | text | 必須。例：テーマのみ |
| └ `plan_price` | number | 必須。税込・円。min 0 / step 1。append「円」。0 は無料扱い |
| └ `plan_description` | textarea | 2行。例：テーマファイル一式＋設置マニュアル |
| └ `plan_booth_url` | url | 必須。BOOTH の商品ページ |
| `product_gallery` | gallery | min 1 / max 8、jpg/png/webp。説明文「4〜6枚推奨。代替テキストを必ず入力」 |
| `product_features` | repeater | 主な機能。max 12、ボタン「機能を追加」 |
| └ `feature_text` | text | 必須 |
| `spec_wp_version` | text | 対応WPバージョン。placeholder `6.x`。説明「WPテーマのみ」 |
| `spec_browsers` | text | 対応ブラウザ。説明「HTMLテンプレのみ」 |
| `spec_license` | text | default `1サイト / 商用可` |
| `spec_support` | text | default `購入後6ヶ月` |
| `product_demo_url` | url | 説明「HTMLテンプレのデモ（/demo/{slug}/ のフルURL）。WPテーマは空欄にする」 |
| `product_faq` | repeater | よくある質問。max 10 |
| └ `faq_question` | text | 必須 |
| └ `faq_answer` | textarea | 必須 |

### 2-2. グループ `app`（表示条件：post_type == app）

| name | 種類 | 設定・説明 |
|---|---|---|
| `app_status` | select | 必須。`published`：公開中 / `coming_soon`：準備中。default `coming_soon` |
| `app_icon` | image | アプリアイコン（正方形） |
| `app_category_label` | text | 例：育児記録 |
| `app_price_label` | text | 例：無料 / アプリ内課金あり |
| `app_play_path` | text | Web版の置き場所。**`/play/xxx/` のように先頭スラッシュから書く相対パス**。説明文にもそう書く |
| `app_store_url` | url | App Store |
| `app_google_play_url` | url | Google Play |
| `app_screenshots` | gallery | max 8 |
| `app_rating` | number | 平均評価。min 0 / max 5 / step 0.1。手入力 |
| `app_downloads_label` | text | 例：12,000+。手入力 |
| `app_tech` | text | 使用技術。例：React / Firebase |

### 2-3. グループ `changelog`（表示条件：post_type == product **または** app）

更新履歴。**新しい版を一番上に追加する運用**。バージョン表記はセマンティックバージョニング。

| name | 種類 | 設定・説明 |
|---|---|---|
| `changelog` | repeater | min 0、layout: table、ボタン「新しい版を追加（上に移動してください）」 |
| └ `cl_version` | text | 必須。例 `1.2.16`。**形式チェックあり**（下記） |
| └ `cl_date` | date_picker | 必須。表示 `Y.m.d`、return `Ymd` |
| └ `cl_notes` | textarea | 3行。変更内容 |

- `cl_version` は `acf/validate_value/name=cl_version` で `^\d+\.\d+\.\d+$` を検証し、不一致なら「1.2.3 の形式で入力してください」
- 準備中のアプリは履歴0行でよい

---

## 3. 保存時の同期メタ（並べ替え・絞り込み用）

バージョンは文字列なので並べ替えに使えない（"1.10.0" < "1.9.0" になる）。価格もリピーターの中にあり検索しづらい。
そこで **保存時に計算した値を隠しメタに書き込む**。

- フック：`acf/save_post`（priority 20）。post_type が product / app のときだけ動く
- 自動保存・リビジョンでは動かさない

| メタキー | 対象 | 値 |
|---|---|---|
| `_shima_price_min` | product | 全プランの `plan_price` の最小値（整数） |
| `_shima_latest_release` | product / app | `changelog` の `cl_date` の **最大値**（`Ymd`）。履歴0行なら `00000000` |
| `_shima_current_version` | product / app | 上記最大日付の行の `cl_version`。同日が複数あれば上の行。0行なら空文字 |

- 「一番上の行」ではなく「日付が最大の行」を現行版とする（並べ替えミスへの保険）
- メタは **必ず全投稿に存在させる**（値が無い場合も既定値で保存）。並べ替え時に投稿が消えるのを防ぐため

---

## 4. 取得関数レイヤー（`inc/template-functions.php`）

テンプレートからはこれらだけを使う。SCF 無効時も落ちないこと。

| 関数 | 戻り値 |
|---|---|
| `shima_field( $name, $post_id = null, $default = '' )` | 汎用。`get_field()` の薄いラッパー |
| `shima_get_plans( $post_id = null )` | `[ ['name','price'(int),'description','booth_url'], ... ]` |
| `shima_get_price_min( $post_id = null )` | `?int`（隠しメタから。無ければ計算） |
| `shima_format_price( int $price )` | `¥14,800`。0 は `FREE` |
| `shima_get_gallery_ids( $name, $post_id = null )` | `int[]` |
| `shima_get_features( $post_id = null )` | `string[]` |
| `shima_get_faq( $post_id = null )` | `[ ['question','answer'], ... ]` |
| `shima_get_changelog( $post_id = null )` | `[ ['version','date'(Ymd),'notes'], ... ]`（保存順のまま） |
| `shima_get_current_version( $post_id = null )` | `['version','date']` または `null` |
| `shima_get_demo_link( $post_id = null )` | 下記ルールで `['type','url','label']` または `null` |
| `shima_app_is_coming_soon( $post_id = null )` | `bool` |
| `shima_get_app_links( $post_id = null )` | 下記ルールでボタン情報の配列 |

**デモリンクのルール**
- `product_demo_url` があれば → `type: demo`、ラベル「デモを見る」
- 無く、`product_type` が `wordpress-theme` なら → `type: contact`、URL は `/contact/?product={slug}`、ラベル「デモを依頼する」
- それ以外 → `null`

**アプリリンクのルール**
- 準備中なら空配列
- `platform` のタームに応じて、`web` → 「ブラウザで使う」（`home_url( app_play_path )`）、`ios` → 「App Store」、`android` → 「Google Play」
- URL が空のものは出さない

---

## 5. 一覧クエリ（`inc/queries.php`）

- `pre_get_posts` で **メインクエリかつ管理画面以外** のときだけ変更
- 独自クエリ変数は `query_vars` フィルタで登録。**WP予約語（`s` `tag` `type` 等）と衝突しないよう `f_` 接頭辞**
- キーワードは `f_q` で受け取り、内部で `s` にセットする（テンプレート判定が search.php に変わらないことを確認）
- `meta_value` で並べ替えるときは、名前付き `meta_query` 句を使い、メタが無い投稿が結果から消えないようにする

### 5-1. 商品（`/products/`、`product_type` / `product_tag` のアーカイブ）

| 変数 | 値 | 動作 |
|---|---|---|
| `f_type` | ターム slug | product_type で絞る |
| `f_tag` | ターム slug（カンマ区切りで複数可） | product_tag で絞る（AND） |
| `f_price` | `free` / `lt10000` / `10000-19999` / `gte20000` | `_shima_price_min` で範囲指定 |
| `f_sort` | `new`（既定）/ `price_asc` / `price_desc` | new は `_shima_latest_release` 降順→投稿日降順 |
| `f_q` | 文字列 | キーワード |

- 1ページ 9件

### 5-2. アプリ（`/apps/`、`platform` のアーカイブ）

| 変数 | 値 | 動作 |
|---|---|---|
| `f_platform` | ターム slug | platform で絞る |
| `f_sort` | `new`（既定） | 公開中→準備中の順、その中で `_shima_latest_release` 降順 |
| `f_q` | 文字列 | キーワード |

- 1ページ 12件

### 5-3. シリーズ（`/series/{slug}/`）

- 連載なので **投稿日の古い順**、1ページ 50件

### 5-4. 補助関数

- `shima_get_active_filters()`：現在かかっている条件を `[ ['var','value','label','remove_url'], ... ]` で返す（後で「選択中」チップと「条件をクリア」に使う）

---

## 6. ファイル構成（最終形）

```
style.css                 テーマ情報ヘッダのみ（CSSはまだ書かない）
functions.php             require_once のみ
index.php                 最小のループ（確認用）
inc/setup.php             テーマサポート・メニュー・画像サイズ
inc/enqueue.php           フォント・CSS 読み込み
inc/post-types.php        CPT
inc/taxonomies.php        タクソノミー
inc/activation.php        有効化時の処理
inc/fields.php            SCF フィールド定義
inc/field-sync.php        保存時の同期メタ
inc/template-functions.php 取得関数
inc/queries.php           一覧クエリ
assets/css/tokens.css     デザイントークン（:root 変数）
```

---

## 7. フェーズ計画

各フェーズの最後に `php -l` を全変更ファイルに実行し、報告フォーマットで報告して **停止** すること。

### Phase 0：読解と計画（コードは書かない）
- `CLAUDE.md` とこの指示書を読み、**不明点・矛盾・懸念を質問として列挙**する
- リポジトリの現状（既存ファイル、git の初期化状況）を報告する
- PHP のバージョン（`php -v`）を報告する
- ローカル WordPress の状況を報告する（読み取りのみ）
  - リポジトリが `wp-content/themes/001_shima/` の位置にあるか、それとも別の場所でシンボリックリンク等が必要か
  - WordPress 本体のバージョン、SCF プラグインの有無と有効・無効
  - WP-CLI が使えるか（`wp --info`）。使えない場合はその旨
- 完了条件：質問リストと現状報告のみ。ファイルの作成・変更ゼロ

### Phase 1：骨組み
- 触る：`style.css` `functions.php` `index.php` `inc/setup.php`
- `style.css`：Theme Name `Shima`、Text Domain `shima`、Version `0.1.0`
- `index.php`：`get_header()` 等は使わず、`wp_head()` / `wp_footer()` を含む最小HTML。ループでタイトル（リンク付き）と投稿タイプ名を表示するだけ
- `inc/setup.php`：title-tag / post-thumbnails / html5（search-form, gallery, caption, style, script）/ responsive-embeds、メニュー `primary`（グローバル）・`footer`（SNS）、画像サイズ `shima-card`（960×600 切り抜き）・`shima-shot`（600×1300 切り抜きなし）
- 完了条件：ローカル WordPress でテーマを有効化してエラーが出ない
- **ユーザー確認**：ローカル WP の「外観＞テーマ」で `Shima` を有効化 → トップと適当な記事が表示される

### Phase 2：アセット読み込み
- 触る：`inc/enqueue.php` `assets/css/tokens.css` `functions.php`（require 追加のみ）
- Google Fonts：IBM Plex Sans JP（400/500/700）、IBM Plex Mono（400/500）、`display=swap`、preconnect
- `style.css` と `tokens.css` をファイル更新時刻でバージョン付けして読み込む
- `tokens.css` は `DESIGN.md` の `:root` 変数を転記。**`DESIGN.md` が無い場合は、下記4色だけ入れて停止し、報告で知らせる**
  - `--color-text: #15191C` / `--color-text-sub: #5B6167` / `--color-surface: #DFE5E8` / `--color-accent: #E0B021`
- **ユーザー確認**：ページのソースでフォントとCSSの読み込みを確認

### Phase 3：CPT `product`
- 触る：`inc/post-types.php` `functions.php`
- 1-2 の表どおり。ラベルは日本語で一通り設定
- 完了条件：`with_front => false` が入っている
- **ユーザー確認**：管理画面に「商品」メニュー → ダミーを1件作成 → **設定＞パーマリンクで「変更を保存」** → `/products/` と `/products/{slug}/` が表示される

### Phase 4：CPT `app`
- 触る：`inc/post-types.php`
- **ユーザー確認**：Phase 3 と同じ手順で `/apps/` を確認

### Phase 5：タクソノミー 4つ
- 触る：`inc/taxonomies.php` `functions.php`
- 1-3 の表どおり（初期タームの投入は次フェーズ）
- **ユーザー確認**：各投稿の編集画面にタクソノミー欄が出る。ターム手動作成で `/product-type/{slug}/` が表示される

### ⭐ Phase 6：有効化時の処理
- 触る：`inc/activation.php` `functions.php`
- `after_switch_theme` で：CPT・タクソノミー登録 → 初期ターム（1-3）が無ければ作成 → `flush_rewrite_rules()` を1回
- 管理画面で、スラッグ `play` / `demo` の固定ページ・投稿・タームが存在したら警告通知を出す
- **ユーザー確認**：テーマを一度別テーマに切り替えて戻す → 初期タームが作成されている
- ⭐ ここで Phase 1〜6 の差分を外部レビューに出す

### Phase 7：取得関数レイヤーの土台
- 触る：`inc/template-functions.php` `functions.php`
- `shima_field()` と `shima_format_price()` のみ実装
- SCF が無効なとき、管理画面に「Secure Custom Fields を有効化してください」と通知
- **ユーザー確認**：SCF を一時停止しても画面が真っ白にならない

### Phase 8：フィールド定義 `product`
- 触る：`inc/fields.php` `functions.php`
- 2-1 の表どおり
- **ユーザー確認**：商品編集画面に全フィールドが出る。ダミー商品にプラン2つ・画像・機能・FAQを入力して保存できる

### Phase 9：フィールド定義 `app`
- 触る：`inc/fields.php`
- 2-2 の表どおり
- **ユーザー確認**：アプリ編集画面で入力・保存できる

### Phase 10：フィールド定義 `changelog` ＋ 形式チェック
- 触る：`inc/fields.php`
- 2-3 の表どおり。product と app の両方に表示
- **ユーザー確認**：`1.2` や `v1.2.3` で保存するとエラー、`1.2.3` なら通る

### ⭐ Phase 11：保存時の同期メタ
- 触る：`inc/field-sync.php` `functions.php`
- 3章どおり
- **ユーザー確認**：Claude Code が確認方法を提案すること（例：一時的な管理画面表示、または投稿編集画面の「カスタムフィールド」パネル。**確認用コードを入れた場合は同フェーズ内で必ず削除**）
- ⭐ ここで Phase 7〜11 の差分を外部レビューに出す

### Phase 12：取得関数 残り全部
- 触る：`inc/template-functions.php`
- 4章の表の残り全部
- **ユーザー確認**：`index.php` を一時的に使った確認は **しない**。代わりに各関数の想定入出力を報告に表で書く（ユーザーが目視レビュー）

### Phase 13：一覧クエリ（商品）
- 触る：`inc/queries.php` `functions.php`
- 5-1 どおり
- **ユーザー確認**：ダミー商品を3件（価格違い）用意 → `/products/?f_sort=price_asc` 等、報告に書かれたテスト用URL一覧を順に開いて並び・件数を確認

### ⭐ Phase 14：一覧クエリ（アプリ・シリーズ）＋ 補助関数
- 触る：`inc/queries.php`
- 5-2 〜 5-4 どおり
- **ユーザー確認**：Phase 13 と同様にテスト用URL一覧で確認
- ⭐ ここで Phase 12〜14 の差分を外部レビューに出す

### Phase 15：最終セルフレビュー（コード変更なし）
- 全ファイルを読み直し、次の観点で監査レポートを出す
  - エスケープ・サニタイズ漏れ
  - `get_field()` の直接呼び出しが `template-functions.php` 以外に無いか
  - 接頭辞 `shima_` の漏れ
  - 指示書との相違点
  - 次の指示書（テンプレート実装）へ引き継ぐべき事項
    - （Phase 2 で記録）WordPress 標準の絵文字スクリプト（wp-emoji-release / twemoji）の読み込み停止を検討する
- 修正が必要な点は **直さずに列挙のみ**。修正はユーザーの承認後に別コミットで
