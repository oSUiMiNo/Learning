//! トレイトとジェネリクス。インターフェースとの違いに絞って確かめます。

use std::fmt::Display;

/// トレイトの定義。C# の interface に相当する。
trait Greet {
    /// 実装側が必ず書くメソッド
    fn name(&self) -> String;

    /// 既定の実装つきメソッド。
    /// C# 8 以降の default interface method と同じ発想だが、
    /// Rust には最初からある。
    fn hello(&self) -> String {
        format!("こんにちは、{} さん", self.name())
    }
}

struct Person {
    first: String,
}

struct Robot {
    id: u32,
}

impl Greet for Person {
    fn name(&self) -> String {
        self.first.clone()
    }
}

impl Greet for Robot {
    fn name(&self) -> String {
        format!("ユニット {}", self.id)
    }

    /// 既定の実装を上書きすることもできる
    fn hello(&self) -> String {
        format!("ピー・ガガ・{} 起動", self.name())
    }
}

/// 標準ライブラリの型に、自分のトレイトを後から実装できる。
/// C# では不可能（拡張メソッドで似せるのが精一杯）。
/// これがトレイトとインターフェースの決定的な違い。
impl Greet for i32 {
    fn name(&self) -> String {
        format!("整数の {self}")
    }
}

/// ジェネリクス + トレイト境界。
/// コンパイル時に型ごとの実体が作られる（単相化）。
/// 実行時のコストはゼロで、C# のジェネリクスより静的。
fn greet_all<T: Greet>(items: &[T]) {
    for item in items {
        println!("  {}", item.hello());
    }
}

/// impl Trait で書くと、境界を短く書ける。上と同じ意味。
fn shout(item: &impl Greet) -> String {
    item.hello().to_uppercase()
}

/// dyn Trait は実行時に決まる。vtable を経由するので
/// C# のインターフェース呼び出しに近い。
/// 型が違うものを 1 つの Vec に混ぜたいときはこれを使う。
fn greet_mixed(items: &[Box<dyn Greet>]) {
    for item in items {
        println!("  {}", item.hello());
    }
}

/// 複数の境界は + でつなぐ。where で後ろに書いてもよい。
fn describe<T>(value: T) -> String
where
    T: Display + PartialOrd<i32>,
{
    if value > 100 {
        format!("{value} は大きい")
    } else {
        format!("{value} は小さい")
    }
}

fn main() {
    println!("── 1. 同じトレイトを別の型が実装する ──");
    greet_all(&[
        Person {
            first: String::from("すずき"),
        },
        Person {
            first: String::from("たなか"),
        },
    ]);
    greet_all(&[Robot { id: 7 }]);

    println!("\n── 2. 標準の型にも後から実装できる ──");
    println!("  {}", 42.hello());

    println!("\n── 3. impl Trait ──");
    println!("  {}", shout(&Robot { id: 1 }));

    println!("\n── 4. dyn Trait で違う型を混ぜる ──");
    let mixed: Vec<Box<dyn Greet>> = vec![
        Box::new(Person {
            first: String::from("さとう"),
        }),
        Box::new(Robot { id: 99 }),
        Box::new(5_i32),
    ];
    greet_mixed(&mixed);

    println!("\n── 5. 複数のトレイト境界 ──");
    println!("  {}", describe(5));
    println!("  {}", describe(500));

    println!("\n── 6. 標準トレイトを derive で手に入れる ──");
    #[derive(Debug, Clone, PartialEq, PartialOrd)]
    struct Version(u32, u32);
    let a = Version(1, 2);
    let b = Version(1, 10);
    println!("  {a:?} < {b:?} = {}", a < b);

    println!("\n── 7. 孤児則 ──");
    println!("  「型」と「トレイト」の少なくとも一方が自分のものでないと実装できない");
    println!("  例: 標準の Display を標準の Vec に実装することはできない");
}
