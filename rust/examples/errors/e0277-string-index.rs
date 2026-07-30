//! expect: E0277
//! title: 文字列を数字で添字アクセスできない
//! chapter: 08-strings
//!
//! C# なら s[0] で 1 文字取れる。Rust はこれを禁じている。
//! String は UTF-8 のバイト列で、1 文字が 1 バイトとは限らないため、
//! 「n 番目」が何を指すのか一意に決まらない。
//! だから .chars().nth(n) や .bytes() のように、
//! 何を数えたいのかを書かせる設計になっている。

fn main() {
    let text = String::from("こんにちは");

    let first = text[0]; // 数字での添字は用意されていない

    println!("{first}");
}
