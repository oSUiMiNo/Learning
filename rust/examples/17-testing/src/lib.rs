//! テストとドキュメント。テスト機構が言語に組み込みであることを確かめます。
//!
//! この章のサンプルはライブラリ（--lib）にしてあります。
//! `cargo test` を実行すると、次の 3 種類がまとめて走ります。
//!   1. #[test] を付けた単体テスト
//!   2. ドキュメントコメントの中のコード例（doc テスト）
//!   3. tests/ ディレクトリの結合テスト

/// 消費税を加えた金額を返す。円未満は切り捨て。
///
/// # 例
///
/// ```
/// use ch17_testing::with_tax;
///
/// assert_eq!(with_tax(100, 0.10), 110);
/// assert_eq!(with_tax(105, 0.10), 115); // 115.5 → 切り捨て
/// ```
///
/// この ``` で囲んだ部分は、ただの飾りではありません。
/// `cargo test` が実際にコンパイルして実行します。
/// つまり「ドキュメントの例が古くなって動かない」ことが起きません。
pub fn with_tax(price: u32, rate: f64) -> u32 {
    (price as f64 * (1.0 + rate)).floor() as u32
}

/// 文字列を逆さにする。文字単位なので、日本語でも壊れない。
///
/// # 例
///
/// ```
/// use ch17_testing::reverse;
///
/// assert_eq!(reverse("abc"), "cba");
/// assert_eq!(reverse("こんにちは"), "はちにんこ");
/// ```
pub fn reverse(text: &str) -> String {
    text.chars().rev().collect()
}

/// 割り算。0 で割ろうとしたら Err を返す。
///
/// # 例
///
/// ```
/// use ch17_testing::divide;
///
/// assert_eq!(divide(10, 2), Ok(5));
/// assert!(divide(1, 0).is_err());
/// ```
pub fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        return Err("0 で割ることはできません".to_string());
    }
    Ok(a / b)
}

/// パニックすることを示す例も書ける。
///
/// ```should_panic
/// ch17_testing::must_be_positive(-1);
/// ```
pub fn must_be_positive(n: i32) {
    assert!(n > 0, "正の数でなければなりません（受け取った値: {n}）");
}

// テストは同じファイルの中に、専用のモジュールとして置くのが慣習。
// #[cfg(test)] が付いているので、通常のビルドには含まれない。
// 「テストコードが製品に混ざる」心配が要らない。
#[cfg(test)]
mod tests {
    // 親モジュール（つまりこのライブラリ本体）のものを全部持ってくる
    use super::*;

    #[test]
    fn 税込み金額を計算できる() {
        // テスト関数の名前に日本語を使える。読みやすさのために使ってよい。
        assert_eq!(with_tax(100, 0.10), 110);
        assert_eq!(with_tax(1000, 0.08), 1080);
    }

    #[test]
    fn 端数は切り捨てる() {
        assert_eq!(with_tax(105, 0.10), 115);
    }

    #[test]
    fn 日本語も逆さにできる() {
        assert_eq!(reverse("こんにちは"), "はちにんこ");
    }

    #[test]
    fn ゼロ除算はエラーになる() {
        let result = divide(1, 0);
        assert!(result.is_err());
        // エラーの中身まで確かめる
        assert_eq!(result.unwrap_err(), "0 で割ることはできません");
    }

    #[test]
    #[should_panic(expected = "正の数")]
    fn 負の数を渡すと落ちる() {
        must_be_positive(-5);
    }

    /// Result を返すテストも書ける。? が使えるので前準備が短くなる。
    #[test]
    fn 結果型を返すテスト() -> Result<(), String> {
        let value = divide(10, 2)?;
        assert_eq!(value, 5);
        Ok(())
    }

    #[test]
    #[ignore = "時間がかかるので、明示的に指定したときだけ走らせる"]
    fn 重いテスト() {
        // cargo test -- --ignored で走る
        assert_eq!(with_tax(1, 0.0), 1);
    }
}
