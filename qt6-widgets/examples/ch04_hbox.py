"""QHBoxLayout — 左から右へ横に並べる。

実行:  python ch04_hbox.py
"""

import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("QHBoxLayout")
window.resize(420, 110)

layout = QHBoxLayout(window)

layout.addWidget(QPushButton("左"))
layout.addWidget(QPushButton("まんなか"))
layout.addWidget(QPushButton("右"))

window.show()

sys.exit(app.exec())
