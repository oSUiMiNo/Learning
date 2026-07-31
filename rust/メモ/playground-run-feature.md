# Rust 入門に「その場で実行」機能を足せるか（Rust Playground 調査）

| 内容 | 反映状況 |
| --- | --- |
| 初回 | [ ] |

## 1. 背景・目的

ユーザーから「VS Code を Web に埋め込むように、本文中のコードをその場で
実行できないか」という相談があり、調査だけ行った（**教材本体への実装はまだしていない**）。
Web 上でのコード実行が現実的か、コスト・制約は何かを確かめるのが目的。

調査は [rust-lang/rust-playground](https://github.com/rust-lang/rust-playground)
のソースコードを直接 fetch して読む形で行った。
**`play.rust-lang.org` そのものへは、この環境からネットワーク接続がブロックされて
おり（到達不能）、実機での動作確認は一切できていない。** 以下はすべて
「ソースコードに書かれている内容」であって、「実際にその通り動くことを確認した」
わけではない点に注意。

## 2. 実行 API の要点（ソースコードで確認）

`ui/src/public_http_api.rs` に定義されている HTTP API。

- ルート: `/execute`（実行）、`/compile`（アセンブリ等の生成）、`/evaluate.json`
  （旧形式）、`/format`（rustfmt）、`/clippy`、`/miri`、`/macro-expansion`、
  `/meta/crates`、`/meta/versions`、`/meta/gist`
- `/execute` のリクエストは概ね次のフィールドを持つ:
  - `channel`（`stable` / `beta` / `nightly`）
  - `mode`（`debug` / `release`）
  - `edition`（`2015` / `2018` / `2021` / `2024` など）
  - `crateType`（`bin` / `lib`）
  - `tests`（bool。テストとして実行するか）
  - `code`（ソース本文）
- レスポンスは `success` / `stdout` / `stderr` に加え、実行時間などを含む

## 3. CORS の制約（確認できたことと、できていないこと）

**ソースコードで確認したこと**: `ui/src/server_axum.rs` に
`.allow_origin(cors::Any)` という設定があり、これは
**`PLAYGROUND_CORS_ENABLED` という環境変数で有効化を切り替える作りになっている**
（コード上はそう読める）。つまり本番でこの環境変数が実際にどう設定されているか次第で、
ブラウザから直接 `fetch` できるかが変わる。

**確認できていないこと（重要）**:
- 本番の `play.rust-lang.org` が実際にどの CORS ヘッダーを返すかは、
  ブラウザ／`curl` 等での実測をしていない（接続がブロックされていたため）
- そのため「教材のページから直接 `fetch` できる」と断定することはまだできない

反映するなら、実装前に実測が必須。

## 4. 収録クレート版（`compiler/base/Cargo.toml` を読んで確認、調査日: 2026 年）

Playground が使えるクレートには制限があり、`CRATE_POLICY.md` によると
「ダウンロード数上位 100 + Rust Cookbook 掲載クレート」を基準に、
「だいたい 6 週間おき、Rust のリリースに合わせて」更新しているとのこと。

調査時点で `Cargo.toml` に確認できた版（あくまで調査時点のスナップショット。
Playground 側が更新されれば当然変わる）:

| クレート | 版 |
| --- | --- |
| rand | 0.10.2 |
| serde | 1.0.229 |
| serde_json | 1.0.151 |
| anyhow | 1.0.104 |
| clap | 4.6.3（`clap_builder` 4.6.2） |
| tokio | 1.53.1（`full` 等の feature 込み） |
| itertools | 0.15.0 |
| thiserror | 2.0.19 |

`clap` について: `unstable-doc` feature の存在は確認したが、
**`derive` feature が使えるかどうかまでは確認できていない。**

## 5. 教材への反映方針（未確定）

- 反映するとしても、**独自にサーバを立てる必要はなく、Playground の API を
  そのまま呼ぶ形が現実的**に見える（ただし 3 節の CORS 実測が先）
- 全章に入れる必要はなく、「試してみよう」的な章に限定する案が良さそう
- Playground はネットワーク依存になるため、**オフラインでは動かない**ことを
  本文に明記する必要がある

## 6. 未解決の疑問・次に調べること

- 本番エンドポイントへの実際のブラウザからの CORS 実測（最優先）
- `clap` の `derive` feature の可否
- エディタ部分（コード入力欄）に何を使うか。Monaco / CodeMirror / Ace を
  比較する調査を別途動かしたが、**その結果はまだ届いていない（未確認）**。
  届き次第、このメモに追記する形で反映する
- レートリミット・同時実行数の制約（ソース上は見当たらなかったが、
  運用上の制限が別途あるかもしれない）

## 7. 参考にした一次情報

- https://github.com/rust-lang/rust-playground （リポジトリ全体）
- `ui/src/public_http_api.rs`（リクエスト/レスポンス形状）
- `ui/src/server_axum.rs`（CORS 設定）
- `compiler/base/Cargo.toml`（収録クレート版）
- `CRATE_POLICY.md`（クレート選定・更新方針）
