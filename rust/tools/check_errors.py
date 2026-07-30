"""「コンパイルが通らない例」が、本当に宣言どおりのエラーで落ちることを確かめる。

    python tools/check_errors.py
    python tools/check_errors.py e0382     # 名前で絞り込む

Rust の入門書では「これはコンパイルエラーになります」という例が主役になる。
ところがこの手の記述は、言語の変化でいちばん先に嘘になる。
借用検査が賢くなって通るようになったり、エラーコードが変わったりするからだ。

そこで各サンプルの先頭に期待するエラーコードを書いておき、
実際に rustc に食わせて突き合わせる。食い違ったら公開を止める。

    //! expect: E0382
    //! title: move した後の変数を使ってしまう
    //! chapter: 06-ownership

複数のコードを期待するときはカンマで並べる（例: `expect: E0499, E0502`）。
「エラーにならないこと」を確かめたいときは `expect: ok` と書く。
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS = ROOT / "examples" / "errors"

HEADER_RE = re.compile(r"^//!\s*(\w+)\s*:\s*(.+?)\s*$", re.M)

failures: list[str] = []


def read_header(source: Path) -> dict:
    text = source.read_text(encoding="utf-8")
    return {k: v for k, v in HEADER_RE.findall(text)}


def compile_for_diagnostics(source: Path, edition: str) -> list[dict]:
    """rustc に JSON で診断を出させ、error レベルのものを返す。"""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copy2(source, work / source.name)
        proc = subprocess.run(
            ["rustc", "--edition", edition, "--error-format=json",
             "--emit=metadata", "-o", os.devnull, source.name],
            cwd=work, capture_output=True, text=True)

    diagnostics = []
    for line in proc.stderr.splitlines():
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if data.get("level") == "error":
            diagnostics.append(data)
    return diagnostics


def codes_of(diagnostics: list[dict]) -> list[str]:
    found = []
    for d in diagnostics:
        code = (d.get("code") or {}).get("code")
        if code:
            found.append(code)
    return found


def check(source: Path) -> None:
    header = read_header(source)
    expect_raw = header.get("expect")
    edition = header.get("edition", "2024")

    if not expect_raw:
        failures.append(f"{source.name}: 先頭に `//! expect: ...` がありません")
        return

    diagnostics = compile_for_diagnostics(source, edition)
    found = codes_of(diagnostics)

    if expect_raw.strip().lower() == "ok":
        if diagnostics:
            failures.append(
                f"{source.name}: 通るはずなのにエラーになりました "
                f"（{', '.join(found) or diagnostics[0].get('message', '')[:60]}）")
            print(f"  ✗ {source.name}  期待: 通る / 実際: {', '.join(found) or 'エラー'}")
        else:
            print(f"  ✓ {source.name}  通る")
        return

    expected = [c.strip() for c in expect_raw.split(",") if c.strip()]
    missing = [c for c in expected if c not in found]

    if not diagnostics:
        failures.append(
            f"{source.name}: {', '.join(expected)} で落ちるはずが、コンパイルが通りました"
            "（言語側が緩くなった可能性があります。本文の記述を見直してください）")
        print(f"  ✗ {source.name}  期待: {', '.join(expected)} / 実際: エラーなし")
        return

    if missing:
        failures.append(
            f"{source.name}: 期待した {', '.join(missing)} が出ませんでした"
            f"（実際に出たのは {', '.join(found) or '（コード無しのエラー）'}）")
        print(f"  ✗ {source.name}  期待: {', '.join(expected)} / 実際: {', '.join(found) or '?'}")
        return

    title = header.get("title", "")
    extra = f"  ({title})" if title else ""
    print(f"  ✓ {source.name}  {', '.join(expected)}{extra}")


def main() -> int:
    only = [a.lower() for a in sys.argv[1:] if not a.startswith("-")]
    sources = sorted(ERRORS.glob("*.rs"))
    if only:
        sources = [s for s in sources if any(o in s.name.lower() for o in only)]

    if not sources:
        print("examples/errors/ に .rs がありません。", file=sys.stderr)
        return 1

    rustc = subprocess.run(["rustc", "--version"], capture_output=True, text=True).stdout.strip()
    print(f"{rustc} で {len(sources)} 件を検証します\n")

    for source in sources:
        check(source)

    if failures:
        print(f"\n本文の主張と実物が食い違っています（{len(failures)} 件）:", file=sys.stderr)
        for f in failures:
            print(f"  ✗ {f}", file=sys.stderr)
        return 1

    print(f"\n{len(sources)} 件すべて、宣言どおりのエラーで落ちました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
