# Qt6 Widgets 入門 — ソース

Python (PySide6 6.11) で Qt Widgets を学ぶ、初心者向けの入門書です。全 15 章。
公開ページ: https://osuimino.github.io/Learning/qt6-widgets/

> **この教材を直しに来た人へ。**
> 先に [../AUTHORING.md](../AUTHORING.md)（教材づくりの共通ルール）と
> [AUTHORING.md](AUTHORING.md)（この教材で実際に踏んだこと）を読んでください。
> とくに「本文の主張は実物で確かめてから書く」の理由は、
> 実例つきで書いてあるので目を通しておくと事故が減ります。

## この教材の作り

読み物とコードを別々に管理すると、必ずどこかで食い違います。
そこでこの教材では、**本文に載るコードと、スクリーンショットの元になるコードを同一のファイル**にしています。

```
qt6-widgets/
├── examples/     ★ コードの単一情報源。すべて単体で実行できる
│   └── cpp/      付録章の C++ 版。CMake でビルドして動作確認している
├── book/         本文（章ごとの HTML）と章立て定義 toc.py
├── assets/       style.css / book.js / 概念図の SVG
└── tools/        ビルドと検証のスクリプト
        ↓ 生成
../docs/qt6-widgets/   GitHub Pages で公開されるサイト
```

`docs/` の直下は教材一覧のハブになっています（リポジトリ直下の
`tools/build_hub.py` が生成）。各教材は自分の `tools/build.py` で
`docs/<教材名>/` を作ります。

本文中の `<!--code: ch02_hello.py-->` は、ビルド時に `examples/ch02_hello.py` の
中身をそのまま読み込んで構文強調します。書き写しは一切行いません。

## 読者として使う

サンプルはどれも単体で動きます。

```bash
pip install pyside6
python qt6-widgets/examples/ch02_hello.py
```

## 教材を更新する

```bash
pip install -r qt6-widgets/requirements-build.txt
cd qt6-widgets
```

| コマンド | やること |
|---|---|
| `python tools/check_examples.py` | 全サンプルを画面なしで起動し、エラーが出ないことを確認する |
| `python tools/check_claims.py` | 本文が主張している Qt5 → Qt6 の挙動を、実物の PySide6 で確かめる |
| `python tools/shots.py [絞り込み]` | Xvfb 上でサンプルを実際に動かし、スクリーンショットを撮り直す |
| `python tools/shots_cpp.py` | 付録の C++ サンプルをビルドして実行し、撮影する（Qt6 の C++ 環境がなければ自動で飛ばす） |
| `python tools/build.py` | `book/` と `examples/` から `../docs/qt6-widgets/` を生成する |
| `python tools/build.py --check` | 生成せずに、壊れている箇所だけを調べる |
| `python tools/preview.py` | 出来上がったサイトをブラウザで巡回して検証する |
| `python ../tools/build_hub.py` | 教材一覧のハブと旧 URL の転送ページを更新する（リポジトリ直下のスクリプト） |

典型的な流れは次のとおりです。

```bash
python tools/check_examples.py   # コードが動くか
python tools/check_claims.py     # 本文の「Qt5 ではこう、Qt6 ではこう」が事実か
python tools/shots.py            # 画面写真を撮り直す（コードを変えたとき）
python tools/build.py            # サイトを生成
python tools/preview.py          # ブラウザで検証
python ../tools/build_hub.py     # 教材一覧のハブを更新（章数などが変わったとき）
```

ハブに出している章数・通読時間・検証バージョンは `book/toc.py` と
`docs/qt6-widgets/assets/versions.json` から読んでいます。
そのため章を増やしたら `build_hub.py` も走らせてください。

### `tools/check_claims.py` を用意した理由

第13章の「Qt5 時代の記事との差分・早見表」は、本来いちばん間違えてはいけない表です。
にもかかわらず、この教材の初稿では 4 行が間違っていました。
`Qt.AlignCenter` や `app.exec_()` は「Qt6 ではエラーになる」と書いていたのですが、
実際には **PySide6 の寛容モードによって今も動きます**（`exec_()` は警告つき、enum は無警告）。
PyQt6 の挙動を PySide6 の話として書いてしまっていたのです。

Web の記事を読んで書くかぎり、この種の間違いは避けられません。
そこで表の各行を実物の PySide6 に対して実行して確かめ、
食い違ったら公開が止まるようにしています。

### `tools/preview.py` が調べていること

- JavaScript のコンソールエラーが出ていないか
- 404 になっている画像やリンクがないか
- 横スクロールが発生していないか（スマホ幅を含む）
- 展開されていない指示子や「未作成」の目印が残っていないか
- **表示されているコードが `examples/` の実ファイルと 1 文字も違わないか**

### スクリーンショットについて

撮影は Xvfb 上の実際の Qt で行い、2 倍解像度で撮って WebP に変換しています。
章をまたいで見た目を揃えるため、スタイルは `Fusion` に固定しています。

ウィンドウ枠（タイトルバー）は画像には焼き込まず、HTML/CSS 側で描いています。
そのための情報（実際のウィンドウタイトルとサイズ）は
撮影時に `docs/qt6-widgets/img/shots.json` へ書き出され、`build.py` が読みます。

`tools/shots.py` の `OUT_DIR` と `tools/build.py` の `DOCS` は
同じ場所を指していなければなりません。ずれると撮った画像を
`build.py` が見つけられず、「スクリーンショットが未生成」で止まります。

新しいスクリーンショットを足すときは、`tools/shots.py` の `SHOTS` に 1 行加えます。
撮影前にボタンを押しておきたい場合は `steps` に操作を書きます。

```python
shot("ch08-messagebox", "ch08_messagebox.py", steps=[
    {"action": "click", "target": "askButton", "ms": 400},
], note="QMessageBox の質問ダイアログ"),
```

`target` には、サンプル側で `setObjectName()` した名前を指定します。

## 章を追加する

1. `book/toc.py` の `CHAPTERS` に項目を足す
2. 同じ `slug` の名前で `book/<slug>.html` を作る
3. `python tools/build.py --check` で漏れがないか確認する

ナビゲーション・目次・前後リンクはすべて `toc.py` から生成されるので、
他のファイルを触る必要はありません。
