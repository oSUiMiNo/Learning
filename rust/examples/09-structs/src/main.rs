//! 構造体と impl。C# の class に当たるものを、データとふるまいに分けて書きます。

/// データの定義。derive で「よくある能力」を自動実装させる。
///   Debug   → {:?} で表示できる
///   Clone   → .clone() で複製できる
///   PartialEq → == で比べられる
#[derive(Debug, Clone, PartialEq)]
struct Book {
    title: String,
    pages: u32,
    read: bool,
}

/// ふるまいの定義。C# ならクラス本体に混ぜて書くところを、別のブロックにする。
impl Book {
    /// 関連関数。self を取らないので、C# の static メソッドに相当する。
    /// 慣習として new という名前を使うが、言語の予約語ではない。
    fn new(title: &str, pages: u32) -> Self {
        Self {
            title: title.to_string(),
            pages,
            read: false,
        }
    }

    /// &self を取るメソッド。読むだけ。
    fn is_long(&self) -> bool {
        self.pages > 300
    }

    /// &mut self を取るメソッド。自分を書き換える。
    fn finish(&mut self) {
        self.read = true;
    }

    /// self を取るメソッド。自分を消費して別の値になる。
    /// C# には対応するものがないので戸惑いやすいが、
    /// 「この値はもう使わせない」と表明できるのが利点。
    fn into_summary(self) -> String {
        format!("『{}』{} ページ", self.title, self.pages)
    }
}

/// タプル構造体。名前を付けたいだけのとき使う。
/// 単位を型で区別すると、取り違えがコンパイルエラーになる。
struct Yen(u32);
struct Dollar(u32);

/// フィールドを持たない構造体。ふるまいだけをまとめたいとき。
struct Formatter;

impl Formatter {
    fn line() -> String {
        "─".repeat(20)
    }
}

fn main() {
    println!("── 1. 作って使う ──");
    let mut book = Book::new("Rust 入門", 420);
    println!("  {book:?}");
    println!("  長い本か = {}", book.is_long());

    println!("\n── 2. 書き換える ──");
    book.finish(); // &mut self を渡すため、book は mut でなければならない
    println!("  読み終わった = {}", book.read);

    println!("\n── 3. 複製と比較 ──");
    let copy = book.clone();
    println!("  複製と等しいか = {}", book == copy);

    println!("\n── 4. 一部だけ変えて作る ──");
    // .. で「残りは元のものと同じ」と書ける。C# の with 式に近い。
    let sequel = Book {
        title: String::from("Rust 実践"),
        ..copy
    };
    println!("  {sequel:?}");

    println!("\n── 5. 型で単位を分ける ──");
    let price = Yen(1200);
    let fee = Dollar(8);
    // 足そうとすると型が違うのでコンパイルエラーになる。取り違えが起きない。
    println!("  {} 円 / {} ドル", price.0, fee.0);

    println!("\n── 6. self を消費するメソッド ──");
    println!("  {}", Formatter::line());
    println!("  {}", book.into_summary());
    // ここで book はもう使えない。into_summary が所有権を持っていったため。
    println!("  {}", Formatter::line());
}
