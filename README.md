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

## GitHub Pages の公開設定

`docs/` を公開ディレクトリとして使っています。

1. Settings → General → Change repository visibility → **Public**
   （private リポジトリでの Pages 公開は GitHub Pro/Team が必要なため）
2. Settings → Pages → Source: `Deploy from a branch`
   → Branch: `main` / フォルダ: `/docs` → Save
