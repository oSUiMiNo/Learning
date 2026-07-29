"""教材に載っている全サンプルが、実際にエラーなく動くことを確かめる。

    python tools/check_examples.py

各サンプルを QT_QPA_PLATFORM=offscreen（画面なし）で起動し、
イベントループに入った直後に終了させる。例外・Qt の警告が出たら失敗扱い。

本文に載るコードはここにある .py そのものなので、
このチェックが通っている限り「本に書いてあるとおりに書けば動く」ことが保証される。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

# 起動して即終了させるための小細工。サンプル自体は一切変更しない。
DRIVER = """
import runpy, sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

_orig = QApplication.exec

def _exec():
    QTimer.singleShot(120, QApplication.instance().quit)
    return _orig()

QApplication.exec = staticmethod(_exec)
sys.argv = [sys.argv[1]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""

# Qt が出す「無視してよい」ノイズ。これ以外の stderr 出力は失敗とみなす。
IGNORABLE = (
    "QStandardPaths:",
    "Fontconfig",
    "qt.qpa.fonts",
    # offscreen プラットフォームが必ず出すもの。実行環境の都合であって
    # サンプルの問題ではない。
    "propagateSizeHints",
)


def is_noise(line: str) -> bool:
    return not line.strip() or any(token in line for token in IGNORABLE)


def check(script: Path) -> tuple[bool, str]:
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_LOGGING_RULES": "qt.qpa.*=false"}
    try:
        result = subprocess.run(
            [sys.executable, "-c", DRIVER, str(script)],
            capture_output=True, text=True, timeout=60, env=env, cwd=script.parent,
        )
    except subprocess.TimeoutExpired:
        return False, "タイムアウト（イベントループから抜けられていない可能性）"

    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()

    problems = [ln for ln in result.stderr.splitlines() if not is_noise(ln)]
    if problems:
        return False, "\n".join(problems)
    return True, ""


def main() -> int:
    # ui_*.py は pyside6-uic の生成物で、単体では起動しない（画面の組み立て手順書）。
    scripts = sorted(p for p in EXAMPLES.glob("*.py")
                     if not p.name.startswith(("_", "ui_")))
    if not scripts:
        print("サンプルが 1 つも見つかりません", file=sys.stderr)
        return 1

    print(f"サンプルの動作チェック（{len(scripts)} 件）\n")
    failed = []
    for script in scripts:
        ok, detail = check(script)
        print(f"  {'✓' if ok else '✗'} {script.name}")
        if not ok:
            failed.append((script.name, detail))

    if failed:
        print(f"\n{len(failed)} 件が失敗しました:\n", file=sys.stderr)
        for name, detail in failed:
            print(f"--- {name} ---\n{detail}\n", file=sys.stderr)
        return 1

    print(f"\n全 {len(scripts)} 件が正常に起動・終了しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
