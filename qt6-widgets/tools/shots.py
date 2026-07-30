"""教材のスクリーンショットを、実際にサンプルを動かして生成する。

    python tools/shots.py            # 全部撮り直す
    python tools/shots.py ch04       # 名前に ch04 を含むものだけ

撮影は Xvfb 上の実 Qt で行われ、2 倍解像度でキャプチャして WebP に変換する。
ウィンドウ枠（タイトルバー）は画像には焼き込まず、HTML/CSS 側で描く。
そのためのメタ情報（実際のウィンドウタイトルとサイズ）は
img/<name>.json に書き出され、build.py が読む。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
# 出力先は build.py の DOCS と一致させること。
# ここがずれると、撮った画像と shots.json を build.py が見つけられない。
OUT_DIR = ROOT.parent / "docs" / "qt6-widgets" / "img"
SCALE = 2


def shot(name: str, script: str, *, steps=None, settle: int = 450, note: str = "") -> dict:
    return {"name": name, "script": script, "steps": steps or [], "settle": settle, "note": note}


# ---------------------------------------------------------------------------
# 撮影リスト。name がそのまま docs/img/<name>.webp になる。
# steps は撮影前の操作（ボタンを押してダイアログを出す、など）。
# ---------------------------------------------------------------------------
SHOTS = [
    shot("ch01-verify", "ch01_verify.py", note="バージョン確認ツールの実行結果"),
    shot("ch02-hello", "ch02_hello.py", note="最小構成のウィンドウ"),
    shot("ch02-window", "ch02_window.py", note="タイトルとサイズを持つウィンドウ"),
    shot("ch03-signals", "ch03_signals.py", steps=[
        {"action": "click", "target": "countButton"},
        {"action": "click", "target": "countButton"},
        {"action": "click", "target": "countButton"},
    ], note="ボタンを 3 回押した状態"),
    shot("ch03-custom-signal", "ch03_custom_signal.py", steps=[
        {"action": "text", "target": "nameEdit", "value": "すずき"},
        {"action": "click", "target": "greetButton"},
    ], note="自作シグナルが飛んだ後"),
    shot("ch04-vbox", "ch04_vbox.py", note="QVBoxLayout"),
    shot("ch04-hbox", "ch04_hbox.py", note="QHBoxLayout"),
    shot("ch04-stretch", "ch04_stretch.py", note="addStretch による寄せ"),
    shot("ch04-grid", "ch04_grid.py", note="QGridLayout"),
    shot("ch04-form", "ch04_form.py", note="QFormLayout"),
    shot("ch04-nested", "ch04_nested.py", note="レイアウトの入れ子"),
    shot("ch04-sizepolicy", "ch04_sizepolicy.py", note="サイズポリシーの効き方"),
    shot("ch05-buttons", "ch05_buttons.py", note="ボタン系ウィジェット"),
    shot("ch05-inputs", "ch05_inputs.py", note="入力系ウィジェット"),
    shot("ch05-choosers", "ch05_choosers.py", note="選択系ウィジェット"),
    shot("ch05-displays", "ch05_displays.py", note="表示系ウィジェット"),
    shot("ch05-containers", "ch05_containers.py", note="まとめ役のウィジェット"),
    shot("ch06-mainwindow", "ch06_mainwindow.py", note="QMainWindow の全体像"),
    shot("ch06-menu", "ch06_mainwindow.py", steps=[
        {"action": "click", "target": "aboutAction"},
    ], settle=500, note="メニュー項目を実行した直後"),
    shot("ch08-messagebox", "ch08_messagebox.py", steps=[
        {"action": "click", "target": "askButton"}, {"action": "wait", "ms": 400},
    ], note="QMessageBox の質問ダイアログ"),
    shot("ch08-custom-dialog", "ch08_custom_dialog.py", steps=[
        {"action": "click", "target": "openButton"}, {"action": "wait", "ms": 400},
    ], note="自作ダイアログ"),
    shot("ch09-designer-result", "ch09_designer_app.py", note=".ui から作った画面"),
    shot("ch10-tableview", "ch10_tableview.py", note="QTableView + 自作モデル"),
    shot("ch10-filter", "ch10_filter.py", steps=[
        {"action": "text", "target": "filterEdit", "value": "ラ"},
    ], note="QSortFilterProxyModel による絞り込み"),
    shot("ch11-stylesheet", "ch11_stylesheet.py", note="Qt Style Sheets を当てた画面"),
    shot("ch11-dark", "ch11_dark_palette.py", note="ダークパレット"),
    shot("ch11-japanese", "ch11_japanese.py", note="標準ボタンが日本語になった状態"),
    shot("ch11-japanese-dialog", "ch11_japanese.py", steps=[
        {"action": "click", "target": "askButton", "ms": 450},
    ], note="日本語化された QMessageBox"),
    shot("ch12-todo", "ch12_todo_app.py", note="完成した ToDo アプリ"),
    shot("ch12-todo-done", "ch12_todo_app.py", steps=[
        {"action": "text", "target": "inputEdit", "value": "牛乳を買う"},
        {"action": "click", "target": "addButton"},
        {"action": "text", "target": "inputEdit", "value": "Qt の教材を読む"},
        {"action": "click", "target": "addButton"},
        {"action": "text", "target": "inputEdit", "value": "散歩に行く"},
        {"action": "click", "target": "addButton"},
    ], note="項目を追加した状態"),
]


def capture_one(spec: dict, tmp_dir: Path) -> dict | None:
    script = EXAMPLES / spec["script"]
    if not script.exists():
        print(f"  ✗ {spec['name']}: サンプルがありません ({script.name})")
        return None

    png = tmp_dir / f"{spec['name']}.png"
    # データを保存するサンプル（ToDo アプリ）が前回の実行結果を読み込まないよう、
    # 保存先を撮影ごとに使い捨てのディレクトリへ向ける。
    data_home = tmp_dir / f"{spec['name']}-home"
    shutil.rmtree(data_home, ignore_errors=True)
    data_home.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "QT_SCALE_FACTOR": str(SCALE),
        "QT_STYLE_OVERRIDE": "Fusion",
        "QT_LOGGING_RULES": "qt.qpa.*=false",
        "XDG_DATA_HOME": str(data_home),
    }
    cmd = [
        "xvfb-run", "-a", "-s", "-screen 0 2800x1800x24",
        sys.executable, str(ROOT / "tools" / "_capture.py"),
        str(png), str(script), json.dumps(spec["steps"]), str(spec["settle"]),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=EXAMPLES,
                            timeout=120, env=env)
    if result.returncode != 0 or not png.exists():
        print(f"  ✗ {spec['name']}\n{result.stdout}\n{result.stderr}")
        return None

    meta = json.loads(png.with_suffix(".json").read_text(encoding="utf-8"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    webp = OUT_DIR / f"{spec['name']}.webp"
    with Image.open(png) as im:
        im.convert("RGB").save(webp, "WEBP", quality=92, method=6)

    meta.update({
        "name": spec["name"],
        "file": f"img/{webp.name}",
        "script": spec["script"],
        "note": spec["note"],
        "bytes": webp.stat().st_size,
    })
    print(f"  ✓ {spec['name']:22s} {meta['css_width']}×{meta['css_height']}  "
          f"{meta['bytes'] / 1024:.0f} KB  「{meta['title']}」")
    return meta


def main() -> int:
    if shutil.which("xvfb-run") is None:
        print("xvfb-run が見つかりません（apt install xvfb）", file=sys.stderr)
        return 1

    pattern = sys.argv[1] if len(sys.argv) > 1 else ""
    targets = [s for s in SHOTS if pattern in s["name"]]
    if not targets:
        print(f"該当する撮影対象がありません: {pattern!r}", file=sys.stderr)
        return 1

    tmp_dir = ROOT / "tools" / ".shots-tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"スクリーンショットを撮影します（{len(targets)} 件, {SCALE}x）")
    index_path = OUT_DIR / "shots.json"
    index = {}
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))

    failed = []
    for spec in targets:
        meta = capture_one(spec, tmp_dir)
        if meta is None:
            failed.append(spec["name"])
        else:
            index[spec["name"]] = meta

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.rmtree(tmp_dir, ignore_errors=True)

    if failed:
        print(f"\n失敗: {len(failed)} 件 -> {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"\n完了。{len(targets)} 件を {OUT_DIR} に出力しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
