//! expect: E0382
//! title: move した後の変数を使ってしまう
//! chapter: 06-ownership
//!
//! String は Copy ではないので、代入した時点で所有権が移る。
//! 移った後の元の変数は「もう空」なので、触るとコンパイルが止まる。

fn main() {
    let s1 = String::from("こんにちは");
    let s2 = s1; // ここで所有権が s1 から s2 へ移る

    println!("{s1}"); // s1 はもう使えない
    println!("{s2}");
}
