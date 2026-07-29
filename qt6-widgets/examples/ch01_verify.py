"""環境が正しく整ったかを確認する。

この教材と同じバージョンで動いているかを、実際にウィンドウを出して確かめる。

実行:  python ch01_verify.py
"""

import sys

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import qVersion
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("環境チェック")
layout = QVBoxLayout(window)

layout.addWidget(QLabel("✅ Qt が正しく動いています"))
layout.addWidget(QLabel(f"PySide6 : {pyside_version}"))
layout.addWidget(QLabel(f"Qt      : {qVersion()}"))
layout.addWidget(QLabel(f"Python  : {sys.version.split()[0]}"))

window.show()

sys.exit(app.exec())
