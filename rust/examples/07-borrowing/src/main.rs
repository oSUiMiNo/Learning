//! 借用（参照）のふるまいを確かめるサンプル。
//!
//! 規則はふたつだけ。
//!   ・読む参照 &T は、同時に何本でも作れる
//!   ・書く参照 &mut T は、同時に 1 本だけ。しかも &T と同席できない
//! この 2 行が、データ競合と「イテレート中の変更」を根こそぎ防いでいる。

/// 読むだけなので &Vec ではなく &[i32] で受け取る。
/// スライスで受け取ると、Vec でも配列でも渡せて使い回しが利く。
fn total(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}

/// 中身を書き換えるので &mut が必要。
/// ただし要素を差し替えるだけなら &mut [i32] で足りる。
/// 個数を変えないのに &mut Vec<i32> を要求すると、
/// 配列を渡せなくなるだけ損なので、clippy にも注意される。
fn double_all(numbers: &mut [i32]) {
    for n in numbers.iter_mut() {
        *n *= 2;
    }
}

/// 個数そのものを変えるなら、スライスでは足りず &mut Vec<i32> が要る。
/// push は Vec のメソッドで、長さを変えられるのは Vec だけだから。
fn append_total(numbers: &mut Vec<i32>) {
    let sum = total(numbers);
    numbers.push(sum);
}

fn main() {
    println!("── 1. 読む借用は何本でも ──");
    let numbers = vec![1, 2, 3, 4, 5];
    let a = &numbers;
    let b = &numbers;
    println!("  a の合計 = {}", total(a));
    println!("  b の要素数 = {}", b.len());
    println!("  元の numbers も使える = {numbers:?}");

    println!("\n── 2. 書く借用は 1 本だけ ──");
    let mut scores = vec![10, 20, 30];
    double_all(&mut scores);
    println!("  倍にした = {scores:?}");
    append_total(&mut scores);
    println!("  合計を末尾に足した = {scores:?}");
    println!("  ← 個数を変える操作は &mut [i32] ではできず、&mut Vec<i32> が必要");
    // &mut を 2 本作ろうとすると E0499。
    // examples/errors/e0499-two-mutable-borrows.rs で確かめている。

    println!("\n── 3. 借用は「最後に使った所」で終わる ──");
    let mut queue = vec![1, 2, 3];
    let first = &queue[0];
    println!("  先頭は {first}"); // first の用はここで済む
    queue.push(4); // だからここで &mut を作れる
    println!("  追加後 = {queue:?}");

    println!("\n── 4. スライスは「窓」であって複製ではない ──");
    let text = String::from("Rust はたのしい");
    let head = &text[0..4]; // バイト単位で 0〜3。"Rust" の 4 バイト
    println!("  元の文字列 = {text}");
    println!("  切り出した窓 = {head}");
    println!("  窓は元データを指しているだけなので、コピーは起きていない");

    println!("\n── 5. &mut 越しに書き換える ──");
    let mut counter = 0;
    {
        let handle = &mut counter;
        *handle += 1; // * で中身に触る
        *handle += 1;
    } // ここで handle の借用が終わる
    println!("  counter = {counter}");
}
