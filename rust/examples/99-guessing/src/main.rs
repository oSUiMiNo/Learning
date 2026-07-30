//! 数当てゲーム。Rust 入門の定番題材を、いまの rand で書いたもの。
//!
//! ネット上の記事はほとんどが rand 0.8 の書き方（thread_rng / gen_range）で、
//! そのまま写すと動きません。付録の早見表で詳しく扱います。
//!
//! ここでは自動で当てにいく形にしてあります。
//! 標準入力から読む形にすると、そのままでは自動確認ができないためです。
//! 人が遊ぶ形にするには、下の `guess` を作っている行を
//! 標準入力の読み取りに差し替えてください（本文に手順があります）。

use std::cmp::Ordering;

// これが今の書き方。random_range は RngExt トレイトのメソッドなので、
// これを import する。`use rand::Rng;` では生えないので注意。
use rand::RngExt;

fn main() {
    let mut rng = rand::rng();
    let secret = rng.random_range(1..=100);

    println!("1 から 100 の数を当ててください");

    // 二分探索で当てにいく。人が遊ぶときの「だんだん絞る」動きと同じ。
    let mut low = 1;
    let mut high = 100;

    for attempt in 1..=10 {
        let guess = (low + high) / 2;
        print!("{attempt} 回目: {guess} → ");

        // match で 3 つの結果を漏れなく扱う。ここが Rust らしい部分。
        match guess.cmp(&secret) {
            Ordering::Less => {
                println!("small（もっと大きい）");
                low = guess + 1;
            }
            Ordering::Greater => {
                println!("big（もっと小さい）");
                high = guess - 1;
            }
            Ordering::Equal => {
                println!("正解");
                println!("\n{attempt} 回で当てました（答えは {secret}）");
                return;
            }
        }
    }

    println!("\n当てられませんでした（答えは {secret}）");
}
