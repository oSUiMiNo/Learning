"""ウィンドウらしいウィンドウを作る — タイトル・サイズ・中身を持たせる。

実行:  python ch02_window.py
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

app = QApplication(sys.argv)

# 「入れ物」となるウィジェット。これがウィンドウ本体になる。
window = QWidget()
window.setWindowTitle("はじめての Qt ウィンドウ")
window.resize(420, 180)

# 中身を縦に並べるためのレイアウト。
# QVBoxLayout(window) のように親を渡すと、その場で window に適用される。
layout = QVBoxLayout(window)
layout.addWidget(QLabel("ようこそ、Qt Widgets の世界へ。"))
layout.addWidget(QLabel("このウィンドウは 20 行足らずで出来ています。"))

window.show()

sys.exit(app.exec())
