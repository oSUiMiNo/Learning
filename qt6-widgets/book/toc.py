"""教材の章立て。ナビゲーション・目次・前後リンクはすべてここから生成される。

各章:
    slug     : 出力ディレクトリ名かつ URL（docs/<slug>/index.html）
    label    : サイドバーに出す短い見出し
    title    : ページの見出し
    lede     : 表紙と章頭に出す 1〜2 文の要約
    minutes  : 読了目安（分）
"""

CHAPTERS = [
    dict(
        slug="00-intro",
        label="はじめに",
        title="はじめに — この教材の歩き方",
        lede="Qt とは何か、なぜ PySide6 と Qt Widgets なのか、そして"
             "「ネットの記事どおりに書いたのに動かない」がなぜ起きるのかを先に片付けます。",
        minutes=7,
    ),
    dict(
        slug="01-setup",
        label="環境構築",
        title="第1章 環境構築 — 3 分で始める",
        lede="Python さえ入っていれば、Qt の準備は pip コマンド 1 行で終わります。"
             "つまずきやすい仮想環境の話も含めて確実に通します。",
        minutes=8,
    ),
    dict(
        slug="02-first-window",
        label="最初のウィンドウ",
        title="第2章 最初のウィンドウ — イベントループを理解する",
        lede="たった 6 行のコードを題材に、Qt アプリが動き続ける仕組み"
             "「イベントループ」を最初に押さえます。ここが分かると後が全部楽になります。",
        minutes=10,
    ),
    dict(
        slug="03-signals",
        label="シグナルとスロット",
        title="第3章 シグナルとスロット — 部品どうしをつなぐ",
        lede="「ボタンが押されたら何かする」を Qt はどう表現するのか。"
             "Qt のいちばんの発明であり、Qt6 で書き方が変わった部分でもあります。",
        minutes=12,
    ),
    dict(
        slug="04-layouts",
        label="レイアウト",
        title="第4章 レイアウト — 部品の並べ方",
        lede="この教材でいちばん大事な章です。座標を指定しないのが Qt 流。"
             "縦・横・格子・フォームの 4 つと「伸び縮みの配分」を覚えれば大半の画面は作れます。",
        minutes=18,
    ),
    dict(
        slug="05-widgets",
        label="ウィジェット図鑑",
        title="第5章 ウィジェット図鑑 — よく使う部品カタログ",
        lede="ボタン・入力欄・選択肢・表示・まとめ役。実際の画面写真つきで"
             "「やりたいことに対してどれを使うか」が引けるカタログです。",
        minutes=14,
    ),
    dict(
        slug="06-mainwindow",
        label="ウィンドウの骨格",
        title="第6章 ウィンドウの骨格 — QMainWindow",
        lede="メニューバー、ツールバー、ステータスバー、ドック。"
             "「アプリらしいアプリ」の枠組みは QMainWindow が用意してくれています。",
        minutes=12,
    ),
    dict(
        slug="07-object-tree",
        label="親子関係とメモリ",
        title="第7章 親子関係とメモリ — 消えるウィンドウの謎",
        lede="「ウィンドウを出したのに一瞬で消える」「なぜか落ちる」。"
             "Python と Qt でオブジェクトの寿命の考え方が違うことが原因です。",
        minutes=10,
    ),
    dict(
        slug="08-dialogs",
        label="ダイアログ",
        title="第8章 ダイアログ — 確認・入力・ファイル選択",
        lede="メッセージボックスとファイル選択は 1 行で呼べます。"
             "自作ダイアログと、モーダル／モードレスの違いまで押さえます。",
        minutes=12,
    ),
    dict(
        slug="09-designer",
        label="Qt Designer",
        title="第9章 Qt Designer — 画面をマウスで作る",
        lede="コードを書かずに画面を組み立てるツールが標準で付いてきます。"
             "作った .ui ファイルを Python から使う 2 つの方法を比べます。",
        minutes=12,
    ),
    dict(
        slug="10-model-view",
        label="モデル / ビュー",
        title="第10章 モデル / ビュー — 表やリストを扱う",
        lede="Qt 入門者が最初にぶつかる壁。"
             "「データ」と「見せ方」を分けるという考え方さえ掴めれば、実は素直な仕組みです。",
        minutes=16,
    ),
    dict(
        slug="11-styling",
        label="見た目を整える",
        title="第11章 見た目を整える — スタイルシートとテーマ",
        lede="Qt は CSS によく似た記法で見た目を変えられます。"
             "ダークテーマ、アイコン、高解像度ディスプレイ対応まで。",
        minutes=13,
    ),
    dict(
        slug="12-todo-app",
        label="実践: ToDo アプリ",
        title="第12章 実践 — ToDo アプリを 1 本作る",
        lede="ここまでの全部入り。保存機能つきの ToDo アプリを、"
             "設計の考え方から順に組み上げて完成させます。",
        minutes=20,
    ),
    dict(
        slug="13-pitfalls",
        label="つまずき集と次の一歩",
        title="第13章 つまずき集と、次の一歩",
        lede="Qt5 時代の記事との差分早見表、PyQt6 との違い、配布方法、"
             "そして公式ドキュメントの歩き方。ここから先は自力で進めます。",
        minutes=10,
    ),
    dict(
        slug="14-cpp",
        label="付録: C++ の場合",
        title="付録 C++ でやるなら — 何がそのままで、何が違うか",
        lede="「Python で書いたところを、そのまま C++ で書けばいいの？」への答え。"
             "結論から言えば大部分はそのままですが、質的に違うものが 5 つあります。",
        minutes=14,
    ),
]

BOOK_TITLE = "Qt6 Widgets 入門"
BOOK_SUBTITLE = "Python (PySide6) ではじめるデスクトップ GUI"
BOOK_DESCRIPTION = (
    "PySide6 6.11 と Qt 6.11 で学ぶ、Qt Widgets の初心者向け入門書。"
    "掲載コードはすべて実際に実行して動作確認され、スクリーンショットも"
    "そのコードを動かして撮影しています。"
)
