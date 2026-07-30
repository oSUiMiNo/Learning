"""教材の章立て。ナビゲーション・目次・前後リンクはすべてここから生成される。

各章:
    slug     : 出力ディレクトリ名かつ URL（docs/rust/<slug>/index.html）
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
        lede="Rust が何のための言語で、なぜ「難しい」と言われるのか。"
             "そして C# が書けるあなたが、どこを速く飛ばし、どこで立ち止まるべきかを先に決めます。",
        minutes=9,
    ),
    dict(
        slug="01-setup",
        label="環境構築",
        title="第1章 環境構築 — Windows 11 に Rust を入れる",
        lede="rustup ひとつで、コンパイラもパッケージ管理も整形もぜんぶ入ります。"
             "Windows だけに必要な「もう 1 つの準備」も、つまずく前に片付けます。",
        minutes=13,
    ),
    dict(
        slug="02-editor",
        label="エディタの準備",
        title="第2章 エディタの準備 — rust-analyzer に働かせる",
        lede="Rust は「エディタが賢いと一気に楽になる」言語です。"
             "型を目で見えるようにして、コンパイル前に間違いを潰せる状態を作ります。",
        minutes=11,
    ),
    dict(
        slug="03-cargo",
        label="Cargo と最初の一本",
        title="第3章 Cargo と最初の一本 — dotnet CLI に相当するもの",
        lede="`cargo new` から `cargo run` まで。`Cargo.toml` は .csproj、"
             "crates.io は NuGet に当たります。エディションという Rust 独自の概念もここで。",
        minutes=13,
    ),
    dict(
        slug="04-variables",
        label="変数と型",
        title="第4章 変数と型 — 既定が不変であること",
        lede="C# との最大の違いは、変数が既定で書き換えられないことです。"
             "`var` と `let` は似て見えて、態度がまるで違います。",
        minutes=14,
    ),
    dict(
        slug="05-control-flow",
        label="関数と制御フロー",
        title="第5章 関数と制御フロー — ほとんどが「式」である",
        lede="`if` が値を返し、ブロックの最後の行が戻り値になります。"
             "C# の式形式メンバーが好きな人には、たぶん気持ちのいい章です。",
        minutes=12,
    ),
    dict(
        slug="06-ownership",
        label="★ 所有権",
        title="第6章 所有権 — GC のない世界の片付け方",
        lede="この教材でいちばん大事な章です。Rust に GC はなく、"
             "かわりに「値には所有者がひとりだけいる」という規則で寿命を決めます。",
        minutes=20,
    ),
    dict(
        slug="07-borrowing",
        label="★ 借用と参照",
        title="第7章 借用と参照 — 貸し借りの規則",
        lede="所有権を渡さずに値を使わせるのが借用です。"
             "「書き込みできる参照は同時に 1 つだけ」という一行が、データ競合を根こそぎ防ぎます。",
        minutes=18,
    ),
    dict(
        slug="08-strings",
        label="文字列",
        title="第8章 文字列 — String と &str、そして UTF-8",
        lede="C# の string は UTF-16、Rust の String は UTF-8 です。"
             "この違いのせいで「文字数の数え方」まで変わります。ここは早めに知るほど得をします。",
        minutes=15,
    ),
    dict(
        slug="09-structs",
        label="構造体と impl",
        title="第9章 構造体と impl — クラスがない代わりに",
        lede="Rust に class はありません。データは struct、ふるまいは impl に分けて書きます。"
             "そして継承がありません。その埋め合わせ方まで見ます。",
        minutes=14,
    ),
    dict(
        slug="10-enums",
        label="列挙型と match",
        title="第10章 列挙型と match — null が消える仕組み",
        lede="Rust の enum は値を持てます。だから `Option<T>` で「無いかもしれない」を"
             "型として表せて、null 参照例外という概念そのものが無くなります。",
        minutes=16,
    ),
    dict(
        slug="11-errors",
        label="エラー処理",
        title="第11章 エラー処理 — 例外のない世界",
        lede="失敗は投げるのではなく、戻り値で返します。`Result<T, E>` と `?` の 2 つで、"
             "try-catch と同じくらい短く書けます。",
        minutes=16,
    ),
    dict(
        slug="12-collections",
        label="コレクション",
        title="第12章 コレクション — Vec と HashMap",
        lede="`List<T>` は `Vec<T>`、`Dictionary<K,V>` は `HashMap<K,V>`。"
             "対応は素直ですが、借用の規則がここで初めて実戦になります。",
        minutes=13,
    ),
    dict(
        slug="13-iterators",
        label="イテレータ",
        title="第13章 イテレータとクロージャ — LINQ に似ている話",
        lede="`Where` は `filter`、`Select` は `map`。遅延評価まで同じです。"
             "この章はたぶん、C# 経験がいちばん効きます。",
        minutes=16,
    ),
    dict(
        slug="14-traits",
        label="★ トレイト",
        title="第14章 トレイトとジェネリクス — インターフェースとの違い",
        lede="トレイトはインターフェースによく似ていますが、"
             "「後から他人の型に実装できる」点が決定的に違います。単相化の話も避けずにやります。",
        minutes=18,
    ),
    dict(
        slug="15-lifetimes",
        label="★ ライフタイム",
        title="第15章 ライフタイム — 'a は何を言っているのか",
        lede="初心者がいちばん怖がる記法です。しかし正体は"
             "「この参照はいつまで有効か」をコンパイラに伝えるだけのもの。落ち着いて読めば短い話です。",
        minutes=16,
    ),
    dict(
        slug="16-modules",
        label="モジュールとクレート",
        title="第16章 モジュールとクレート — namespace との違い",
        lede="`mod` はファイル分割の仕組みでもあり、公開範囲の仕組みでもあります。"
             "既定が非公開なところが C# と違います。外部クレートの入れ方もここで。",
        minutes=13,
    ),
    dict(
        slug="17-testing",
        label="テストとドキュメント",
        title="第17章 テストとドキュメント — 標準で付いてくるもの",
        lede="テスト機構は言語に組み込みです。さらに「ドキュメントに書いた例が"
             "テストとして走る」仕組みまであります。この教材自身もそれに支えられています。",
        minutes=12,
    ),
    dict(
        slug="18-smart-pointers",
        label="スマートポインタ",
        title="第18章 スマートポインタ — Box, Rc, RefCell",
        lede="「所有者はひとりだけ」では書けない形が出てきたときの道具です。"
             "参照カウントと、実行時に借用を検査する仕組みを使い分けます。",
        minutes=15,
    ),
    dict(
        slug="19-concurrency",
        label="並行処理",
        title="第19章 並行処理 — 競合がコンパイルエラーになる",
        lede="Rust の売り文句「恐れなき並行性」の中身を見ます。"
             "所有権と借用の規則を、そのままスレッドに適用しただけだと分かります。",
        minutes=16,
    ),
    dict(
        slug="20-async",
        label="★ async / await",
        title="第20章 async / await — C# の Task と何が違うか",
        lede="見た目はそっくりですが、動き方が根本的に違います。"
             "Rust の Future は、誰かが await するまで 1 行も走りません。ここは必ず読んでください。",
        minutes=18,
    ),
    dict(
        slug="21-cli-app",
        label="実践: CLI ツール",
        title="第21章 実践 — CLI ツールを 1 本作って配る",
        lede="ここまでの全部入り。引数解析・ファイル読み書き・JSON・エラー処理を組み合わせて、"
             "単体で配布できる実行ファイルまで持っていきます。",
        minutes=22,
    ),
    dict(
        slug="99-pitfalls",
        label="つまずき集と次の一歩",
        title="付録 つまずき集と、次の一歩",
        lede="エラーコード早見表、古い記事との差分、そして unsafe・FFI・WebAssembly の入口。"
             "ここから先は自力で進めるための地図です。",
        minutes=17,
    ),
]

BOOK_TITLE = "Rust 入門"
BOOK_SUBTITLE = "C# が書ける人のための、所有権から async まで"
BOOK_DESCRIPTION = (
    "Windows 11 と最新の stable Rust で学ぶ、初心者向けの入門書。"
    "掲載コードはすべて実際にビルドして動作確認し、「コンパイルが通らない例」も"
    "実際に rustc に通してエラーコードまで確かめています。"
    "C# の知識をそのまま足がかりにできるよう、対応関係と"
    "「C# の直感が裏切られる箇所」を各章で名指しします。"
)
