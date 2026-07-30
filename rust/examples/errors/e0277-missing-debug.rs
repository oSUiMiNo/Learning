//! expect: E0277
//! title: 表示のしかたを教えていない型は {:?} で出せない
//! chapter: 09-structs
//!
//! C# はどんなオブジェクトでも ToString() を持っているので必ず何か出る。
//! Rust は「表示できる」という能力もトレイトで明示する必要がある。
//! #[derive(Debug)] を 1 行足せば直る。

struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    println!("{p:?}"); // Debug を実装していない
}
