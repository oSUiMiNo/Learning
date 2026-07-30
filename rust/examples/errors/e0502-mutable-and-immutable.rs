//! expect: E0502
//! title: 読む参照が生きている間は、書く参照を作れない
//! chapter: 07-borrowing
//!
//! 借用の規則そのもの。読み手がいる最中に書き手を作らせない。
//! これが「イテレート中にコレクションを変更した」系のバグを根絶している。

fn main() {
    let mut numbers = vec![1, 2, 3];

    let first = &numbers[0]; // 読む借用が始まる
    numbers.push(4); // 中で &mut が必要になる → ぶつかる

    println!("最初の要素は {first}");
}
