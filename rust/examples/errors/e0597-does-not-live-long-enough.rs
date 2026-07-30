//! expect: E0597
//! title: 借りた先が自分より先に消える
//! chapter: 15-lifetimes
//!
//! C や C++ ならダングリングポインタになり、
//! うまくいけば動き、運が悪いとおかしな値を読む。
//! Rust はこれをコンパイル時に止める。

fn main() {
    let outer;

    {
        let inner = String::from("短い命");
        outer = &inner; // inner はこのブロックの終わりで消える
    }

    println!("{outer}"); // 消えたものを見ようとしている
}
