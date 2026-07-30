//! expect: E0106
//! title: 参照を返すのに、どこから借りたか書いていない
//! chapter: 15-lifetimes
//!
//! 引数が 2 つあると、返す参照がどちらから来たのか
//! コンパイラには決められない。だから 'a を書いて教える必要がある。
//! 「ライフタイムを書かされる」典型的な場面はこれ。

fn longer(a: &str, b: &str) -> &str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let left = String::from("うさぎ");
    let right = String::from("かめ");
    println!("{}", longer(&left, &right));
}
