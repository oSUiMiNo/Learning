//! expect: E0596
//! title: mut でない変数からは &mut を作れない
//! chapter: 07-borrowing
//!
//! 「中身を書き換えるメソッドを呼んだらエラーになった」の正体はこれ。
//! push は &mut self を要求するので、変数側にも mut が必要。

fn main() {
    let numbers = vec![1, 2, 3]; // mut が付いていない

    numbers.push(4); // push は &mut self を要求する

    println!("{numbers:?}");
}
