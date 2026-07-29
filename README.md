# Learning

様々な技術などを学ぶための教材を格納する

## 教材一覧

| 教材 | 内容 | 公開ページ |
|---|---|---|
| [Qt6 Widgets 入門](qt6-widgets/) | Python (PySide6 6.11) でデスクトップ GUI を作る初心者向け入門書。全 14 章 | https://osuimino.github.io/Learning/ |

## この教材群の作り方

教材は「読み物」と「動くコード」を分けずに管理しています。

- 本文に載っているコードは、`examples/` にある **実際に実行可能なファイルそのもの** を読み込んで表示している
- スクリーンショットは、**その同じファイルを起動して撮影** したもの
- ビルド時にすべてのサンプルが自動で起動テストされる

そのため「本文とコードと画面写真が食い違う」ことが構造的に起きません。

## GitHub Pages の公開設定

`docs/` を公開ディレクトリとして使っています。

1. Settings → General → Change repository visibility → **Public**
   （private リポジトリでの Pages 公開は GitHub Pro/Team が必要なため）
2. Settings → Pages → Source: `Deploy from a branch`
   → Branch: `main` / フォルダ: `/docs` → Save
