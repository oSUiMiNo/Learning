"""教材が「Qt5 の書き方は今どうなるか」と書いている内容を、実物で検証する。

    python tools/check_claims.py

第13章の「Qt5 時代の記事との差分・早見表」は、本来いちばん間違えてはいけない表なのに、
Web の記事を写すと簡単に間違える。実際、初稿では PyQt6 の挙動を PySide6 の話として
書いてしまっていた（PySide6 には古い書き方を通す「寛容モード」がある）。

そこで表の各行を、いま入っている PySide6 に対して実際に試して確かめる。
本文を書き換えたら、ここも合わせて更新すること。
"""

from __future__ import annotations

import os
import sys
import warnings

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtGui import QAction, QShortcut  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QMessageBox  # noqa: E402
from PySide6 import QtCore, QtGui, QtWidgets  # noqa: E402

failures: list[str] = []


def expect(claim: str, ok: bool, detail: str = "") -> None:
    print(f"  {'✓' if ok else '✗'} {claim}")
    if not ok:
        failures.append(f"{claim}{' — ' + detail if detail else ''}")


def missing(module, name: str) -> bool:
    return not hasattr(module, name)


def main() -> int:
    app = QApplication(sys.argv)

    print("PySide6 での実測（第0・2・8・13章の記述の裏取り）\n")

    print("【本当に動かなくなったもの】")
    expect("QAction は QtWidgets から消え、QtGui にある",
           missing(QtWidgets, "QAction") and QtGui.QAction is QAction)
    expect("QShortcut は QtWidgets から消え、QtGui にある",
           missing(QtWidgets, "QShortcut") and QtGui.QShortcut is QShortcut)
    expect("QRegExp は QtCore から消えている", missing(QtCore, "QRegExp"))
    expect("QDesktopWidget は QtWidgets から消えている", missing(QtWidgets, "QDesktopWidget"))

    print("\n【動くが非推奨（警告が出る）】")
    label = QLabel("x")
    label.show()
    QTimer.singleShot(30, app.quit)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        app.exec_()
        warned = any("exec_" in str(w.message) for w in caught)
    expect("app.exec_() は動く", True)
    expect("app.exec_() は非推奨の警告を出す", warned,
           "警告が出なくなったなら、本文の書き方を見直すこと")
    expect("QDialog にも exec_ がある", hasattr(QDialog, "exec_"))

    print("\n【動くうえに警告も出ない（PySide6 の寛容モード）】")
    short_forms = {
        "Qt.AlignCenter": (lambda: Qt.AlignCenter, Qt.AlignmentFlag.AlignCenter),
        "Qt.Horizontal": (lambda: Qt.Horizontal, Qt.Orientation.Horizontal),
        "Qt.Checked": (lambda: Qt.Checked, Qt.CheckState.Checked),
        "QMessageBox.Yes": (lambda: QMessageBox.Yes, QMessageBox.StandardButton.Yes),
    }
    for name, (getter, full) in short_forms.items():
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                value = getter()
            same = value == full
            quiet = not caught
        except AttributeError:
            same = quiet = False
            value = None
        expect(f"{name} は使えて、完全修飾版と等しい", same, f"得られた値: {value!r}")
        expect(f"{name} は警告を出さない", quiet)

    print("\n【Qt6 では書く必要がなくなったもの】")
    expect("AA_EnableHighDpiScaling は非推奨として残っている",
           hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"))

    print("\n【モデル / ビューの戻り値（第10・12章）】")
    expect("TextAlignmentRole は int() で包まなくてよい",
           int(Qt.AlignmentFlag.AlignRight) == Qt.AlignmentFlag.AlignRight.value)
    expect("int の 2 は Qt.CheckState.Checked と等しくない（setData の落とし穴）",
           2 != Qt.CheckState.Checked)
    expect("Qt.CheckState(2) は Checked と等しい",
           Qt.CheckState(2) == Qt.CheckState.Checked)

    print("\n【付属コマンド（第1・9章）】")
    from shutil import which
    for command in ("pyside6-designer", "pyside6-uic", "pyside6-rcc", "pyside6-lupdate"):
        expect(f"{command} が使える", which(command) is not None)

    print("\n【対応する Python の範囲（第0・1章）】")
    # 第0章の表と第1章の「3.10 以上 3.14 以下」が、パッケージの実際の宣言と合っているか。
    import importlib.metadata as metadata
    requires = metadata.metadata("PySide6").get("Requires-Python", "")
    expect(f"下限が 3.10（宣言: {requires}）", ">=3.10" in requires.replace(" ", ""),
           "本文の『3.10 以上』を実際の下限に合わせること")
    expect("上限が 3.15 未満 ＝ 3.14 まで", "<3.15" in requires.replace(" ", ""),
           "本文の『3.14 以下』を実際の上限に合わせること")

    if failures:
        print(f"\n本文の記述と実物が食い違っています（{len(failures)} 件）:", file=sys.stderr)
        for f in failures:
            print(f"  ✗ {f}", file=sys.stderr)
        return 1

    print("\n本文に書いてある挙動は、すべて実物と一致しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
