"""レイアウトの入れ子 — 実際の画面はこれで組み立てる。

「縦に積んだものの中に、横並びの列がある」
という構造を addLayout() で作る。

実行:  python ch04_nested.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QPushButton, QVBoxLayout, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("レイアウトの入れ子")
window.resize(460, 300)

# 一番外側は縦並び。
outer = QVBoxLayout(window)
outer.addWidget(QLabel("やることリスト"))

# ① 入力欄とボタンの「横並びの列」を作る。
input_row = QHBoxLayout()
input_row.addWidget(QLineEdit(), 1)          # 第2引数の 1 は「伸びる担当」の意味
input_row.addWidget(QPushButton("追加"))

# ② できた列を、外側の縦並びに差し込む。
#    ウィジェットではなくレイアウトなので addLayout を使う。
outer.addLayout(input_row)

outer.addWidget(QListWidget(), 1)            # 残りの高さはリストに与える

# ③ 下部のボタン列。バネで右に寄せる。
button_row = QHBoxLayout()
button_row.addStretch()
button_row.addWidget(QPushButton("すべて消す"))
button_row.addWidget(QPushButton("保存"))
outer.addLayout(button_row)

window.show()

sys.exit(app.exec())
