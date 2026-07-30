"""本文に載るサンプルが、全部ちゃんとビルドできて動くことを確かめる。

    python tools/check_examples.py
    python tools/check_examples.py 06         # 名前で絞り込む
    python tools/check_examples.py --lenient  # clippy の警告は報告するだけにする

examples/ の下にある Cargo プロジェクトをひとつずつ

    cargo build      → コンパイルが通るか
    cargo test       → テストがあれば通るか
    cargo run        → 実行して異常終了しないか（run = true のものだけ）
    cargo fmt --check → 整形済みか

の順で確かめる。1 つでも落ちたら公開しない。
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

failures: list[str] = []


def projects() -> list[Path]:
    """examples/ 直下の Cargo プロジェクトを列挙する。"""
    return sorted(p.parent for p in EXAMPLES.glob("*/Cargo.toml"))


def has_tests(project: Path) -> bool:
    for path in project.rglob("*.rs"):
        if "#[test]" in path.read_text(encoding="utf-8"):
            return True
        if "```" in path.read_text(encoding="utf-8"):
            return True
    return False


def is_binary(project: Path) -> bool:
    return (project / "src" / "main.rs").exists()


def wants_run(project: Path) -> bool:
    """Cargo.toml の [package.metadata.book] run = false で実行を止められる。

    入力待ちのサンプルや、わざと panic するサンプルのため。
    """
    manifest = tomllib.loads((project / "Cargo.toml").read_text(encoding="utf-8"))
    meta = manifest.get("package", {}).get("metadata", {}).get("book", {})
    return bool(meta.get("run", is_binary(project)))


def step(project: Path, label: str, args: list[str], *, allow_fail: bool = False) -> bool:
    proc = subprocess.run(["cargo", *args], cwd=project,
                          capture_output=True, text=True)
    ok = proc.returncode == 0
    mark = "✓" if ok else ("!" if allow_fail else "✗")
    print(f"    {mark} {label}")
    if not ok and not allow_fail:
        tail = (proc.stderr or proc.stdout).strip().splitlines()
        detail = "\n        ".join(tail[-12:])
        failures.append(f"{project.name} / {label}\n        {detail}")
    return ok


def main() -> int:
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    # 教材に載せるコードなので、clippy の指摘は既定で「落ちる」扱いにする。
    # 意図して破りたいときはコード側に #[allow(...)] と理由を書く。
    strict_clippy = "--lenient" not in sys.argv

    found = projects()
    if only:
        found = [p for p in found if any(o in p.name for o in only)]
    if not found:
        print("examples/ に Cargo プロジェクトがありません。", file=sys.stderr)
        return 1

    rustc = subprocess.run(["rustc", "--version"], capture_output=True, text=True).stdout.strip()
    print(f"{rustc} で {len(found)} プロジェクトを確認します\n")

    for project in found:
        print(f"  {project.name}")
        if not step(project, "cargo build", ["build", "--quiet"]):
            continue
        if has_tests(project):
            step(project, "cargo test", ["test", "--quiet"])
        if wants_run(project):
            step(project, "cargo run", ["run", "--quiet"])
        step(project, "cargo fmt --check", ["fmt", "--check"])
        step(project, "cargo clippy", ["clippy", "--quiet", "--", "-D", "warnings"],
             allow_fail=not strict_clippy)

    if failures:
        print(f"\n{len(failures)} 件のサンプルが問題を抱えています:", file=sys.stderr)
        for f in failures:
            print(f"  ✗ {f}", file=sys.stderr)
        return 1

    print(f"\n{len(found)} プロジェクトすべて問題ありませんでした。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
