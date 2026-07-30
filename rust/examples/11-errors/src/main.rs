//! エラー処理。例外を投げるかわりに、失敗を戻り値で返します。

use std::fmt;
use std::num::ParseIntError;

/// 自分で定義するエラー型。
/// C# の例外クラスに当たるが、継承ではなくトレイト実装で作る。
#[derive(Debug)]
enum ConfigError {
    Missing(String),
    NotANumber { key: String, source: ParseIntError },
    OutOfRange { key: String, value: i64 },
}

/// 人間に見せる文言。C# の Message プロパティに相当する。
impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConfigError::Missing(key) => write!(f, "設定 {key} がありません"),
            ConfigError::NotANumber { key, source } => {
                write!(f, "設定 {key} が数値として読めません（{source}）")
            }
            ConfigError::OutOfRange { key, value } => {
                write!(f, "設定 {key} の値 {value} は範囲外です")
            }
        }
    }
}

/// これを実装すると「標準のエラー」として扱える。
/// source() で原因の連鎖を辿れるようになる。
impl std::error::Error for ConfigError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            ConfigError::NotANumber { source, .. } => Some(source),
            _ => None,
        }
    }
}

/// 失敗しうる関数は Result を返す。呼び出し側は無視できない。
fn read_port(settings: &[(&str, &str)], key: &str) -> Result<u16, ConfigError> {
    // 探す。無ければ即座に Err を返す。
    let raw = settings
        .iter()
        .find(|(k, _)| *k == key)
        .map(|(_, v)| *v)
        .ok_or_else(|| ConfigError::Missing(key.to_string()))?;

    // 数値に変換する。失敗したら自分のエラー型に包み替える。
    let value: i64 = raw.parse().map_err(|source| ConfigError::NotANumber {
        key: key.to_string(),
        source,
    })?;

    // 範囲を検査する。
    if !(1..=65535).contains(&value) {
        return Err(ConfigError::OutOfRange {
            key: key.to_string(),
            value,
        });
    }

    Ok(value as u16)
}

/// ? を並べるだけで、失敗はそのまま上へ伝わる。
/// C# なら try-catch を書かずに例外が伝播していくのと同じ感覚。
fn load(settings: &[(&str, &str)]) -> Result<String, ConfigError> {
    let http = read_port(settings, "http_port")?;
    let https = read_port(settings, "https_port")?;
    Ok(format!("http:{http} / https:{https}"))
}

fn main() {
    let cases: [&[(&str, &str)]; 4] = [
        &[("http_port", "80"), ("https_port", "443")],
        &[("http_port", "80")],
        &[("http_port", "はちじゅう"), ("https_port", "443")],
        &[("http_port", "99999"), ("https_port", "443")],
    ];

    println!("── 1. 成功と失敗を並べて見る ──");
    for (i, settings) in cases.iter().enumerate() {
        match load(settings) {
            Ok(summary) => println!("  {}: OK   {summary}", i + 1),
            Err(e) => println!("  {}: NG   {e}", i + 1),
        }
    }

    println!("\n── 2. 原因の連鎖を辿る ──");
    if let Err(e) = load(cases[2]) {
        println!("  一番外のエラー: {e}");
        let mut current = std::error::Error::source(&e);
        while let Some(cause) = current {
            println!("  その原因      : {cause}");
            current = cause.source();
        }
    }

    println!("\n── 3. panic! は「もう続けられない」とき ──");
    // unwrap は「失敗したら panic」。書き捨てや、失敗しえない場面だけで使う。
    let sure: Result<i32, ParseIntError> = "42".parse();
    println!("  unwrap = {}", sure.unwrap());
    // expect はメッセージを添えられるので、unwrap より事故の調査が楽になる。
    let n: i32 = "7".parse().expect("ここは必ず数値のはず");
    println!("  expect = {n}");
    println!("  Result を無視すると警告が出る。C# の「例外を握り潰す」が起きにくい");
}
