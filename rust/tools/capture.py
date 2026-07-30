"""コマンドを実際に走らせて、ANSI 付きの出力を捕獲する。

    python tools/capture.py            # 全部撮り直す
    python tools/capture.py e0382      # 名前に e0382 を含むものだけ

Qt6 の教材が「サンプルを起動してスクリーンショットを撮る」のと同じ役目。
Rust には見せる GUI がないので、かわりに本物のターミナル出力を撮る。

捕獲した結果は outputs/<name>.json に入る。build.py がそれを読んで、
ANSI を色付き HTML に直し、ターミナル枠に収めて本文へ差し込む。

擬似端末 (pty) 上で走らせているので、cargo も rustc も
「人間が見ている」と判断して色を付けてくれる。パイプに繋ぐと色が消えるため、
--color=always を付けずに済むこの方法のほうが実機に近い。
"""

from __future__ import annotations

import json
import os
import pty
import re
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
ERRORS = EXAMPLES / "errors"
OUTPUTS = ROOT / "outputs"

# 本文が示すプロンプト。読者の Windows に合わせた表示にする。
PROMPT = "PS C:\\rust>"


def run_in_pty(command: list[str], cwd: Path, env_extra: dict | None = None,
               timeout: float = 240.0) -> str:
    """擬似端末でコマンドを走らせ、混ざった標準出力・標準エラーをそのまま返す。

    入力待ちで止まるコマンドがあっても撮影全体が固まらないよう、
    必ず時間制限を設けて打ち切る。
    """
    env = dict(os.environ)
    env["TERM"] = "xterm-256color"
    # 端末幅は本文の見た目を安定させるために固定する。
    env["COLUMNS"] = "92"
    env.pop("NO_COLOR", None)
    env["CLICOLOR_FORCE"] = "1"
    # 擬似端末だと rustc --explain などがページャ（less）を起こし、
    # 入力待ちのまま止まってしまう。ページャは必ず素通しにする。
    env["PAGER"] = "cat"
    env["RUST_PAGER"] = "cat"
    env["LESS"] = "-F -X"
    env["GIT_PAGER"] = "cat"
    if env_extra:
        env.update(env_extra)

    primary, secondary = pty.openpty()
    try:
        import fcntl
        import struct
        import termios
        fcntl.ioctl(secondary, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 92, 0, 0))
    except Exception:
        pass

    proc = subprocess.Popen(command, cwd=str(cwd), stdout=secondary, stderr=secondary,
                            stdin=subprocess.DEVNULL, env=env, close_fds=True)
    os.close(secondary)

    chunks: list[bytes] = []
    selector = selectors.DefaultSelector()
    selector.register(primary, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    timed_out = False
    while True:
        for _ in selector.select(timeout=0.2):
            try:
                data = os.read(primary, 65536)
            except OSError:
                data = b""
            if data:
                chunks.append(data)
        if proc.poll() is None and time.monotonic() > deadline:
            proc.kill()
            timed_out = True
            chunks.append(
                f"\n[capture.py] {timeout:.0f} 秒を超えたため打ち切りました\n".encode())
        if proc.poll() is not None:
            # 残りを読み切る
            while True:
                try:
                    data = os.read(primary, 65536)
                except OSError:
                    break
                if not data:
                    break
                chunks.append(data)
            break
    selector.close()
    os.close(primary)
    proc.wait()
    if timed_out:
        print(f"    ! 時間切れで打ち切り: {' '.join(command)}")
    return b"".join(chunks).decode("utf-8", errors="replace")


# 捕獲は Linux 上で行っているが、読者は Windows で読む。
# そこで「パスの見た目」だけを Windows 形式に直す。直すのは次の 3 つに限る。
#
#   1. 一時作業ディレクトリの絶対パス  → C:\rust
#   2. target/debug/<名前>            → target\debug\<名前>.exe
#   3. 残った作業ディレクトリ内の / 区切り → \ 区切り
#
# エラーメッセージ本文・バージョン番号・コンパイル時間・警告の内容は
# 一切いじらない。実測であることの意味が無くなるからだ。
# この加工をしていること自体は、第0章と rust/README.md に明記してある。
WIN_ROOT = "C:\\rust"
# クレートの展開先。rustc の診断が「トレイトはここで定義されている」と
# 示すときに出てくる。読者の Windows では下のような場所になる。
WIN_CARGO_HOME = "C:\\Users\\you\\.cargo"
CARGO_HOME = Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo")).resolve()


def to_windows_paths(text: str, work: Path | None = None, project: str = "") -> str:
    if work is not None:
        # /tmp/xxxx/hello → C:\rust\hello、/tmp/xxxx → C:\rust
        text = text.replace(str(work), WIN_ROOT)
    # ~/.cargo/registry/... → C:\Users\you\.cargo\registry\...
    text = text.replace(str(CARGO_HOME), WIN_CARGO_HOME)
    if project:
        for profile in ("debug", "release"):
            text = text.replace(f"target/{profile}/{project}",
                                f"target\\{profile}\\{project}.exe")
    # 置き換えた Windows の根に続く / 区切りを \ に直す
    for root in (re.escape(WIN_ROOT), re.escape(WIN_CARGO_HOME)):
        text = re.sub(
            rf"({root})((?:/[A-Za-z0-9_.@+\-]+)+)",
            lambda m: m.group(1) + m.group(2).replace("/", "\\"), text)
    return text


def scrub(text: str, work: Path | None = None, project: str = "") -> str:
    """端末制御のうち、静的な HTML にしても意味のないものを落とす。"""
    text = text.replace("\x1b[?25l", "").replace("\x1b[?25h", "")
    text = to_windows_paths(text, work, project)
    # 万一まだ Linux の一時パスが残っていたら、作業フォルダ風に見せる
    text = re.sub(r"/tmp/[A-Za-z0-9_./-]*?/(?=[a-z0-9_-]+\b)", "", text)
    return text


# ---------------------------------------------------------------------------
# 撮るものの定義
# ---------------------------------------------------------------------------
class Capture:
    """1 枚のターミナル画面。複数のコマンドを続けて撮ることもできる。"""

    def __init__(self, name: str, title: str = "Windows PowerShell", note: str = ""):
        self.name = name
        self.title = title
        self.note = note
        self.steps: list[dict] = []

    def add(self, command: str, output: str, prompt: str = PROMPT) -> None:
        self.steps.append({"prompt": prompt, "command": command, "output": output})

    def save(self, versions: dict) -> None:
        OUTPUTS.mkdir(parents=True, exist_ok=True)
        payload = {
            "name": self.name,
            "title": self.title,
            "note": self.note,
            "steps": self.steps,
            "captured_at": date.today().isoformat(),
            "rustc": versions["rustc"],
            "cargo": versions["cargo"],
        }
        (OUTPUTS / f"{self.name}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def versions_now() -> dict:
    def out(*a: str) -> str:
        r = subprocess.run(a, capture_output=True, text=True)
        return r.stdout.strip()
    return {"rustc": out("rustc", "--version"), "cargo": out("cargo", "--version")}


# ---------------------------------------------------------------------------
def capture_versions(versions: dict) -> Capture:
    """バージョン確認。第 1 章の「ちゃんと入ったか」の証拠。"""
    cap = Capture("verify-install", note="インストール直後の確認")
    for cmd in ("rustc --version", "cargo --version", "rustup --version"):
        cap.add(cmd, run_in_pty(cmd.split(), ROOT))
    return cap


# rustup show は実際に走らせられるが、この環境で撮ると host triple が
# x86_64-unknown-linux-gnu になり、Windows の読者にとっては誤りになる。
# そのため実測では扱わず、book/repro.py の再現として置いている。


def capture_cargo_new() -> Capture:
    """cargo new の実物と、作られた Cargo.toml の中身。"""
    cap = Capture("cargo-new", note="cargo new で雛形を作る")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        cap.add("cargo new hello",
                scrub(run_in_pty(["cargo", "new", "hello"], work), work))
        # 生成されたファイルの一覧と Cargo.toml の中身を続けて見せる。
        cap.add("type Cargo.toml",
                (work / "hello" / "Cargo.toml").read_text(encoding="utf-8"),
                prompt="PS C:\\rust\\hello>")
        cap.add("type src\\main.rs",
                (work / "hello" / "src" / "main.rs").read_text(encoding="utf-8"),
                prompt="PS C:\\rust\\hello>")
    return cap


def capture_hello_run() -> Capture:
    """cargo run のいちばん最初の体験。Compiling / Finished / Running の 3 行。"""
    cap = Capture("cargo-run-hello", note="はじめての cargo run")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        run_in_pty(["cargo", "new", "--quiet", "hello"], work)
        project = work / "hello"
        cap.add("cargo run",
                scrub(run_in_pty(["cargo", "run"], project), work, "hello"),
                prompt="PS C:\\rust\\hello>")
        # 2 回目は再ビルドされないことを見せる（Cargo のキャッシュの説明用）
        cap.add("cargo run",
                scrub(run_in_pty(["cargo", "run"], project), work, "hello"),
                prompt="PS C:\\rust\\hello>")
    return cap


def capture_error(name: str, source: Path, edition: str = "2024") -> Capture:
    """わざと通らない例を rustc に食わせ、そのエラー出力を丸ごと撮る。

    ここが本書の中心。本文の「これは E0382 になります」は、
    この捕獲結果と tools/check_errors.py の 2 つで裏打ちされている。
    """
    cap = Capture(f"err-{name}", note=f"{source.name} のコンパイルエラー")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        shutil.copy2(source, work / source.name)
        output = run_in_pty(
            ["rustc", "--edition", edition, "--emit=metadata",
             "-o", os.devnull, source.name], work)
        cap.add(f"rustc {source.name}", scrub(output, work))
    return cap


def capture_project(name: str, project: str, commands: list[str],
                    note: str = "") -> Capture:
    """examples/ の実プロジェクトに対してコマンドを走らせて撮る。"""
    cap = Capture(name, note=note)
    path = EXAMPLES / project
    if not path.exists():
        print(f"  ! examples/{project} がないので飛ばします")
        return cap
    prompt = f"PS C:\\rust\\{project}>"
    for cmd in commands:
        output = run_in_pty(cmd.split(), path)
        # ワークスペースの target/ が親にあるので、実行パスの表示だけ整える。
        output = output.replace(str(EXAMPLES.resolve()), WIN_ROOT)
        cap.add(cmd, scrub(output, None, project.split("-", 1)[0]), prompt=prompt)
    return cap


def capture_cargo_add() -> Capture:
    """cargo add で依存を足す様子。crates.io から実際に解決している。"""
    cap = Capture("cargo-add", note="cargo add で依存クレートを足す")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        run_in_pty(["cargo", "new", "--quiet", "guessing"], work)
        project = work / "guessing"
        cap.add("cargo add rand",
                scrub(run_in_pty(["cargo", "add", "rand"], project), work),
                prompt="PS C:\\rust\\guessing>")
        cap.add("type Cargo.toml",
                (project / "Cargo.toml").read_text(encoding="utf-8"),
                prompt="PS C:\\rust\\guessing>")
    return cap


def capture_clippy_lesson() -> Capture:
    """clippy が何を言ってくるかの実例。第2章で見せる。"""
    cap = Capture("cargo-clippy", note="clippy の指摘の出かた")
    sloppy = """fn main() {
    let numbers = vec![1, 2, 3];
    if numbers.len() == 0 {
        println!("空です");
    }
    let doubled: Vec<i32> = numbers.iter().map(|n| n * 2).collect();
    println!("{:?}", doubled);
}
"""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        run_in_pty(["cargo", "new", "--quiet", "sloppy"], work)
        project = work / "sloppy"
        (project / "src" / "main.rs").write_text(sloppy, encoding="utf-8")
        cap.add("cargo clippy",
                scrub(run_in_pty(["cargo", "clippy"], project), work),
                prompt="PS C:\\rust\\sloppy>")
    return cap


def capture_cli_app() -> Capture:
    """第21章の CLI ツールを、実際に引数付きで動かす。"""
    cap = Capture("cli-app-demo", note="作った ToDo ツールを動かす")
    project = EXAMPLES / "21-cli-app"
    if not project.exists():
        return cap
    binary = EXAMPLES / "target" / "debug" / "ch21_cli_app"
    if not binary.exists():
        run_in_pty(["cargo", "build", "--quiet"], project)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        store = work / "todo.json"
        sequence = [
            ["add", "牛乳を買う", "--priority", "high"],
            ["add", "本を返す"],
            ["add", "請求書を出す", "--priority", "high"],
            ["done", "2"],
            ["list"],
            ["stats"],
        ]
        for args in sequence:
            shown = " ".join(f'"{a}"' if " " in a else a for a in args)
            output = run_in_pty(
                [str(binary), "--file", str(store), *args], work)
            cap.add(f"todo {shown}", scrub(output, work),
                    prompt="PS C:\\rust\\todo>")
    return cap


def capture_release_build() -> Capture:
    """--release の効果。第21章で配布の話に使う。"""
    cap = Capture("cargo-release", note="リリースビルドと実行ファイル")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        run_in_pty(["cargo", "new", "--quiet", "tool"], work)
        project = work / "tool"
        cap.add("cargo build --release",
                scrub(run_in_pty(["cargo", "build", "--release"], project),
                      work, "tool"),
                prompt="PS C:\\rust\\tool>")
    return cap


def capture_rand_old_style() -> Capture:
    """rand 0.8 時代の書き方が、いまどう失敗するかを実際に撮る。

    付録の「古い記事との差分」の主役。ネット記事のとおりに書いた人が
    実際に目にする画面をそのまま見せる。
    """
    cap = Capture("err-rand-old-style", note="古い記事のとおりに書いた場合")
    old_08 = """use rand::Rng;

fn main() {
    let secret = rand::thread_rng().gen_range(1..=100);
    println!("{secret}");
}
"""
    old_09 = """use rand::Rng;

fn main() {
    let secret = rand::rng().random_range(1..=100);
    println!("{secret}");
}
"""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        run_in_pty(["cargo", "new", "--quiet", "guessing"], work)
        project = work / "guessing"
        run_in_pty(["cargo", "add", "--quiet", "rand"], project)
        for label, source in (("0.8 の書き方", old_08), ("0.9 の書き方", old_09)):
            (project / "src" / "main.rs").write_text(source, encoding="utf-8")
            cap.add(f"cargo build   # {label}",
                    scrub(run_in_pty(["cargo", "build"], project), work),
                    prompt="PS C:\\rust\\guessing>")
    return cap


def capture_explain() -> Capture:
    """rustc --explain の実物。付録の「自分で調べる」で使う。"""
    cap = Capture("rustc-explain", note="rustc --explain でエラーの解説を読む")
    output = run_in_pty(["rustc", "--explain", "E0382"], ROOT)
    # 全文は長いので、先頭のあたりだけ見せる
    lines = output.splitlines()
    cap.add("rustc --explain E0382", "\n".join(lines[:24]) + "\n…（続く）")
    return cap


def main() -> int:
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    versions = versions_now()
    if not versions["rustc"]:
        print("rustc が見つかりません。", file=sys.stderr)
        return 1

    print(f"捕獲します（{versions['rustc']}）\n")

    builders: list[tuple[str, callable]] = [
        ("verify-install", lambda: capture_versions(versions)),
        ("cargo-new", capture_cargo_new),
        ("cargo-run-hello", capture_hello_run),
        ("cargo-add", capture_cargo_add),
        ("cargo-clippy", capture_clippy_lesson),
        ("cargo-release", capture_release_build),
        ("rustc-explain", capture_explain),
        ("cli-app-demo", capture_cli_app),
        ("err-rand-old-style", capture_rand_old_style),
    ]

    # 章のサンプルを実際に走らせた出力。本文の「こう出ます」の裏付けになる。
    for name, project, commands in [
        ("run-ownership", "06-ownership", ["cargo run --quiet"]),
        ("run-borrowing", "07-borrowing", ["cargo run --quiet"]),
        ("run-strings", "08-strings", ["cargo run --quiet"]),
        ("run-structs", "09-structs", ["cargo run --quiet"]),
        ("run-enums", "10-enums", ["cargo run --quiet"]),
        ("run-errors", "11-errors", ["cargo run --quiet"]),
        ("run-iterators", "13-iterators", ["cargo run --quiet"]),
        ("run-traits", "14-traits", ["cargo run --quiet"]),
        ("run-modules", "16-modules", ["cargo run --quiet"]),
        ("run-smart-pointers", "18-smart-pointers", ["cargo run --quiet"]),
        ("run-concurrency", "19-concurrency", ["cargo run --quiet"]),
        ("run-async", "20-async", ["cargo run --quiet"]),
        ("cargo-test", "17-testing", ["cargo test"]),
        ("run-guessing", "99-guessing", ["cargo run --quiet"]),
    ]:
        builders.append(
            (name, lambda n=name, p=project, c=commands:
                capture_project(n, p, c, note=f"examples/{p} の実行結果")))

    # エラー例は examples/errors/*.rs から自動で全部撮る。
    for source in sorted(ERRORS.glob("*.rs")):
        stem = source.stem
        builders.append((f"err-{stem}",
                         lambda s=source, n=stem: capture_error(n, s)))

    made = 0
    for name, build in builders:
        if only and not any(o in name for o in only):
            continue
        print(f"  → {name}")
        cap = build()
        if cap.steps:
            cap.save(versions)
            made += 1

    print(f"\noutputs/ に {made} 件を書き出しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
