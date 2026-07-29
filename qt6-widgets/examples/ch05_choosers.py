"""選択系ウィジェット — 候補の中から選ばせる部品たち。

実行:  python ch05_choosers.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QComboBox, QDial, QFormLayout,
                               QListWidget, QSlider, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("選択系ウィジェット")
window.resize(420, 320)
form = QFormLayout(window)

# 折りたたまれた選択肢。省スペース。
combo = QComboBox()
combo.addItems(["東京", "大阪", "名古屋", "福岡", "札幌"])
combo.setCurrentIndex(1)
form.addRow("QComboBox", combo)

# 入力もできる選択肢。
editable = QComboBox()
editable.setEditable(True)
editable.addItems(["python", "pyside6", "qt"])
editable.setCurrentText("好きな語を打てる")
form.addRow("　└ 編集可能", editable)

# 一覧から選ぶ。項目数が多いならこちら。
listw = QListWidget()
listw.addItems(["りんご", "みかん", "ぶどう", "もも", "なし"])
listw.setCurrentRow(2)
listw.setFixedHeight(96)
form.addRow("QListWidget", listw)

# 連続した値をつまんで決める。
slider = QSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 100)
slider.setValue(65)
slider.setTickPosition(QSlider.TickPosition.TicksBelow)
slider.setTickInterval(10)
form.addRow("QSlider", slider)

# つまみを回す入力。音量やパンなどに。
dial = QDial()
dial.setRange(0, 100)
dial.setValue(30)
dial.setNotchesVisible(True)
dial.setFixedSize(64, 64)
form.addRow("QDial", dial)

window.show()

sys.exit(app.exec())
