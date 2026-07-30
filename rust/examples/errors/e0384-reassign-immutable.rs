//! expect: E0384
//! title: mut を付けていない変数は書き換えられない
//! chapter: 04-variables
//!
//! C# の var は既定で書き換え可能。Rust の let は既定で不可。
//! 既定が逆であることを、最初に体で覚えるための例。

fn main() {
    let total = 10;
    println!("最初: {total}");

    total = 20; // mut がないので書き換えられない
    println!("あと: {total}");
}
