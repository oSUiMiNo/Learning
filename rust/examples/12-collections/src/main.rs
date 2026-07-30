//! コレクション。C# の List / Dictionary / HashSet と対応させながら見ます。

use std::collections::{HashMap, HashSet, VecDeque};

fn main() {
    println!("── 1. Vec は List<T> ──");
    // vec! マクロで最初から中身を入れて作れる
    let mut fruits = vec!["りんご", "みかん"];
    // 後から足すのが push。C# の List.Add に相当する。
    fruits.push("ぶどう");
    println!("  {fruits:?}（{} 個）", fruits.len());

    // 空から作ることもできる。型は入れたものから決まる。
    let mut empty: Vec<&str> = Vec::new();
    println!("  空の Vec = {empty:?}（is_empty = {}）", empty.is_empty());
    empty.push("これで 1 個");
    println!("  1 つ足した = {empty:?}");

    let numbers = vec![5, 3, 8, 1];
    println!("  numbers = {numbers:?}");

    // 添字アクセスは範囲外で panic する。get なら Option で受けられる。
    println!("  numbers[0] = {}", numbers[0]);
    println!("  get(99)    = {:?}（範囲外でも落ちない）", numbers.get(99));

    println!("\n── 2. 並べ替えと検索 ──");
    let mut sorted = numbers.clone();
    sorted.sort(); // 破壊的に並べ替える
    println!("  昇順       = {sorted:?}");
    sorted.sort_by(|a, b| b.cmp(a)); // 比較関数を渡す
    println!("  降順       = {sorted:?}");
    println!("  contains   = {}", sorted.contains(&8));

    println!("\n── 3. HashMap は Dictionary<K, V> ──");
    let mut ages = HashMap::new();
    ages.insert("すずき", 28);
    ages.insert("たなか", 34);

    // 取り出しは Option。キーが無いときに例外ではなく None が返る。
    println!("  すずき = {:?}", ages.get("すずき"));
    println!("  さとう = {:?}", ages.get("さとう"));

    // 「無ければ入れる」を 1 行で書ける。C# の GetOrAdd に相当。
    let entry = ages.entry("さとう").or_insert(0);
    *entry += 41;
    println!("  さとう = {:?}（entry で追加した）", ages.get("さとう"));

    // 出てくる順番は決まっていない。並べたいなら自分で並べる。
    let mut names: Vec<_> = ages.keys().collect();
    names.sort();
    println!("  キーを並べた = {names:?}");

    println!("\n── 4. HashSet は HashSet<T> ──");
    let a: HashSet<i32> = [1, 2, 3, 4].into_iter().collect();
    let b: HashSet<i32> = [3, 4, 5].into_iter().collect();
    let mut common: Vec<_> = a.intersection(&b).copied().collect();
    common.sort();
    println!("  共通部分 = {common:?}");

    println!("\n── 5. VecDeque は両端から出し入れできる ──");
    let mut queue = VecDeque::new();
    queue.push_back("あとから");
    queue.push_front("さきに");
    println!("  {queue:?}");
    println!("  先頭を取り出す = {:?}", queue.pop_front());

    println!("\n── 6. 借用の規則がここで効いてくる ──");
    let mut stack = vec![1, 2, 3];
    // 読む借用が生きている間は push できない（E0502）。
    // 借用を先に終わらせれば通る。
    let last = *stack.last().unwrap(); // * で値を取り出して借用を終わらせる
    stack.push(last * 10);
    println!("  {stack:?}");

    println!("\n── 7. 所有権を渡す繰り返しと、借りる繰り返し ──");
    let words = vec![String::from("あ"), String::from("い")];
    for w in &words {
        // 借りるだけなので後でも使える
        print!("  借用: {w}");
    }
    println!("\n  元の Vec も健在: {words:?}");

    for w in words {
        // 所有権をもらうので、この後 words は使えない
        print!("  消費: {w}");
    }
    println!();
}
