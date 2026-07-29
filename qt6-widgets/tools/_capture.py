"""サンプルスクリプトを「そのまま」実行してスクリーンショットを撮る撮影ハーネス。

教材のサンプル (examples/*.py) には撮影用のコードを一切入れたくない。
読者がコピーしてそのまま動かせる、素の PySide6 コードであってほしいからだ。

そこでこのハーネスは QApplication.exec() を一時的に差し替え、
「イベントループに入った直後にキャプチャして終了する」よう外側から仕向ける。
サンプル側は自分が撮影されていることを知らない。

    python tools/_capture.py <出力PNG> <サンプル.py> [操作指示JSON] [待ち時間ms]

操作指示 JSON の例（撮影前にボタンを押してダイアログを開いておきたい場合）:
    [{"action": "click", "target": "askButton", "ms": 400}]

操作は「絶対時刻」で予約する。モーダルダイアログを開くボタンは
click() が戻ってこないため、直列に繋ぐと撮影までたどり着けないからだ。
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QWidget


def _visible_windows() -> list[QWidget]:
    return [w for w in QApplication.topLevelWidgets() if w.isVisible()]


def _find(name: str):
    """objectName で操作対象を探す（QAction のような非ウィジェットも対象）。"""
    for top in QApplication.topLevelWidgets():
        if top.objectName() == name:
            return top
        found = top.findChild(QObject, name)
        if found is not None:
            return found
    raise RuntimeError(f"操作対象が見つかりません: objectName={name!r}")


def _apply(step: dict) -> None:
    action = step.get("action", "wait")
    if action == "wait":
        return
    target = _find(step["target"])
    if action == "click":
        target.click() if hasattr(target, "click") else target.trigger()
    elif action == "trigger":
        target.trigger()
    elif action == "select":
        target.setCurrentIndex(step["index"])
    elif action == "focus":
        target.setFocus()
    elif action == "text":
        target.setText(step["value"])
    else:
        raise RuntimeError(f"未知の操作: {action}")


def _grab(windows: list[QWidget]):
    """ウィンドウを取り込む。

    複数ある（ダイアログが開いている）ときは、画面全体を撮ると
    Xvfb の黒いデスクトップが写り込んでしまう。そこで各ウィンドウを
    個別に取り込み、中立的な色の下地の上に自分で並べ直す。
    """
    if len(windows) == 1:
        return windows[0].grab()

    modal = QApplication.activeModalWidget()
    # 手前に来るべきモーダルダイアログを最後に描く。
    ordered = [w for w in windows if w is not modal] + [w for w in windows if w is modal]

    rect = ordered[0].geometry()
    for w in ordered[1:]:
        rect = rect.united(w.geometry())
    pad = 18
    rect = rect.adjusted(-pad, -pad, pad, pad)

    shots = [(w.geometry().topLeft() - rect.topLeft(), w.grab()) for w in ordered]
    ratio = shots[0][1].devicePixelRatio() or 1.0

    canvas = QPixmap(round(rect.width() * ratio), round(rect.height() * ratio))
    canvas.setDevicePixelRatio(ratio)
    canvas.fill(QColor("#cdc9c2"))          # デスクトップの代わりの下地

    painter = QPainter(canvas)
    for offset, pixmap in shots:
        painter.drawPixmap(offset, pixmap)
    painter.end()
    return canvas


def main() -> int:
    out_path = Path(sys.argv[1]).resolve()
    script = Path(sys.argv[2]).resolve()
    steps = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []
    settle = int(sys.argv[4]) if len(sys.argv) > 4 else 400

    state: dict = {"captured": False, "error": None}
    original_exec = QApplication.exec

    def stop() -> None:
        # モーダルダイアログは自前のイベントループを回しているので、
        # quit() だけでは抜けられない。開いている窓をすべて閉じてから止める。
        for window in _visible_windows():
            window.close()
        QApplication.instance().quit()

    def capture() -> None:
        try:
            windows = _visible_windows()
            if not windows:
                raise RuntimeError("表示中のウィンドウがありません")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            pixmap = _grab(windows)
            if not pixmap.save(str(out_path)):
                raise RuntimeError(f"画像の保存に失敗しました: {out_path}")

            # ウィンドウ枠は HTML/CSS 側で描くので、そのための情報を書き出す。
            ratio = pixmap.devicePixelRatio() or 1.0
            out_path.with_suffix(".json").write_text(
                json.dumps({
                    "title": windows[0].windowTitle(),
                    "css_width": round(pixmap.width() / ratio),
                    "css_height": round(pixmap.height() / ratio),
                    "pixel_width": pixmap.width(),
                    "pixel_height": pixmap.height(),
                    "windows": len(windows),
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            state["captured"] = True
        except Exception as exc:  # noqa: BLE001 - 失敗理由をそのまま伝えたい
            state["error"] = exc
        finally:
            stop()

    def patched_exec() -> int:
        at = settle
        for step in steps:
            def make(s=step):
                def go() -> None:
                    if state["error"] is not None:
                        return
                    try:
                        _apply(s)
                    except Exception as exc:  # noqa: BLE001
                        state["error"] = exc
                        stop()
                return go
            QTimer.singleShot(at, make())
            at += int(step.get("ms", 250))

        QTimer.singleShot(at + 250, capture)
        return original_exec()

    QApplication.exec = staticmethod(patched_exec)

    # サンプルは __main__ として動く前提で書かれているので run_name を合わせる。
    # 末尾の sys.exit(app.exec()) による SystemExit はここで受け止める。
    # 直接 python で起動したときと同じになるよう、サンプルのある場所を import 先に加える
    # （隣のサンプルを import しているものがあるため）。
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script)]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(f"サンプルが異常終了しました ({script.name}): code={exc.code}", file=sys.stderr)
            return 1

    if state["error"] is not None:
        print(f"撮影に失敗しました ({script.name}): {state['error']}", file=sys.stderr)
        return 1
    if not state["captured"]:
        print(f"撮影されませんでした ({script.name}): exec() に到達していない可能性があります",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
