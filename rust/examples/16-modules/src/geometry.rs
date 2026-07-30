//! 図形に関するモジュール。
//!
//! //! で始まるコメントは「このモジュール自身の説明」。
//! /// で始まるコメントは「次に来る項目の説明」。
//! どちらも cargo doc でそのままドキュメントになる。

// 入れ子のモジュールを宣言する。中身は src/geometry/area.rs にある。
pub mod area;

/// 平面上の点。pub を付けたので、外のモジュールから使える。
#[derive(Debug, Clone, Copy)]
pub struct Point {
    // フィールドは pub を付けていないので、外からは直接触れない。
    // 型としては公開しつつ、中身は隠すという書き方ができる。
    x: f64,
    y: f64,
}

impl Point {
    pub fn new(x: f64, y: f64) -> Self {
        Self { x, y }
    }

    pub fn distance_to(&self, other: &Point) -> f64 {
        let dx = self.x - other.x;
        let dy = self.y - other.y;
        (dx * dx + dy * dy).sqrt()
    }

    /// pub(crate) は「このクレートの中だけ公開」。
    /// C# の internal に相当する。
    pub(crate) fn coords(&self) -> (f64, f64) {
        (self.x, self.y)
    }
}

/// pub が付いていないので、このモジュールの外からは呼べない。
fn secret_scale() -> f64 {
    2.0
}

/// 同じモジュール内からなら、非公開のものも使える。
pub fn doubled_distance(a: &Point, b: &Point) -> f64 {
    a.distance_to(b) * secret_scale()
}
