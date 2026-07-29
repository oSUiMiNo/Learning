"""表示系ウィジェット — 入力を受け取らず、見せることに徹する部品たち。

実行:  python ch05_displays.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLCDNumber,
                               QProgressBar, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("表示系ウィジェット")
window.resize(430, 300)
form = QFormLayout(window)

# ただの文字。
form.addRow("QLabel", QLabel("ふつうの文字を表示する"))

# 簡単な書式なら HTML のような書き方が使える。
rich = QLabel('<b>太字</b>・<i>斜体</i>・<span style="color:#c0392b">色つき</span>')
form.addRow("　└ 書式つき", rich)

# 画像も QLabel で表示する。
pixmap = QPixmap(120, 40)
pixmap.fill(Qt.GlobalColor.darkCyan)
image_label = QLabel()
image_label.setPixmap(pixmap)
form.addRow("　└ 画像", image_label)

# 長い文を折り返す。既定では折り返さないので注意。
wrapped = QLabel(
    "長い文章を入れるときは setWordWrap(True) を忘れずに。"
    "これを付けないと、ウィンドウの外まで一直線に伸びてしまう。"
)
wrapped.setWordWrap(True)
form.addRow("　└ 折り返し", wrapped)

# 進み具合。
bar = QProgressBar()
bar.setValue(64)
form.addRow("QProgressBar", bar)

# 終わりが読めない処理は、範囲を 0-0 にすると「ぐるぐる」になる。
busy = QProgressBar()
busy.setRange(0, 0)
form.addRow("　└ 進行中表示", busy)

# 数字を大きく見せたいとき。
lcd = QLCDNumber()
lcd.setDigitCount(6)
lcd.display(123456)
lcd.setFixedHeight(48)
form.addRow("QLCDNumber", lcd)

window.show()

sys.exit(app.exec())
