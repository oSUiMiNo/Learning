"""addStretch — 「見えないバネ」で余白を配る。

ダイアログの［OK］［キャンセル］を右に寄せる、あの定番の書き方。

実行:  python ch04_stretch.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout,
                               QPushButton, QVBoxLayout, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("addStretch でボタンを寄せる")
window.resize(440, 260)
outer = QVBoxLayout(window)

# --- ① 何もしない: ボタンが横幅いっぱいに引き伸ばされる -------------------
plain = QGroupBox("① そのまま並べた場合")
row = QHBoxLayout(plain)
row.addWidget(QPushButton("OK"))
row.addWidget(QPushButton("キャンセル"))
outer.addWidget(plain)

# --- ② 先頭にバネ: ボタンが右に寄る ---------------------------------------
right = QGroupBox("② 先頭に addStretch()")
row = QHBoxLayout(right)
row.addStretch()                       # ここにバネが入る
row.addWidget(QPushButton("OK"))
row.addWidget(QPushButton("キャンセル"))
outer.addWidget(right)

# --- ③ 両端にバネ: ボタンが中央に寄る -------------------------------------
center = QGroupBox("③ 両端に addStretch()")
row = QHBoxLayout(center)
row.addStretch()
row.addWidget(QPushButton("OK"))
row.addWidget(QPushButton("キャンセル"))
row.addStretch()
outer.addWidget(center)

window.show()

sys.exit(app.exec())
