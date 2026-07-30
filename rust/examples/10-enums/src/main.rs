//! 列挙型と match。null が要らなくなる仕組みを確かめます。

/// Rust の enum は、それぞれの選択肢が値を持てる。
/// C# の enum（ただの整数の別名）とは別物で、
/// F# の判別共用体や TypeScript の直和型に近い。
#[derive(Debug)]
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle(f64, f64), // 底辺と高さ
}

impl Shape {
    fn area(&self) -> f64 {
        // match で分解しながら、必要な値だけ取り出す
        match self {
            Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
            Shape::Rectangle { width, height } => width * height,
            Shape::Triangle(base, height) => base * height / 2.0,
        }
    }
}

/// 見つからないことがある検索。C# なら null を返すか例外を投げるところ。
fn find_user(id: u32) -> Option<&'static str> {
    match id {
        1 => Some("すずき"),
        2 => Some("たなか"),
        _ => None,
    }
}

fn main() {
    println!("── 1. 値を持つ列挙型 ──");
    let shapes = [
        Shape::Circle { radius: 1.0 },
        Shape::Rectangle {
            width: 3.0,
            height: 4.0,
        },
        Shape::Triangle(6.0, 2.0),
    ];
    for shape in &shapes {
        println!("  {shape:?} の面積 = {:.2}", shape.area());
    }

    println!("\n── 2. Option が null の代わり ──");
    for id in [1, 99] {
        match find_user(id) {
            Some(name) => println!("  id {id} → {name}"),
            None => println!("  id {id} → 見つかりません"),
        }
    }

    println!("\n── 3. if let は「片方だけ気にする」書き方 ──");
    if let Some(name) = find_user(2) {
        println!("  見つかった: {name}");
    }

    println!("\n── 4. let else で早く抜ける ──");
    // 「無ければ関数を抜ける」を素直に書ける
    describe(1);
    describe(99);

    println!("\n── 5. Option の便利メソッド ──");
    let found = find_user(1);
    let missing = find_user(99);
    println!("  unwrap_or  = {}", missing.unwrap_or("名無し"));
    println!("  is_some    = {}", found.is_some());
    println!("  map        = {:?}", found.map(|n| n.len()));
    // and_then は「次も失敗しうる処理」をつなぐとき
    println!("  and_then   = {:?}", found.and_then(|n| n.chars().next()));

    println!("\n── 6. match の網羅性 ──");
    // Shape に新しい種類を足すと、この match が
    // 「対応し忘れている」とコンパイルエラーになる。
    // 追加のたびに直すべき場所を全部教えてくれる。
    println!("  Shape を増やすと、上の area() が必ずエラーになって気づける");
}

fn describe(id: u32) {
    let Some(name) = find_user(id) else {
        println!("  id {id} は該当なし。ここで打ち切ります");
        return;
    };
    println!("  id {id} は {name} さん");
}
