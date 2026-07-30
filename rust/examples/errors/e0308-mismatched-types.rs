//! expect: E0308
//! title: 数値型どうしでも、暗黙には変換されない
//! chapter: 04-variables
//!
//! C# は i32 → i64 を暗黙に広げてくれる。Rust は広げてもくれない。
//! 面倒に見えるが、桁あふれや精度落ちが黙って起きないという利点がある。

fn main() {
    let small: i32 = 100;
    let big: i64 = small; // i32 は i64 に自動では入らない

    println!("{big}");
}
