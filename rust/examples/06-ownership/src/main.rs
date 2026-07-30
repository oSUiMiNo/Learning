//! 所有権のふるまいを、実際に動かして目で見るためのサンプル。
//!
//! 「値には所有者がひとりだけいて、所有者がいなくなったら片付けられる」
//! という規則が、どこで働いているかを順に確かめます。

/// スコープを抜けるときに何が起きるかを見せるための型。
/// C# の IDisposable に相当する後片付けが、Rust では Drop になる。
struct Receipt {
    label: String,
}

impl Drop for Receipt {
    fn drop(&mut self) {
        // ここは自分で呼ばない。所有者がいなくなった時点で自動的に呼ばれる。
        println!("  [drop] {} を片付けました", self.label);
    }
}

/// 引数で String を受け取る = 所有権をもらう。
/// 関数が終わるとここで片付けられるので、呼び出し側にはもう返らない。
fn consume(text: String) {
    println!("  もらった: {text}");
}

/// 参照で受け取る = 借りるだけ。呼び出し側の所有権はそのまま。
fn peek(text: &str) {
    println!("  見せてもらった: {text}（長さ {} バイト）", text.len());
}

/// 所有権をもらって、加工してから返す。
fn shout(mut text: String) -> String {
    text.push('!');
    text
}

fn main() {
    println!("── 1. Copy される型 ──");
    // i32 はスタックに収まる固定サイズなので、代入は「複製」になる。
    // 元の変数もそのまま使える。C# の値型と同じ感覚でよい。
    let a = 10;
    let b = a;
    println!("  a = {a}, b = {b}（どちらも使える）");

    println!("\n── 2. move される型 ──");
    // String は中身がヒープにあるので、代入は「引っ越し」になる。
    let s1 = String::from("こんにちは");
    let s2 = s1;
    // ここで s1 を使うとコンパイルエラー（E0382）。
    // examples/errors/e0382-use-after-move.rs で実際に確かめている。
    println!("  s2 = {s2}（s1 はもう使えない）");

    println!("\n── 3. clone すれば両方残る ──");
    let original = String::from("複製したい");
    let copy = original.clone();
    println!("  original = {original}");
    println!("  copy     = {copy}");

    println!("\n── 4. 関数に渡すと所有権も渡る ──");
    let given = String::from("あげる文字列");
    consume(given);
    // ここで given を使うとエラーになる。渡した先で片付けられたから。

    println!("\n── 5. 参照なら渡しても残る ──");
    let kept = String::from("貸すだけの文字列");
    peek(&kept);
    println!("  呼び出し側でもまだ使える: {kept}");

    println!("\n── 6. もらって返せば戻ってくる ──");
    let word = String::from("やった");
    let word = shout(word);
    println!("  返ってきた: {word}");

    println!("\n── 7. スコープと片付け ──");
    {
        let _inner = Receipt {
            label: String::from("内側のブロックの値"),
        };
        println!("  ブロックの中にいます");
    } // ここで _inner の所有者がいなくなり、drop が呼ばれる
    println!("  ブロックを抜けました");

    let _outer = Receipt {
        label: String::from("main の値"),
    };
    println!("\n  main の終わりに向かいます");
    // _outer はこの後、main が終わるときに片付けられる
}
