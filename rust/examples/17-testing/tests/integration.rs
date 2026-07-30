//! 結合テスト。tests/ に置いたファイルは、それぞれ別のクレートとして
//! コンパイルされ、ライブラリを「外から」使う。
//!
//! だから pub が付いていないものには触れない。
//! 「公開している API だけで、ちゃんと目的を果たせるか」を確かめる場所。

use ch17_testing::{divide, reverse, with_tax};

#[test]
fn 公開されている関数だけで一連の処理ができる() {
    let price = with_tax(2500, 0.10);
    assert_eq!(price, 2750);

    let label = reverse("0572");
    assert_eq!(label, "2750");

    let half = divide(price as i32, 2).expect("2 で割れるはず");
    assert_eq!(half, 1375);
}

#[test]
fn 税率がゼロなら金額は変わらない() {
    for price in [0, 1, 100, 99999] {
        assert_eq!(with_tax(price, 0.0), price, "price = {price} で失敗");
    }
}
