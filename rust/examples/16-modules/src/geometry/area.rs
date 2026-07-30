//! 面積の計算。geometry の入れ子モジュール。
//!
//! 親モジュールのものを使うときは super:: で辿れる。
//! クレートの根からたどるなら crate:: を使う。

use super::Point;

/// 円の面積
pub fn circle(radius: f64) -> f64 {
    std::f64::consts::PI * radius * radius
}

/// 長方形の面積
pub fn rectangle(width: f64, height: f64) -> f64 {
    width * height
}

/// 2 点を対角とする長方形の面積。
/// 親モジュールの pub(crate) なメソッドを使っている。
pub fn from_corners(a: &Point, b: &Point) -> f64 {
    let (ax, ay) = a.coords();
    let (bx, by) = b.coords();
    (ax - bx).abs() * (ay - by).abs()
}
