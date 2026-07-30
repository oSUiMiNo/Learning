//! 文字列と UTF-8 のふるまいを確かめるサンプル。
//!
//! C# の string は UTF-16、Rust の String は UTF-8。
//! だから「長さ」の意味が食い違う。ここを実際の数字で確認します。

fn main() {
    let text = String::from("こんにちは");

    println!("── 1. 「長さ」が 3 種類ある ──");
    println!("  文字列: {text}");
    println!("  len()            = {} ← バイト数", text.len());
    println!("  chars().count()  = {} ← 文字数", text.chars().count());
    println!(
        "  encode_utf16()   = {} ← C# の Length と同じ数",
        text.encode_utf16().count()
    );

    println!("\n── 2. 文字によってバイト数が違う ──");
    for c in ['A', 'あ', '漢', '🦀'] {
        println!(
            "  {c}  UTF-8 で {} バイト / UTF-16 で {} 単位",
            c.len_utf8(),
            c.len_utf16()
        );
    }

    println!("\n── 3. 絵文字は C# だと 2 に数えられる ──");
    let crab = "🦀";
    println!("  {crab}");
    println!("  Rust の chars().count()      = {}", crab.chars().count());
    println!(
        "  C# の Length に相当する値    = {}",
        crab.encode_utf16().count()
    );
    println!("  ← C# ではサロゲートペアで 2 になる。ここが食い違いの元");

    println!("\n── 4. n 文字目の取り出し方 ──");
    // text[2] のような添字は使えない（E0277）。何を数えるか明示する。
    if let Some(third) = text.chars().nth(2) {
        println!("  3 文字目 = {third}");
    }

    println!("\n── 5. String と &str ──");
    let owned: String = String::from("持っている文字列");
    let borrowed: &str = &owned; // 借りているだけ
    let literal: &str = "ソースに直接書いた文字列";
    println!("  String  = {owned}");
    println!("  &str    = {borrowed}");
    println!("  リテラル = {literal}");
    println!("  リテラルは実行ファイルに埋め込まれているので確保も解放も要らない");

    println!("\n── 6. つなげる・分ける ──");
    let mut building = String::new();
    building.push_str("Rust");
    building.push(' ');
    building += "入門";
    println!("  組み立てた = {building}");

    let csv = "赤,青,黄";
    let parts: Vec<&str> = csv.split(',').collect();
    println!("  分割した   = {parts:?}");
    println!("  分割しても中身の複製は起きていない（どれも元の文字列への窓）");

    println!("\n── 7. 書記素という第 4 の数え方 ──");
    // 「か」＋濁点のように、見た目 1 文字が複数の char になることもある。
    let ka = "か\u{3099}"; // か + 結合用濁点
    println!("  見た目          = {ka}");
    println!(
        "  chars().count() = {} ← 目には 1 文字に見えるのに 2",
        ka.chars().count()
    );
    println!("  正確に数えたいときは unicode-segmentation クレートを使う");
}
