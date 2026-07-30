# Learning

様々な技術などを学ぶための教材を格納する

公開ページ（教材一覧）: https://osuimino.github.io/Learning/

## 教材一覧

| 教材 | 内容 | 公開ページ |
|---|---|---|
| [Rust 入門](rust/) | C# が書ける人のための Rust 入門書。所有権から async まで。全 23 章 | https://osuimino.github.io/Learning/rust/ |
| [Qt6 Widgets 入門](qt6-widgets/) | Python (PySide6 6.11) でデスクトップ GUI を作る初心者向け入門書。全 15 章 | https://osuimino.github.io/Learning/qt6-widgets/ |

## この教材群の作り方

教材は「読み物」と「動くコード」を分けずに管理しています。

- 本文に載っているコードは、`examples/` にある **実際に実行可能なファイルそのもの** を読み込んで表示している
- 画面や出力は、**その同じコードを動かして得たもの**
- ビルド時にすべてのサンプルが自動で検証され、1 つでも壊れていれば公開できない

そのため「本文とコードと画面が食い違う」ことが構造的に起きません。

教材ごとに、その分野に合った担保のしかたを使っています。

| 教材 | 何を実測しているか |
|---|---|
| Qt6 Widgets | サンプルを Xvfb 上で起動してスクリーンショットを撮影。<br>本文が主張する Qt5 → Qt6 の挙動差を実物の PySide6 で検証 |
| Rust | コマンドを擬似端末で走らせて ANSI 付き出力を捕獲。<br>**「コンパイルが通らない例」のエラーコードを rustc で検証**。<br>**外部クレートの API についての記述を、実際に取得してコンパイルして検証** |

詳しくは各教材の README を見てください。

## ディレクトリ構成

```
Learning/
├── docs/              GitHub Pages で公開されるサイト（生成物。コミット済み）
│   ├── index.html         教材一覧のハブ
│   ├── rust/              Rust 入門
│   ├── qt6-widgets/       Qt6 Widgets 入門
│   └── <旧 slug>/         Qt6 本がルートに居た時代の URL からの転送
├── rust/              Rust 入門のソース
├── qt6-widgets/       Qt6 Widgets 入門のソース
└── tools/
    └── build_hub.py   教材一覧と旧 URL の転送ページを生成する
```

各教材は自分の `tools/build.py` で `docs/<教材名>/` を生成します。
`tools/build_hub.py` は教材をまたぐ部分（一覧ページと転送）だけを受け持ちます。

3 冊目を足すときは、`tools/build_hub.py` の `BOOKS` に 1 項目加えれば一覧に並びます。
章数・通読時間・検証バージョンは各教材の `book/toc.py` と
`docs/<教材名>/assets/versions.json` から自動で読むので、手で書く必要はありません。

### 旧 URL からの転送

Qt6 Widgets 入門は、2 冊目を足すまで**公開ルートに置かれていました**。
そのため次のような URL が外部に出ている可能性があります。

```
https://osuimino.github.io/Learning/03-signals/     ← 旧
https://osuimino.github.io/Learning/qt6-widgets/03-signals/   ← 新
```

既存のリンクを切らないよう、旧パス 15 本に転送ページを置いています。
`<meta http-equiv="refresh">` と `<link rel="canonical">` を書いただけの
薄い HTML で、JavaScript を切っていても手で辿れるリンクを添えてあります。

転送するパスの一覧は `tools/build_hub.py` の `LEGACY_QT6_SLUGS` が情報源です。
教材を移動・改名したときは、ここに追記してください。

なお生成された HTML の中のリンクはすべて相対パスなので、
教材ディレクトリごと移しても内部リンクは壊れません。

## 公開前に走らせるもの

教材を触ったら、公開前にこの順で走らせます。
どれか 1 つでも落ちたら、その時点で直してください。

```bash
pip install -r qt6-widgets/requirements-build.txt
pip install -r rust/requirements-build.txt
```

### 1. 中身が正しいかを実物で確かめる

```bash
# Qt6 Widgets 入門
python qt6-widgets/tools/check_examples.py   # 全サンプルが起動するか
python qt6-widgets/tools/check_claims.py     # 本文の Qt5 → Qt6 の記述が事実か

# Rust 入門
python rust/tools/check_examples.py          # build / test / run / fmt / clippy
python rust/tools/check_errors.py            # 「通らない例」が宣言どおりのエラーで落ちるか
python rust/tools/check_crates.py            # 外部クレートの API についての記述が実物と合うか
```

### 2. 素材を撮り直す（コードを変えたときだけ）

```bash
python qt6-widgets/tools/shots.py            # Xvfb 上で実行してスクリーンショット
python rust/tools/capture.py                 # コマンドを実行して端末出力を捕獲
```

### 3. サイトを組み立てる

```bash
python qt6-widgets/tools/build.py --check    # 先に壊れた箇所だけ調べる
python rust/tools/build.py --check
python qt6-widgets/tools/build.py
python rust/tools/build.py
python tools/build_hub.py                    # 教材一覧と旧 URL 転送
```

### 4. ブラウザで検証する

```bash
python qt6-widgets/tools/preview.py          # 明暗 2 テーマ × デスクトップ/スマホ幅
python rust/tools/preview.py
python -m http.server -d docs 8000           # 目視確認
```

`preview.py` は JavaScript のコンソールエラー・404・横スクロール・
未展開の指示子を検出し、さらに**表示されているコードが `examples/` の
実ファイルと 1 バイトも違わないこと**を確かめます。
Rust 側はこれに加えて、ターミナル枠に「実測」か「再現」のバッジが
付いていることも検査します。

## GitHub Pages の公開設定

`docs/` を公開ディレクトリとして使っています。

1. Settings → General → Change repository visibility → **Public**
   （private リポジトリでの Pages 公開は GitHub Pro/Team が必要なため）
2. Settings → Pages → Source: `Deploy from a branch`
   → Branch: `main` / フォルダ: `/docs` → Save
