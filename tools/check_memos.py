"""教材ごとの研究メモ（`<教材名>/メモ/`）が、決めた書式・不変条件を守っているか検査する。

    python tools/check_memos.py            # 全教材
    python tools/check_memos.py rust       # 教材名で絞り込み（部分一致、複数可、大小無視）

書き方・運用ルールは MEMO.md を参照。ここで検査しているのはその書式面だけで、
未反映（`[ ]`）の行が残っていること自体はエラーにしない。溜まっていて正常な状態。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADER_RE = re.compile(r"^\|\s*内容\s*\|\s*反映状況\s*\|\s*$")
SEP_RE = re.compile(r"^\|\s*-+\s*\|\s*-+\s*\|\s*$")
ROW_RE = re.compile(r"^\|\s*(?P<content>.+?)\s*\|\s*(?P<status>\[[ xX]\])\s*\|\s*$")
LABEL_RE = re.compile(
    r"^(?P<kind>[^\d_\s][^\d_]*)_"
    r"(?P<year>\d{4})_"
    r"(?P<month>0[1-9]|1[0-2])(?P<day>0[1-9]|[12]\d|3[01])_"
    r"(?P<hour>[01]\d|2[0-3])(?P<minute>[0-5]\d)$"
)
ADDENDUM_RE = re.compile(r"^(?P<label>\S+)\n-{3,}\s*$", re.MULTILINE)


def find_memo_dirs() -> list[Path]:
    return sorted(ROOT.glob("*/メモ"))


def memo_files(memo_dir: Path) -> list[Path]:
    files = [p for p in memo_dir.glob("*.md") if p.name != "README.md"]
    done_dir = memo_dir / "反映済"
    if done_dir.exists():
        files += [p for p in done_dir.glob("*.md") if p.name != "README.md"]
    return sorted(files)


def parse_table(lines: list[str], path: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """`#` 見出しの直後にあるチェックボックス表を読む。(行のリスト, エラー) を返す。"""
    errors: list[str] = []
    idx = 0
    # 先頭の `#` 見出しと空行を読み飛ばす
    while idx < len(lines) and (not lines[idx].strip() or lines[idx].startswith("#")):
        idx += 1

    if idx >= len(lines) or not HEADER_RE.match(lines[idx]):
        errors.append(f"{path}: 冒頭にチェックボックス表の見出し行（| 内容 | 反映状況 |）が無い")
        return [], errors

    if idx + 1 >= len(lines) or not SEP_RE.match(lines[idx + 1]):
        errors.append(f"{path}: 見出し行の次に区切り行（| --- | --- |）が無い")
        return [], errors

    rows: list[tuple[str, str]] = []
    i = idx + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        m = ROW_RE.match(lines[i])
        if not m:
            errors.append(f"{path}: 表の行の書式が崩れている: {lines[i]!r}")
        else:
            rows.append((m.group("content"), m.group("status")))
        i += 1

    if not rows:
        errors.append(f"{path}: チェックボックス表に行が無い")
        return [], errors

    if rows[0][0] != "初回":
        errors.append(f"{path}: 表の1行目の内容欄が「初回」ではない: {rows[0][0]!r}")

    seen: set[str] = set()
    for content, _status in rows:
        if content in seen:
            errors.append(f"{path}: 表の内容欄が重複している: {content!r}")
        seen.add(content)
        if content != "初回" and not LABEL_RE.match(content):
            errors.append(
                f"{path}: ラベルの書式が不正（<種別>_<YYYY>_<MMDD>_<HHMM> ではない）: {content!r}"
            )

    return rows, errors


def check_file(path: Path, *, is_done: bool) -> tuple[list[str], list[tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rows, errors = parse_table(lines, path)
    if not rows:
        return errors, []

    if is_done:
        unreflected = [content for content, status in rows if status != "[x]"]
        if unreflected:
            errors.append(
                f"{path}: 反映済フォルダにあるのに未反映の行がある: {unreflected!r}"
            )

    body_labels = {m.group("label") for m in ADDENDUM_RE.finditer(text)}
    table_labels = {content for content, _status in rows if content != "初回"}

    for label in table_labels - body_labels:
        errors.append(f"{path}: 表にラベル {label!r} があるが、本文に対応する追記見出しが無い")
    for label in body_labels - table_labels:
        errors.append(f"{path}: 本文に追記見出し {label!r} があるが、表に対応する行が無い")

    pending = [(path, content) for content, status in rows if status != "[x]"]
    return errors, pending


def main() -> int:
    filters = [f.lower() for f in sys.argv[1:]]
    memo_dirs = find_memo_dirs()
    if filters:
        memo_dirs = [d for d in memo_dirs if any(f in d.parent.name.lower() for f in filters)]
        if not memo_dirs:
            print(f"絞り込み {filters!r} に一致する教材が見つからない", file=sys.stderr)
            return 1

    errors: list[str] = []
    pending: list[tuple[Path, str]] = []

    for memo_dir in memo_dirs:
        done_dir = memo_dir / "反映済"
        for path in memo_files(memo_dir):
            is_done = done_dir in path.parents
            file_errors, file_pending = check_file(path, is_done=is_done)
            errors.extend(file_errors)
            pending.extend(file_pending)

    if pending:
        print("未反映の項目:")
        for path, content in pending:
            print(f"  {path.relative_to(ROOT)}: {content}")
    else:
        print("未反映の項目: なし")

    if errors:
        print("\nエラー:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
