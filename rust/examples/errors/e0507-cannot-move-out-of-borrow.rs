//! expect: E0507
//! title: 借りているものの中身を持ち出せない
//! chapter: 07-borrowing
//!
//! 「借りているだけ」の相手から所有権を奪おうとするとこうなる。
//! 直し方は clone するか、参照のまま使うか、to_owned するか。

struct Config {
    name: String,
}

fn take_name(config: &Config) -> String {
    config.name // 借用越しに String を持ち出そうとしている
}

fn main() {
    let config = Config {
        name: String::from("既定"),
    };
    println!("{}", take_name(&config));
}
