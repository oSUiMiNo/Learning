//! 実践: ToDo を管理する CLI ツール。
//!
//! ここまでに出てきたものを全部使います。
//!   ・struct と enum（データの形）
//!   ・Result と ?（エラー処理）
//!   ・Option（あるかないか）
//!   ・イテレータ（絞り込みと集計）
//!   ・トレイト（derive による直列化）
//!   ・外部クレート（clap / serde / anyhow）
//!
//! 使い方:
//!   cargo run -- add "牛乳を買う" --priority high
//!   cargo run -- list
//!   cargo run -- done 1
//!   cargo run -- stats

use std::fs;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result, bail};
use clap::{Parser, Subcommand, ValueEnum};
use serde::{Deserialize, Serialize};

/// コマンド全体の定義。derive で書くと、ヘルプも自動で作られる。
#[derive(Parser)]
#[command(name = "todo", version, about = "小さな ToDo 管理ツール")]
struct Cli {
    /// 保存先のファイル。指定しなければ todo.json
    #[arg(long, default_value = "todo.json", global = true)]
    file: PathBuf,

    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// 用事を追加する
    Add {
        /// 用事の内容
        title: String,
        /// 優先度
        #[arg(short, long, value_enum, default_value_t = Priority::Medium)]
        priority: Priority,
    },
    /// 一覧を表示する
    List {
        /// 終わったものも含める
        #[arg(short, long)]
        all: bool,
    },
    /// 終わった印を付ける
    Done {
        /// 対象の番号
        id: u32,
    },
    /// 集計を表示する
    Stats,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, ValueEnum, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Priority {
    Low,
    Medium,
    High,
}

impl Priority {
    fn mark(self) -> &'static str {
        match self {
            Priority::Low => "・",
            Priority::Medium => "○",
            Priority::High => "★",
        }
    }
}

/// 1 件の用事。Serialize / Deserialize を derive すると JSON にできる。
#[derive(Debug, Serialize, Deserialize)]
struct Task {
    id: u32,
    title: String,
    priority: Priority,
    done: bool,
}

/// ファイル全体。
#[derive(Debug, Default, Serialize, Deserialize)]
struct Store {
    tasks: Vec<Task>,
}

impl Store {
    /// 読み込む。ファイルが無い場合は空として扱う（エラーにしない）。
    fn load(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let text = fs::read_to_string(path)
            .with_context(|| format!("{} を読めませんでした", path.display()))?;
        let store = serde_json::from_str(&text)
            .with_context(|| format!("{} の中身が JSON として読めません", path.display()))?;
        Ok(store)
    }

    fn save(&self, path: &Path) -> Result<()> {
        let text = serde_json::to_string_pretty(self)?;
        fs::write(path, text).with_context(|| format!("{} に書けませんでした", path.display()))?;
        Ok(())
    }

    fn next_id(&self) -> u32 {
        self.tasks.iter().map(|t| t.id).max().unwrap_or(0) + 1
    }

    fn find_mut(&mut self, id: u32) -> Option<&mut Task> {
        self.tasks.iter_mut().find(|t| t.id == id)
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let mut store = Store::load(&cli.file)?;

    match cli.command {
        Command::Add { title, priority } => {
            if title.trim().is_empty() {
                bail!("用事の内容が空です");
            }
            let task = Task {
                id: store.next_id(),
                title,
                priority,
                done: false,
            };
            println!("追加しました: [{}] {}", task.id, task.title);
            store.tasks.push(task);
            store.save(&cli.file)?;
        }

        Command::List { all } => {
            // 未完了を優先度の高い順に並べる
            let mut shown: Vec<&Task> = store.tasks.iter().filter(|t| all || !t.done).collect();
            shown.sort_by_key(|t| (t.done, std::cmp::Reverse(t.priority), t.id));

            if shown.is_empty() {
                println!("表示するものがありません");
            }
            for task in shown {
                let check = if task.done { "済" } else { "未" };
                println!(
                    "{check} {} [{}] {}",
                    task.priority.mark(),
                    task.id,
                    task.title
                );
            }
        }

        Command::Done { id } => {
            // Option を使って「見つからない」を素直に扱う
            let Some(task) = store.find_mut(id) else {
                bail!("番号 {id} の用事は見つかりません");
            };
            if task.done {
                println!("[{id}] はすでに終わっています");
            } else {
                task.done = true;
                println!("終わりにしました: [{}] {}", task.id, task.title);
                store.save(&cli.file)?;
            }
        }

        Command::Stats => {
            let total = store.tasks.len();
            let done = store.tasks.iter().filter(|t| t.done).count();
            let high = store
                .tasks
                .iter()
                .filter(|t| !t.done && t.priority == Priority::High)
                .count();

            println!("全部で {total} 件、終わったのが {done} 件");
            if total > 0 {
                println!("進捗 {:.0}%", done as f64 / total as f64 * 100.0);
            }
            if high > 0 {
                println!("急ぎのものが {high} 件残っています");
            }
        }
    }

    Ok(())
}
