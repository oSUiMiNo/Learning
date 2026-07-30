//! ライフタイム。'a が何を言っているのかを、動く形で確かめます。

/// 引数が 2 つあると、返す参照がどちらから来たのか書かないと決まらない。
/// 'a は「この 3 つの参照は同じくらい生きる」という約束。
/// 新しい寿命を作るのではなく、既にある寿命に名前を付けているだけ。
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.chars().count() >= b.chars().count() {
        a
    } else {
        b
    }
}

/// 引数が 1 つなら書かなくてよい（省略規則）。
/// 返す参照の出どころが 1 つしかないので、迷う余地がない。
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap_or("")
}

/// 参照を持つ構造体には、必ずライフタイムが要る。
/// 「この構造体は、借りている元より長生きできない」という宣言。
struct Excerpt<'a> {
    source: &'a str,
    part: &'a str,
}

impl<'a> Excerpt<'a> {
    fn new(source: &'a str) -> Self {
        let part = source.split('。').next().unwrap_or(source);
        Self { source, part }
    }

    /// &self のライフタイムが返り値に伝わる（省略規則の 3 番目）
    fn part(&self) -> &str {
        self.part
    }

    fn ratio(&self) -> f64 {
        self.part.chars().count() as f64 / self.source.chars().count() as f64
    }
}

/// 'static は「プログラムが終わるまで生きる」。
/// 文字列リテラルは実行ファイルに埋め込まれているのでこれになる。
fn motto() -> &'static str {
    "速く、安全に"
}

fn main() {
    println!("── 1. 2 つの参照から片方を返す ──");
    let long = String::from("うさぎとかめ");
    let short = String::from("かめ");
    println!("  長いほう = {}", longer(&long, &short));

    println!("\n── 2. 省略できる場合 ──");
    let sentence = String::from("Rust は速い");
    println!("  最初の語 = {}", first_word(&sentence));

    println!("\n── 3. 参照を持つ構造体 ──");
    let text = String::from("所有権は難しくない。慣れの問題である。");
    let excerpt = Excerpt::new(&text);
    println!("  最初の文 = {}", excerpt.part());
    println!("  全体に対する割合 = {:.0}%", excerpt.ratio() * 100.0);

    println!("\n── 4. 'static ──");
    println!("  {}", motto());

    println!("\n── 5. 借用の寿命が足りないとどうなるか ──");
    // 下のコードはコンパイルできない（E0597）。
    // examples/errors/e0597-does-not-live-long-enough.rs で実際に確かめている。
    //
    //     let outer;
    //     {
    //         let inner = String::from("短い命");
    //         outer = &inner;
    //     }
    //     println!("{outer}");
    //
    // 「消えたものを指す参照」がコンパイル時に見つかる、というのが要点。
    println!("  内側で作った値を外に持ち出す参照は、コンパイル時に止まる");

    println!("\n── 6. 参照を持たせない選択 ──");
    // ライフタイムで悩んだら、借りるのをやめて所有させるのが素直な解決策。
    // 少しコピーが増えるが、まず動かすことのほうが大事。
    struct OwnedExcerpt {
        part: String,
    }
    let owned = OwnedExcerpt {
        part: excerpt.part().to_string(),
    };
    println!("  所有してしまえばライフタイムは要らない: {}", owned.part);
}
