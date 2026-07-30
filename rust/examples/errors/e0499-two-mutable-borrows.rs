//! expect: E0499
//! title: 書ける参照は同時にひとつだけ
//! chapter: 07-borrowing
//!
//! 「&mut は排他」を破ったときのエラー。
//! 単一スレッドでも止められる点が大事で、これがそのまま
//! マルチスレッドのデータ競合防止にも効いてくる（第19章）。

fn main() {
    let mut count = 0;

    let a = &mut count;
    let b = &mut count; // 2 本目は作れない

    *a += 1;
    *b += 1;
}
