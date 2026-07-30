//! モジュールとクレート。ファイル分割と公開範囲を確かめます。
//!
//! この章のサンプルは 3 ファイルに分かれています。
//!   src/main.rs        入口。ここから mod で他を読み込む
//!   src/geometry.rs    モジュール本体
//!   src/geometry/area.rs   さらに入れ子のモジュール

// mod は「このファイルの中身をここに取り込む」宣言。
// C# の using とは別物で、using に当たるのは下の use。
mod geometry;

// use は名前を短く使うための別名付け。
// これが C# の using ディレクティブに相当する。
use geometry::area::{circle, from_corners, rectangle};
use geometry::{Point, doubled_distance};

fn main() {
    println!("── 1. モジュールの中の型を使う ──");
    let a = Point::new(0.0, 0.0);
    let b = Point::new(3.0, 4.0);
    println!("  2 点の距離 = {}", a.distance_to(&b));

    println!("\n── 2. 入れ子のモジュール ──");
    println!("  半径 2 の円   = {:.2}", circle(2.0));
    println!("  3 × 4 の長方形 = {:.2}", rectangle(3.0, 4.0));

    println!("\n── 3. 非公開のものは見えない ──");
    // geometry::secret_scale() は pub が付いていないので、ここからは呼べない。
    // pub を付け忘れたときのエラーは E0603（private）。
    // ただし、同じモジュール内から呼んでいる doubled_distance 経由なら使える。
    println!("  pub の付いていない関数は、モジュールの外からは呼べません");
    println!("  でも中で使っている公開関数を通せば結果は得られる:");
    println!("  doubled_distance = {}", doubled_distance(&a, &b));

    println!("\n── 3.5 pub(crate) は「このクレート限定」 ──");
    // Point::coords は pub(crate) なので、area モジュールからは使えるが、
    // このクレートを外から使う人には見えない。
    println!("  対角の長方形の面積 = {:.1}", from_corners(&a, &b));

    println!("\n── 4. フルパスでも書ける ──");
    println!(
        "  crate::geometry::area::circle(1.0) = {:.4}",
        crate::geometry::area::circle(1.0)
    );

    println!("\n── 5. 既定は非公開 ──");
    println!("  C# は internal が既定、Rust はモジュール内だけが既定");
    println!("  外に出したいものに 1 つずつ pub を付けていく");
}
