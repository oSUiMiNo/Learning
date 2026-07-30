//! async / await。C# の Task との違いを、実際の動きで確かめます。
//!
//! いちばん大事な違いは 1 行で言えます。
//!   C#   … async メソッドを呼んだ時点で、もう走り始めている
//!   Rust … await されるまで、1 行も走らない
//!
//! この違いがあるので、Rust には「呼んだけど await していない」状態が
//! 意味を持ちます。C# ならそれは「投げっぱなし」ですが、Rust では「未着手」です。

use std::time::{Duration, Instant};
use tokio::time::sleep;

/// async fn は「Future を返す関数」の書き方。
/// 戻り値の型は見た目には String だが、実際は impl Future<Output = String>。
async fn fetch(name: &str, millis: u64) -> String {
    sleep(Duration::from_millis(millis)).await;
    format!("{name}（{millis}ms）")
}

/// 失敗しうる非同期処理。Result との組み合わせも普通にできる。
async fn parse_after_delay(text: &str) -> Result<i32, std::num::ParseIntError> {
    sleep(Duration::from_millis(10)).await;
    text.parse()
}

// #[tokio::main] は「この main を非同期ランタイムの上で走らせる」印。
// Rust の標準ライブラリにはランタイムが入っていないので、
// tokio のような外部クレートを自分で選んで入れる必要がある。
// C# は .NET ランタイムが最初から面倒を見てくれるので、ここが大きな差。
#[tokio::main]
async fn main() {
    println!("── 1. Future は呼んだだけでは走らない ──");
    let started = Instant::now();
    let future = fetch("走らせていない仕事", 200); // まだ何も起きていない
    println!("  呼んだ直後の経過時間 = {:?}", started.elapsed());
    println!("  ← 200ms 待つ関数を呼んだのに、ほぼ 0 秒");
    let result = future.await; // ここで初めて走る
    println!("  await した後 = {:?}", started.elapsed());
    println!("  結果 = {result}");

    println!("\n── 2. 直列に await すると足し算になる ──");
    let started = Instant::now();
    let a = fetch("A", 100).await;
    let b = fetch("B", 100).await;
    println!("  {a} と {b}");
    println!("  かかった時間 = {:?}（100 + 100）", started.elapsed());

    println!("\n── 3. join! なら同時に走る ──");
    let started = Instant::now();
    // 2 つの Future を同時に進める。C# の Task.WhenAll に相当。
    let (a, b) = tokio::join!(fetch("A", 100), fetch("B", 100));
    println!("  {a} と {b}");
    println!("  かかった時間 = {:?}（並行に進んだ）", started.elapsed());

    println!("\n── 4. spawn すると即座に走り始める ──");
    // spawn に渡したものはランタイムが引き取るので、
    // ここだけは C# の Task と同じく「呼んだら走る」になる。
    let started = Instant::now();
    let handle = tokio::spawn(fetch("spawn した仕事", 120));
    sleep(Duration::from_millis(60)).await; // その間に別のことをする
    println!("  60ms 経過。spawn した仕事は裏で進んでいる");
    let result = handle.await.unwrap();
    println!("  {result} / 合計 {:?}", started.elapsed());

    println!("\n── 5. 先に終わったほうを採る ──");
    // select! は「どちらか片方が終わったら残りは捨てる」。
    tokio::select! {
        fast = fetch("速いほう", 30) => println!("  勝ち: {fast}"),
        slow = fetch("遅いほう", 300) => println!("  勝ち: {slow}"),
    }

    println!("\n── 6. タイムアウト ──");
    match tokio::time::timeout(Duration::from_millis(50), fetch("間に合わない", 500)).await {
        Ok(v) => println!("  間に合った: {v}"),
        Err(_) => println!("  50ms で打ち切った"),
    }

    println!("\n── 7. Result と組み合わせる ──");
    for text in ["42", "よんじゅうに"] {
        match parse_after_delay(text).await {
            Ok(n) => println!("  {text} → {n}"),
            Err(e) => println!("  {text} → 失敗（{e}）"),
        }
    }

    println!("\n── 8. まとめ ──");
    println!("  ・async fn を呼ぶ = Future を作るだけ。まだ走らない");
    println!("  ・await するか spawn するまで進まない");
    println!("  ・ランタイム（tokio など）は自分で入れる");
    println!("  ・「await を忘れた」は警告として出る。C# の投げっぱなしより気づきやすい");
}
