# Rust 入門 — ソース

C# が書ける人のための、Rust の初心者向け入門書です。全 23 章。
公開ページ: https://osuimino.github.io/Learning/rust/

## この教材の作り

読み物とコードを別々に管理すると、必ずどこかで食い違います。
そこでこの教材では、**本文に載るものすべてを「実物」から生成**しています。

```
rust/
├── examples/     ★ コードの単一情報源。ワークスペースになっている
│   ├── NN-name/      章ごとの Cargo プロジェクト。単体で cargo run できる
│   └── errors/       「わざとコンパイルが通らない」コード。期待エラーコード付き
├── outputs/      ★ 実際に走らせて捕獲した ANSI 付きターミナル出力
├── book/         本文（章ごとの HTML）、章立て定義 toc.py、再現画面 repro.py
├── assets/       style.css / book.js / 概念図の SVG 24 枚
└── tools/        ビルドと検証のスクリプト
        ↓ 生成
../docs/rust/     GitHub Pages で公開されるサイト
```

本文中の `<!--code: 06-ownership/src/main.rs-->` は、ビルド時に
`examples/06-ownership/src/main.rs` の中身をそのまま読み込んで構文強調します。
書き写しは一切行いません。

### Qt6 の教材との違い

1 冊目（`qt6-widgets/`）は GUI なので画面写真を撮れました。
Rust には見せる GUI がないので、代わりに次の 2 つで担保しています。

| Qt6 の教材 | この教材 |
|---|---|
| サンプルを起動してスクリーンショットを撮る | **コマンドを実際に走らせて ANSI 付き出力を捕獲する** |
| `check_claims.py` で PySide6 の挙動を実測 | **`check_errors.py` で「通らない例」のエラーコードを実測**<br>**`check_crates.py` で外部クレートの API を実測** |

## 本文で使える指示子

| 指示子 | 展開されるもの |
|---|---|
| `<!--code: 06-ownership/src/main.rs-->` | `examples/` の実ファイルを構文強調して差し込む |
| `<!--figure: move \| キャプション-->` | `assets/figures/move.svg` を inline 展開 |
| `<!--term: err-e0382 \| キャプション-->` | **実測**の出力（実測バッジが付く） |
| `<!--termx: rustup-init \| キャプション-->` | **再現**の画面（再現バッジと出典が付く） |
| `<div class="src" data-lang="rust" data-file="...">` | 本文に直書きした短いコード |

囲みは `.note`（💡ヒント）/ `.note.pitfall`（⚠️つまずき）/
`.note.deep`（🔍もっと詳しく）/ `.note.try`（✅やってみよう）/
**`.note.csharp`（C# ならこう書く）** の 5 種類。最後のものはこの教材で追加したものです。

## 読者として使う

サンプルはどれも単体で動きます。

```powershell
cd rust/examples/06-ownership
cargo run
```

## 教材を更新する

```powershell
pip install -r rust/requirements-build.txt
cd rust
```

| コマンド | やること |
|---|---|
| `python tools/check_examples.py` | 全サンプルを build / test / run / fmt / clippy で確認する |
| `python tools/check_errors.py` | **「通らない例」が宣言どおりのエラーコードで落ちるか確かめる** |
| `python tools/check_crates.py` | **外部クレートの API についての記述を、実物で確かめる** |
| `python tools/capture.py [絞り込み]` | コマンドを実際に走らせて出力を撮り直す |
| `python tools/build.py` | `book/` と `examples/` と `outputs/` から `../docs/rust/` を生成する |
| `python tools/build.py --check` | 生成せずに、壊れている箇所だけを調べる |
| `python tools/preview.py` | 出来上がったサイトをブラウザで巡回して検証する |
| `python ../tools/build_hub.py` | 教材一覧のハブと旧 URL の転送ページを更新する（リポジトリ直下のスクリプト） |

典型的な流れは次のとおりです。

```powershell
python tools/check_examples.py   # コードが動くか
python tools/check_errors.py     # 「通らない例」が本当に通らないか
python tools/check_crates.py     # クレートの記述が実物と合っているか
python tools/capture.py          # 出力を撮り直す（コードを変えたとき）
python tools/build.py            # サイトを生成
python tools/preview.py          # ブラウザで検証
python ../tools/build_hub.py     # 教材一覧のハブを更新（章数などが変わったとき）
```

ハブに出している章数・通読時間・検証バージョンは `book/toc.py` と
`docs/rust/assets/versions.json` から読んでいます。
そのため章を増やしたら `build_hub.py` も走らせてください。

### `tools/check_errors.py` を用意した理由

Rust の入門書では「これはコンパイルエラーになります」という例が主役になります。
ところがこの手の記述は、言語の変化でいちばん先に嘘になります。
借用検査が賢くなって通るようになったり、エラーコードが変わったりするからです。

そこで `examples/errors/*.rs` の先頭に期待するエラーコードを書いておき、
実際に `rustc --error-format=json` に食わせて突き合わせています。

```rust
//! expect: E0382
//! title: move した後の変数を使ってしまう
//! chapter: 06-ownership
```

`expect: ok` と書けば「通ること」を確かめられます。
第 7 章の非語彙的ライフタイム（NLL）の説明は、これを使って
「昔はエラーだったが、いまは通る」ことを実測で示しています。

### `tools/check_crates.py` を用意した理由

初稿を書く時点で、`rand` クレートの最新版を **0.9.5 と誤認していました。**
実際に `cargo add rand` を走らせたら **0.10.2** が入り、
しかも「いまの正しい書き方」も想定と違っていました。

| 版 | 書き方 | 結果 |
|---|---|---|
| 0.8（記事に最も多い） | `rand::thread_rng().gen_range(..)` | `E0425` |
| 0.9 | `use rand::Rng;` + `rng().random_range(..)` | `E0599` |
| **いま** | `use rand::RngExt;` + `rng().random_range(..)` | 通る |

Web の情報や記憶で書くかぎり、この種の間違いは避けられません。
そこで付録の「古い記事との差分」の各行を、
実際にクレートを取得してコンパイルして確かめています。食い違えば公開が止まります。

### 実測と再現について

ターミナル画面には必ず **実測** か **再現** のバッジが付きます。
バッジが付いていない枠があると `tools/preview.py` が検出して落とします。

- **実測** … 擬似端末 (pty) 上でコマンドを実際に走らせて捕獲したもの。
  cargo も rustc も「人間が見ている」と判断して色を付けるので、
  ANSI エスケープごと保存し、ビルド時に色付き HTML へ変換しています。
  配色は Windows コンソールの既定（Campbell）に合わせてあります。
- **再現** … Windows のインストーラのように、この環境では出せない画面。
  `book/repro.py` に定義し、**何に基づく再現かをキャプションに必ず出します**。
  rustup の表示は rustup 自身のソース（表示文字列の定義そのもの）から取っています。

捕獲は Linux 上で行っているため、**パスの見た目だけ**を Windows 形式に直しています。

| 直すもの | 例 |
|---|---|
| 一時作業ディレクトリ | `/tmp/xxxx` → `C:\rust` |
| 実行ファイルのパス | `target/debug/hello` → `target\debug\hello.exe` |
| クレートの展開先 | `~/.cargo/registry/...` → `C:\Users\you\.cargo\registry\...` |

エラーメッセージ本文・バージョン番号・コンパイル時間・警告の内容は一切いじりません。

`rustup show` は実際に走らせられますが、この環境で撮ると host triple が
`x86_64-unknown-linux-gnu` になり Windows の読者にとって誤りになるため、
実測では扱わず再現として置いています。

## 章を追加する

1. `book/toc.py` の `CHAPTERS` に項目を足す
2. 同じ `slug` の名前で `book/<slug>.html` を作る
3. `python tools/build.py --check` で漏れがないか確認する

ナビゲーション・目次・前後リンクはすべて `toc.py` から生成されるので、
他のファイルを触る必要はありません。

## サンプルを追加する

```powershell
cd rust/examples
cargo new --vcs none --name chNN_name NN-name
```

作ったら `examples/Cargo.toml` の `members` に足してください。
ワークスペースにまとめているのは `target/` を 1 か所に集めて
ディスクとビルド時間を節約するためだけで、学習上の意味はありません。
各フォルダはそのままコピーして持ち出しても単体で動きます。
