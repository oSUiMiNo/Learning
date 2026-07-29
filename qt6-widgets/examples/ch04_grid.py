"""QGridLayout — 格子に並べる。電卓のようなキーパッドが得意。

addWidget(部品, 行, 列) の行・列は 0 から数える。
最後の 2 つの引数で「何行ぶん・何列ぶん占めるか」を指定できる。

実行:  python ch04_grid.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QGridLayout, QLineEdit,
                               QPushButton, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("QGridLayout")
window.resize(300, 260)

grid = QGridLayout(window)

display = QLineEdit("0")
display.setReadOnly(True)
# 0 行 0 列に置き、1 行ぶん・4 列ぶんを占める。
grid.addWidget(display, 0, 0, 1, 4)

keys = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("÷", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("×", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("−", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
]
for text, row, col in keys:
    grid.addWidget(QPushButton(text), row, col)

window.show()

sys.exit(app.exec())
