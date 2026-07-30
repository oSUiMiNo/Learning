//! expect: E0505
//! title: 貸している最中に引っ越せない
//! chapter: 07-borrowing
//!
//! 借用が生きている間は、元の値を move できない。
//! move してしまうと、借用が指す先が無くなるため。

fn main() {
    let text = String::from("貸出中");

    let borrowed = &text; // text を借りている
    let moved = text; // 借用が生きているのに引っ越そうとしている

    println!("{borrowed} / {moved}");
}
