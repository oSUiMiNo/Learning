"""ボタン系ウィジェット。

押す・切り替える・選ぶ、という「操作」を担当する部品たち。

実行:  python ch05_buttons.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox,
                               QFormLayout, QGroupBox, QHBoxLayout,
                               QPushButton, QRadioButton, QToolButton,
                               QVBoxLayout, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("ボタン系ウィジェット")
window.resize(470, 330)
outer = QVBoxLayout(window)

# --- QPushButton ---------------------------------------------------------
box = QGroupBox("QPushButton — 押すたびに何かが起きる")
row = QHBoxLayout(box)
row.addWidget(QPushButton("ふつうのボタン"))

default = QPushButton("既定のボタン")
default.setDefault(True)               # Enter キーで押されるボタン
row.addWidget(default)

toggle = QPushButton("押しっぱなしにできる")
toggle.setCheckable(True)              # ON/OFF を保持する
toggle.setChecked(True)
row.addWidget(toggle)

disabled = QPushButton("使えない状態")
disabled.setEnabled(False)
row.addWidget(disabled)
outer.addWidget(box)

# --- QCheckBox -----------------------------------------------------------
box = QGroupBox("QCheckBox — 独立した ON / OFF")
row = QHBoxLayout(box)
row.addWidget(QCheckBox("自動保存"))
checked = QCheckBox("通知を出す")
checked.setChecked(True)
row.addWidget(checked)
tri = QCheckBox("一部だけ選択中")
tri.setTristate(True)                  # ON / OFF / どちらでもない の 3 状態
# Qt6 では enum を Qt.CheckState.PartiallyChecked のように最後まで書く。
tri.setCheckState(Qt.CheckState.PartiallyChecked)
row.addWidget(tri)
outer.addWidget(box)

# --- QRadioButton --------------------------------------------------------
box = QGroupBox("QRadioButton — この中からひとつだけ")
row = QHBoxLayout(box)
group = QButtonGroup(window)           # 排他の範囲を明示しておくと安全
for i, text in enumerate(["小", "中", "大"]):
    radio = QRadioButton(text)
    radio.setChecked(i == 1)
    group.addButton(radio)
    row.addWidget(radio)
outer.addWidget(box)

# --- QToolButton ---------------------------------------------------------
box = QGroupBox("QToolButton — ツールバー向けの小さなボタン")
form = QFormLayout(box)
tool = QToolButton()
tool.setText("⚙")
form.addRow("アイコンだけ置きたいとき", tool)
outer.addWidget(box)

window.show()

sys.exit(app.exec())
