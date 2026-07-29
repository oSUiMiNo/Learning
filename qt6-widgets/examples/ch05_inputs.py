"""入力系ウィジェット — 文字・数値・日付を受け取る部品たち。

実行:  python ch05_inputs.py
"""

import sys

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QApplication, QDateEdit, QDoubleSpinBox,
                               QFormLayout, QLineEdit, QPlainTextEdit,
                               QSpinBox, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("入力系ウィジェット")
window.resize(430, 330)
form = QFormLayout(window)

# 1 行のテキスト入力。
name = QLineEdit()
name.setPlaceholderText("山田 太郎")
form.addRow("QLineEdit", name)

# パスワード入力は echoMode を変えるだけ。
password = QLineEdit()
password.setEchoMode(QLineEdit.EchoMode.Password)
password.setText("himitsu")
form.addRow("　└ パスワード", password)

# 整数。範囲・単位・きざみを指定できる。
count = QSpinBox()
count.setRange(1, 99)
count.setValue(3)
count.setSuffix(" 個")
form.addRow("QSpinBox", count)

# 小数。
price = QDoubleSpinBox()
price.setRange(0, 1_000_000)
price.setValue(1280.5)
price.setPrefix("¥ ")
price.setDecimals(1)
form.addRow("QDoubleSpinBox", price)

# 日付。カレンダーも出せる。
day = QDateEdit()
day.setDate(QDate(2026, 7, 29))
day.setCalendarPopup(True)
form.addRow("QDateEdit", day)

# 複数行のテキスト。書式なしの入力なら QTextEdit よりこちらが軽い。
memo = QPlainTextEdit()
memo.setPlainText("複数行のメモ。\n書式なしのテキストならこれが定番。")
memo.setFixedHeight(80)
form.addRow("QPlainTextEdit", memo)

window.show()

sys.exit(app.exec())
