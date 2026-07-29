"""QFormLayout — 「ラベル : 入力欄」の入力フォーム専用レイアウト。

自分でグリッドを組むより短く書けて、
ラベルの位置も OS の作法に合わせて自動で決まる。

実行:  python ch04_form.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
                               QLineEdit, QSpinBox, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("QFormLayout")
window.resize(380, 200)

form = QFormLayout(window)

form.addRow("お名前", QLineEdit())
form.addRow("メール", QLineEdit())

age = QSpinBox()
age.setRange(0, 120)
age.setValue(30)
age.setSuffix(" 歳")
form.addRow("年齢", age)

plan = QComboBox()
plan.addItems(["無料プラン", "標準プラン", "上位プラン"])
form.addRow("プラン", plan)

# ラベルなしで 1 行ぶんを占めさせることもできる。
form.addRow(QCheckBox("お知らせメールを受け取る"))

window.show()

sys.exit(app.exec())
