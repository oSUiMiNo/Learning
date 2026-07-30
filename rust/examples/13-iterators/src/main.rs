//! イテレータとクロージャ。LINQ を知っていれば、ほぼそのまま読めます。

#[derive(Debug)]
struct Employee {
    name: &'static str,
    department: &'static str,
    salary: u32,
}

fn staff() -> Vec<Employee> {
    vec![
        Employee {
            name: "すずき",
            department: "開発",
            salary: 620,
        },
        Employee {
            name: "たなか",
            department: "営業",
            salary: 480,
        },
        Employee {
            name: "さとう",
            department: "開発",
            salary: 710,
        },
        Employee {
            name: "いとう",
            department: "営業",
            salary: 530,
        },
        Employee {
            name: "やまだ",
            department: "総務",
            salary: 450,
        },
    ]
}

fn main() {
    let people = staff();

    println!("── 1. Where / Select はそのまま filter / map ──");
    // LINQ: people.Where(p => p.Department == "開発").Select(p => p.Name)
    let devs: Vec<&str> = people
        .iter()
        .filter(|p| p.department == "開発")
        .map(|p| p.name)
        .collect();
    println!("  開発の人 = {devs:?}");

    println!("\n── 2. 遅延評価も同じ ──");
    // ここではまだ 1 件も処理されていない。collect や for で初めて走る。
    let pipeline = people.iter().map(|p| {
        println!("    （map が動いた: {}）", p.name);
        p.salary
    });
    println!("  ここまで何も出ていないことに注目");
    let total: u32 = pipeline.sum(); // ここで初めて動く
    println!("  合計 = {total}");

    println!("\n── 3. 集約 ──");
    println!("  人数     = {}", people.len());
    println!("  最高給与 = {:?}", people.iter().map(|p| p.salary).max());
    println!(
        "  平均給与 = {:.1}",
        people.iter().map(|p| p.salary).sum::<u32>() as f64 / people.len() as f64
    );
    // Any / All
    println!(
        "  700 超えがいるか = {}",
        people.iter().any(|p| p.salary > 700)
    );
    println!(
        "  全員 400 超えか  = {}",
        people.iter().all(|p| p.salary > 400)
    );

    println!("\n── 4. First / FirstOrDefault は find ──");
    // LINQ の FirstOrDefault は null を返すが、Rust は Option を返す
    let found = people.iter().find(|p| p.department == "総務");
    println!("  総務の人 = {:?}", found.map(|p| p.name));

    println!("\n── 5. OrderBy は sort_by_key ──");
    let mut sorted: Vec<&Employee> = people.iter().collect();
    sorted.sort_by_key(|p| std::cmp::Reverse(p.salary));
    let ranking: Vec<String> = sorted
        .iter()
        .map(|p| format!("{}({})", p.name, p.salary))
        .collect();
    println!("  給与順 = {}", ranking.join(" > "));

    println!("\n── 6. GroupBy は fold で書く ──");
    // 標準ライブラリに group_by は無いので、fold で畳み込む。
    // itertools クレートを入れれば chunk_by なども使える。
    use std::collections::BTreeMap;
    let by_department: BTreeMap<&str, Vec<&str>> =
        people.iter().fold(BTreeMap::new(), |mut acc, p| {
            acc.entry(p.department).or_default().push(p.name);
            acc
        });
    for (department, names) in &by_department {
        println!("  {department}: {names:?}");
    }

    println!("\n── 7. Take / Skip / Zip ──");
    let numbers: Vec<i32> = (1..=10).collect();
    println!(
        "  take(3)      = {:?}",
        numbers.iter().take(3).collect::<Vec<_>>()
    );
    println!(
        "  skip(7)      = {:?}",
        numbers.iter().skip(7).collect::<Vec<_>>()
    );
    println!(
        "  step_by(3)   = {:?}",
        numbers.iter().step_by(3).collect::<Vec<_>>()
    );
    let letters = ["a", "b", "c"];
    let zipped: Vec<String> = numbers
        .iter()
        .zip(letters.iter())
        .map(|(n, s)| format!("{n}{s}"))
        .collect();
    println!("  zip          = {zipped:?}");

    println!("\n── 8. クロージャは環境を捕まえる ──");
    let threshold = 500;
    // threshold を借用して覚えている
    let is_high = |p: &Employee| p.salary >= threshold;
    let count = people.iter().filter(|p| is_high(p)).count();
    println!("  {threshold} 以上は {count} 人");

    // move を付けると、捕まえた値の所有権をもらう
    let label = String::from("給与");
    let describe = move |n: u32| format!("{label}: {n}");
    println!("  {}", describe(620));

    println!("\n── 9. 失敗しうる変換を collect でまとめる ──");
    // Vec<Result<T, E>> を Result<Vec<T>, E> にたたむことができる。
    // 1 つでも失敗すれば全体が Err になる。
    let all_ok: Result<Vec<i32>, _> = ["1", "2", "3"].iter().map(|s| s.parse::<i32>()).collect();
    let has_bad: Result<Vec<i32>, _> = ["1", "に", "3"].iter().map(|s| s.parse::<i32>()).collect();
    println!("  全部数値   = {all_ok:?}");
    println!("  ひとつ駄目 = {}", has_bad.is_err());
}
