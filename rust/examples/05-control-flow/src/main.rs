//! 制御フロー。Rust では if も match もループも「式」なので、値を返せます。

/// 早期 return も普通に書ける。式指向だからといって縛られはしない。
fn classify(score: i32) -> &'static str {
    if score < 0 {
        return "ありえない値";
    }

    // if は式なので、そのまま戻り値になる
    if score >= 80 {
        "優"
    } else if score >= 60 {
        "良"
    } else {
        "可"
    }
}

fn main() {
    println!("── 1. if は値を返す ──");
    let hour = 14;
    // C# の三項演算子 (cond ? a : b) の代わりがこれ
    let greeting = if hour < 12 {
        "おはよう"
    } else {
        "こんにちは"
    };
    println!("  {greeting}");

    for score in [95, 70, 30, -1] {
        println!("  {score} 点 → {}", classify(score));
    }

    println!("\n── 2. loop は値を返せる ──");
    let mut n = 1;
    // break に値を付けると、それが loop 式の値になる
    let first_over_100 = loop {
        n *= 3;
        if n > 100 {
            break n;
        }
    };
    println!("  3 を掛け続けて最初に 100 を超えたのは {first_over_100}");

    println!("\n── 3. while ──");
    let mut countdown = 3;
    while countdown > 0 {
        println!("  {countdown}...");
        countdown -= 1;
    }
    println!("  発射");

    println!("\n── 4. for は必ず「何かをなめる」形 ──");
    // C 風の for (i = 0; i < n; i++) は無い。範囲や反復子をなめる。
    for i in 1..=3 {
        println!("  1..=3 の {i}");
    }
    for (index, name) in ["赤", "青", "黄"].iter().enumerate() {
        println!("  {index} 番目は {name}");
    }

    println!("\n── 5. ラベル付き break ──");
    // 入れ子のループから一気に抜ける。C# の goto 代わり。
    'outer: for a in 1..=3 {
        for b in 1..=3 {
            if a * b >= 6 {
                println!("  {a} × {b} = {} で打ち切り", a * b);
                break 'outer;
            }
        }
    }

    println!("\n── 6. match は網羅性を検査される ──");
    for n in [0, 1, 5, 42] {
        let label = match n {
            0 => "ゼロ".to_string(),
            1 => "ひとつ".to_string(),
            // 範囲でも受けられる
            2..=9 => format!("{n} は一桁"),
            // _ は「それ以外」。これが無いと漏れとして怒られる
            _ => format!("{n} は二桁以上"),
        };
        println!("  {label}");
    }

    println!("\n── 7. ブロックも式 ──");
    let computed = {
        let base = 10;
        base * base // これがブロックの値
    };
    println!("  ブロックの値 = {computed}");
}
