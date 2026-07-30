//! expect: E0382
//! title: 関数に渡したら、呼び出し側では使えなくなる
//! chapter: 06-ownership
//!
//! 関数の引数も代入と同じで、所有権が移る。
//! C# で参照型を渡す感覚のままだと、ここで必ず一度つまずく。

fn consume(text: String) {
    println!("受け取った: {text}");
}

fn main() {
    let message = String::from("おはよう");

    consume(message); // ここで所有権が関数に移る
    consume(message); // 2 回目は渡すものが残っていない
}
