//! 並行処理。所有権の規則がそのままスレッド安全性になることを確かめます。

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex, mpsc};
use std::thread;
use std::time::Duration;

fn main() {
    println!("── 1. スレッドを起こして待つ ──");
    let mut handles = Vec::new();
    for id in 1..=3 {
        // move で、id の所有権をクロージャに渡す。
        // これが無いと「借用がスレッドより短いかもしれない」と怒られる。
        let handle = thread::spawn(move || {
            thread::sleep(Duration::from_millis(10 * id));
            format!("スレッド {id} 完了")
        });
        handles.push(handle);
    }
    for handle in handles {
        // join で終わるのを待ち、戻り値を受け取る
        println!("  {}", handle.join().unwrap());
    }

    println!("\n── 2. チャネルで値を渡す ──");
    // 送信側と受信側に分かれる。送るときに所有権も一緒に渡る。
    let (tx, rx) = mpsc::channel();
    for id in 1..=3 {
        let tx = tx.clone(); // 送信側は複製できる（mpsc = 多対一）
        thread::spawn(move || {
            tx.send(format!("仕事 {id} の結果")).unwrap();
        });
    }
    drop(tx); // 元の送信側を落とすと、受信側のループが終われる

    // rx をなめると、送られてくるものを順に受け取れる
    let mut received: Vec<String> = rx.iter().collect();
    received.sort();
    println!("  受け取った = {received:?}");

    println!("\n── 3. Mutex で共有して書き換える ──");
    // Arc は「スレッドをまたげる Rc」。Mutex は排他ロック。
    // この 2 つを重ねるのが定番の形。
    let counter = Arc::new(Mutex::new(0));
    let mut handles = Vec::new();
    for _ in 0..8 {
        let counter = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            for _ in 0..1000 {
                // lock() は Result を返す。ロックを持っていたスレッドが
                // panic した場合に Err になるため。
                let mut value = counter.lock().unwrap();
                *value += 1;
                // ここでスコープを抜けると自動でロックが外れる。
                // C# の lock 文と違い、外し忘れが起きない。
            }
        }));
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("  8 スレッド × 1000 回 = {}", counter.lock().unwrap());

    println!("\n── 4. 数を数えるだけなら Atomic ──");
    let hits = Arc::new(AtomicUsize::new(0));
    let mut handles = Vec::new();
    for _ in 0..4 {
        let hits = Arc::clone(&hits);
        handles.push(thread::spawn(move || {
            for _ in 0..1000 {
                hits.fetch_add(1, Ordering::Relaxed);
            }
        }));
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("  4 スレッド × 1000 回 = {}", hits.load(Ordering::Relaxed));

    println!("\n── 5. スコープ付きスレッドなら借用できる ──");
    // scope の中のスレッドは、抜ける前に必ず終わることが保証される。
    // だから外側の値を Arc に包まずに借用できる。
    let data = [1, 2, 3, 4, 5, 6];
    let (left, right) = data.split_at(3);
    let total = thread::scope(|s| {
        let a = s.spawn(|| left.iter().sum::<i32>());
        let b = s.spawn(|| right.iter().sum::<i32>());
        a.join().unwrap() + b.join().unwrap()
    });
    println!("  分けて合計 = {total}（元の Vec を借用したまま渡せた）");

    println!("\n── 6. 何が守られているのか ──");
    println!("  Send  … 別のスレッドへ移してよい型");
    println!("  Sync  … 複数のスレッドから同時に参照してよい型");
    println!("  Rc は Send ではないので、スレッドに渡そうとするとコンパイルエラー");
    println!("  → データ競合が実行時のバグではなく、型の不一致として現れる");
}
