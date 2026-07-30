//! スマートポインタ。「所有者はひとりだけ」では書けない形への対処です。

use std::cell::RefCell;
use std::rc::{Rc, Weak};

/// Box は「中身をヒープに置く」だけの箱。
/// 再帰的なデータ構造は、これが無いとサイズが決まらず定義できない。
#[derive(Debug)]
enum Tree {
    Leaf(i32),
    Node(Box<Tree>, Box<Tree>),
}

fn sum(tree: &Tree) -> i32 {
    match tree {
        Tree::Leaf(v) => *v,
        Tree::Node(left, right) => sum(left) + sum(right),
    }
}

/// Rc は参照カウント付きの共有。読むだけなら複数の持ち主を作れる。
/// C# の参照とだいたい同じ感覚だが、カウントが見える点が違う。
#[derive(Debug)]
struct Document {
    title: String,
}

/// RefCell は「借用の検査を実行時に回す」箱。
/// 外から見ると不変なのに中身を書き換えられる（内部可変性）。
#[derive(Debug)]
struct Counter {
    hits: RefCell<u32>,
}

impl Counter {
    /// &self なのに書き換えられる。ここが RefCell の使いどころ。
    fn hit(&self) {
        *self.hits.borrow_mut() += 1;
    }
}

/// 親子で相互に参照したいとき、両方を Rc にすると循環して解放されない。
/// 片方を Weak にすると解決する。
struct Parent {
    name: String,
    children: RefCell<Vec<Rc<Child>>>,
}

struct Child {
    name: String,
    parent: RefCell<Weak<Parent>>,
}

fn main() {
    println!("── 1. Box でヒープに置く ──");
    let tree = Tree::Node(
        Box::new(Tree::Leaf(1)),
        Box::new(Tree::Node(Box::new(Tree::Leaf(2)), Box::new(Tree::Leaf(3)))),
    );
    println!("  合計 = {}", sum(&tree));
    println!("  Box が無いと、この enum は「サイズが無限」になって定義できない");

    println!("\n── 2. Rc で共有する ──");
    let doc = Rc::new(Document {
        title: String::from("仕様書"),
    });
    println!("  作った直後のカウント = {}", Rc::strong_count(&doc));
    {
        let viewer_a = Rc::clone(&doc); // 中身は複製しない。カウントだけ増える
        let viewer_b = Rc::clone(&doc);
        println!("  2 人が見ている       = {}", Rc::strong_count(&doc));
        println!(
            "  どちらも同じ中身     = {} / {}",
            viewer_a.title, viewer_b.title
        );
    } // ここで 2 人ぶん減る
    println!("  抜けた後のカウント   = {}", Rc::strong_count(&doc));

    println!("\n── 3. RefCell で内部可変性 ──");
    let counter = Counter {
        hits: RefCell::new(0),
    };
    counter.hit();
    counter.hit();
    counter.hit();
    // counter は mut ではないのに、中身が増えている
    println!("  hits = {}", counter.hits.borrow());
    println!("  変数に mut を付けていないのに書き換えられた");

    println!("\n── 4. RefCell の代償 ──");
    // コンパイル時ではなく実行時に検査するので、破ると panic する。
    let cell = RefCell::new(1);
    let first = cell.borrow();
    match cell.try_borrow_mut() {
        Ok(_) => println!("  借用できた（ここには来ない）"),
        Err(_) => println!("  読み中に書き込み借用しようとして弾かれた（実行時検査）"),
    }
    drop(first);
    println!(
        "  借用を手放してからなら書ける: {:?}",
        cell.try_borrow_mut().is_ok()
    );

    println!("\n── 5. Rc + RefCell の組み合わせ ──");
    // 「共有したうえで書き換えたい」ときの定番。
    let shared = Rc::new(RefCell::new(Vec::new()));
    let writer = Rc::clone(&shared);
    writer.borrow_mut().push("追記した");
    println!("  共有した Vec = {:?}", shared.borrow());

    println!("\n── 6. Weak で循環参照を避ける ──");
    let parent = Rc::new(Parent {
        name: String::from("親"),
        children: RefCell::new(Vec::new()),
    });
    let child = Rc::new(Child {
        name: String::from("子"),
        parent: RefCell::new(Rc::downgrade(&parent)), // 弱い参照
    });
    parent.children.borrow_mut().push(Rc::clone(&child));

    println!("  親のカウント（強い）= {}", Rc::strong_count(&parent));
    println!("  親のカウント（弱い）= {}", Rc::weak_count(&parent));
    // 弱い参照は upgrade して初めて使える。相手が消えていれば None。
    if let Some(found) = child.parent.borrow().upgrade() {
        println!("  {} から {} を辿れた", child.name, found.name);
    }
    println!("  両方を Rc にすると、カウントが 0 にならず解放されない");

    println!("\n── 7. 使い分け ──");
    println!("  所有者が 1 人でヒープに置きたい      → Box");
    println!("  読む持ち主が複数（単一スレッド）      → Rc");
    println!("  読む持ち主が複数（複数スレッド）      → Arc");
    println!("  不変に見せたまま中身を書き換えたい    → RefCell / Mutex");
}
