//! expect: E0004
//! title: match に漏れがあるとコンパイルが通らない
//! chapter: 10-enums
//!
//! C# の switch は分岐が漏れていても黙って通る（default が無ければ何もしない）。
//! Rust は網羅性を検査するので、enum に値を追加した瞬間に
//! 「対応し忘れている場所」が全部エラーとして挙がる。

enum Signal {
    Red,
    Yellow,
    Green,
}

fn action(signal: Signal) -> &'static str {
    match signal {
        Signal::Red => "止まる",
        Signal::Green => "進む",
        // Signal::Yellow を書き忘れている
    }
}

fn main() {
    println!("{}", action(Signal::Red));
}
