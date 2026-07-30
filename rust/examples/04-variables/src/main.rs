//! 変数と型のふるまい。C# との差だけを速く確認するためのサンプル。

fn main() {
    println!("── 1. 既定は不変 ──");
    let fixed = 10;
    println!("  fixed = {fixed}（書き換えようとすると E0384）");

    let mut changeable = 10;
    println!("  changeable = {changeable}");
    changeable = 20;
    println!("  書き換えたら {changeable}");

    println!("\n── 2. シャドーイング ──");
    // 同じ名前で「別の変数」を作り直せる。型を変えてもよい。
    // C# ではスコープ内の再宣言はエラーなので、ここは Rust 独自。
    let value = "42"; // &str
    let value = value.parse::<i32>().unwrap(); // i32 に化ける
    let value = value * 2;
    println!("  文字列から数値にして倍にした = {value}");

    println!("\n── 3. 型は明示もできる ──");
    let a: i64 = 9_000_000_000; // 桁区切りに _ が使える
    let b: f64 = 0.5;
    let c: bool = true;
    let d: char = '猫'; // char は Unicode スカラ値 1 つ ＝ 4 バイト
    println!("  i64  = {a}");
    println!("  f64  = {b}");
    println!("  bool = {c}");
    println!("  char = {d}（{} バイト）", std::mem::size_of::<char>());

    println!("\n── 4. 暗黙の型変換はない ──");
    let small: i32 = 100;
    let big: i64 = small.into(); // 明示的に変換する
    let back: i32 = big as i32; // as は「切り詰めてよい」という宣言
    println!("  i32 → i64 は into() で {big}");
    println!("  i64 → i32 は as で {back}");

    println!("\n── 5. あふれたときの挙動 ──");
    let max = i32::MAX;
    // checked_add はあふれたら None を返す。黙って壊れない。
    match max.checked_add(1) {
        Some(n) => println!("  足せた: {n}"),
        None => println!("  i32::MAX に 1 を足すとあふれるので None が返った"),
    }
    println!("  wrapping_add なら回り込む: {}", max.wrapping_add(1));
    println!("  デバッグビルドでは max + 1 はその場で panic する");

    println!("\n── 6. タプルと配列 ──");
    let pair: (i32, &str) = (1, "一");
    println!("  タプル = {:?} / 1 番目 = {}", pair, pair.1);

    let fixed_array: [i32; 3] = [10, 20, 30]; // 長さが型に含まれる
    println!("  配列  = {fixed_array:?}（長さ {}）", fixed_array.len());

    let (x, y) = (3, 4); // 分解して受け取れる
    println!("  分解代入 = x:{x} y:{y}");

    println!("\n── 7. 定数 ──");
    // const はコンパイル時に決まる値。型の明記が必須。
    const LIMIT: u32 = 100;
    println!("  LIMIT = {LIMIT}");
}
