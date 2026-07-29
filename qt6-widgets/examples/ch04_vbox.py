"""QVBoxLayout — 上から下へ縦に並べる。

実行:  python ch04_vbox.py
"""

import sys

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("QVBoxLayout")
window.resize(320, 200)

# 親ウィジェットを渡してレイアウトを作ると、その場で window に適用される。
layout = QVBoxLayout(window)

layout.addWidget(QPushButton("上"))
layout.addWidget(QPushButton("なか"))
layout.addWidget(QPushButton("下"))

window.show()

sys.exit(app.exec())
