"""伸び縮みの配分 — stretch 係数とサイズポリシー。

「どの部品に余った空間を渡すか」を決めるのが、この 2 つ。

実行:  python ch04_sizepolicy.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("伸び縮みの配分")
window.resize(520, 300)
outer = QVBoxLayout(window)

# --- ① stretch 係数: 余りを 1 : 2 : 1 の比で配る -------------------------
box = QGroupBox("① addWidget(部品, stretch) で比を決める（1 : 2 : 1）")
row = QHBoxLayout(box)
row.addWidget(QPushButton("1"), 1)
row.addWidget(QPushButton("2 ← 2倍もらう"), 2)
row.addWidget(QPushButton("1"), 1)
outer.addWidget(box)

# --- ② サイズポリシー: 部品自身の「伸びたがり度」を変える -----------------
box = QGroupBox("② Fixed は伸びない / Expanding は伸びる")
row = QHBoxLayout(box)

fixed = QPushButton("Fixed（広がらない）")
fixed.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
row.addWidget(fixed)

expanding = QPushButton("Expanding（余りを吸う）")
expanding.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
row.addWidget(expanding)

outer.addWidget(box)

# --- ③ 余白そのものを調整する --------------------------------------------
box = QGroupBox("③ 余白 (margin) と 間隔 (spacing)")
row = QHBoxLayout(box)
row.setContentsMargins(24, 8, 24, 8)   # 枠の内側の余白（左, 上, 右, 下）
row.setSpacing(24)                     # 部品どうしの間隔
row.addWidget(QLabel("ぴったり"))
row.addWidget(QLabel("じゃなくて"))
row.addWidget(QLabel("ゆったり"))
outer.addWidget(box)

window.show()

sys.exit(app.exec())
