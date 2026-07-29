"""C++ 版サンプルを実際にビルドして起動し、スクリーンショットを撮る。

    python tools/shots_cpp.py

Python 版（tools/shots.py）と違い、相手は自前のプロセスなので
QApplication.exec() を差し替える手は使えない。そこで
「Xvfb 上で C++ アプリを起動 → 別プロセスの Qt で画面を取り込む」形にしている。

Qt6 の C++ 開発環境（qt6-base-dev など）が入っていない場合は、
何もせず終了する。教材の Python 側のビルドを止めないため。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CPP = ROOT / "examples" / "cpp"
OUT_DIR = ROOT.parent / "docs" / "img"
BUILD = ROOT / "tools" / ".cpp-build"
SCALE = 2

# name, 実行ファイル, ウィンドウタイトル, CSS 上の大きさ
SHOTS = [
    ("cpp-ch02-window", "ch02_window", "はじめての Qt ウィンドウ", 420, 180),
    ("cpp-ch03-signals", "ch03_signals", "シグナルとスロット（C++）", 360, 150),
]

# 画面全体から切り出すための取り込みスクリプト（別プロセスで動かす）。
GRABBER = """
import sys
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
out, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
# grabWindow に渡すのは拡大前の座標。取り込み側も 2 倍で動いているので、
# 出来上がる画像は自動的に 2 倍の画素数になる。
# ウィンドウマネージャがないため、ウィンドウは必ず原点に置かれる。
pix = app.primaryScreen().grabWindow(0, 0, 0, w, h)
if not pix.save(out):
    raise SystemExit("保存に失敗しました")
"""


def configure() -> subprocess.CompletedProcess:
    return subprocess.run(
        ["cmake", "-S", str(CPP), "-B", str(BUILD), "-DCMAKE_BUILD_TYPE=Release"],
        capture_output=True, text=True)


def build(result: subprocess.CompletedProcess) -> bool:
    if result.returncode != 0:
        print(result.stdout[-1500:], result.stderr[-1500:], file=sys.stderr)
        return False
    compiled = subprocess.run(["cmake", "--build", str(BUILD), "-j4"],
                              capture_output=True, text=True)
    if compiled.returncode != 0:
        print(compiled.stdout[-1500:], compiled.stderr[-1500:], file=sys.stderr)
        return False
    return True


def qt_cxx_version() -> str:
    """ビルドに使われた Qt のバージョンを qmake に聞く。"""
    for command in ("qmake6", "/usr/lib/qt6/bin/qmake6"):
        try:
            out = subprocess.run([command, "-query", "QT_VERSION"],
                                 capture_output=True, text=True)
        except OSError:
            continue
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    return "不明"


def capture(name: str, binary: str, title: str, w: int, h: int, index: dict) -> bool:
    exe = BUILD / binary
    if not exe.exists():
        print(f"  ✗ {name}: 実行ファイルがありません")
        return False

    png = BUILD / f"{name}.png"
    # C++ アプリと取り込み役を、同じ Xvfb の画面に同居させる。
    script = (
        f'{exe} & APP=$!; sleep 1.6; '
        f'"{sys.executable}" -c \'{GRABBER}\' "{png}" {w} {h}; '
        f'RC=$?; kill $APP 2>/dev/null; wait $APP 2>/dev/null; exit $RC'
    )
    env = {**os.environ, "QT_SCALE_FACTOR": str(SCALE), "QT_STYLE_OVERRIDE": "Fusion",
           "QT_QPA_PLATFORM": "xcb"}
    result = subprocess.run(
        ["xvfb-run", "-a", "-s", "-screen 0 2000x1400x24", "bash", "-c", script],
        capture_output=True, text=True, env=env, timeout=120)

    if not png.exists():
        print(f"  ✗ {name}\n{result.stdout[-800:]}\n{result.stderr[-800:]}")
        return False

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    webp = OUT_DIR / f"{name}.webp"
    with Image.open(png) as im:
        im.convert("RGB").save(webp, "WEBP", quality=92, method=6)

    index[name] = {
        "name": name, "file": f"img/{webp.name}", "script": f"cpp/{binary}.cpp",
        "title": title, "css_width": w, "css_height": h,
        "pixel_width": w * SCALE, "pixel_height": h * SCALE, "windows": 1,
        "note": "C++ 版をビルドして実行したもの", "bytes": webp.stat().st_size,
    }
    print(f"  ✓ {name:22s} {w}×{h}  {webp.stat().st_size / 1024:.0f} KB  「{title}」")
    return True


def main() -> int:
    if shutil.which("cmake") is None:
        print("cmake がないため、C++ 版の撮影は飛ばします。")
        return 0

    print("C++ 版サンプルをビルドします")
    configured = configure()
    if configured.returncode != 0 and "Qt6" in (configured.stderr + configured.stdout):
        print("Qt6 の C++ 開発環境が見つからないため、C++ 版の撮影は飛ばします。")
        print("（Ubuntu なら: sudo apt install qt6-base-dev cmake g++）")
        return 0
    if not build(configured):
        print("ビルドに失敗しました", file=sys.stderr)
        return 1

    version = qt_cxx_version()
    print(f"ビルド成功（Qt {version}）。撮影します")

    index_path = OUT_DIR / "shots.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}

    failed = [s[0] for s in SHOTS if not capture(*s, index)]

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.rmtree(BUILD, ignore_errors=True)

    if failed:
        print(f"\n失敗: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"\n完了。{len(SHOTS)} 件を {OUT_DIR} に出力しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
