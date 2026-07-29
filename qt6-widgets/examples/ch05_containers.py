"""まとめ役のウィジェット — 部品をグループ化して整理する。

実行:  python ch05_containers.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QLabel,
                               QPushButton, QScrollArea, QSplitter, QTabWidget,
                               QVBoxLayout, QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("まとめ役のウィジェット")
window.resize(480, 340)
outer = QVBoxLayout(window)

# --- QTabWidget: 画面を切り替える -----------------------------------------
tabs = QTabWidget()

# タブ 1: QGroupBox で関連する設定をひとまとめに。
page1 = QWidget()
page1_layout = QVBoxLayout(page1)
group = QGroupBox("表示に関する設定")
group_layout = QVBoxLayout(group)
group_layout.addWidget(QCheckBox("行番号を表示する"))
group_layout.addWidget(QCheckBox("空白文字を表示する"))
page1_layout.addWidget(group)
page1_layout.addStretch()
tabs.addTab(page1, "一般")

# タブ 2: QScrollArea で入りきらない中身をスクロールさせる。
scroll = QScrollArea()
scroll.setWidgetResizable(True)          # ★これを忘れると中身が潰れる
inner = QWidget()
inner_layout = QVBoxLayout(inner)
for i in range(1, 21):
    inner_layout.addWidget(QPushButton(f"項目 {i}"))
scroll.setWidget(inner)
tabs.addTab(scroll, "スクロール")

# タブ 3: QSplitter で境界をドラッグして幅を変えられるようにする。
splitter = QSplitter(Qt.Orientation.Horizontal)
left = QLabel("左\n（境界をドラッグできる）")
left.setAlignment(Qt.AlignmentFlag.AlignCenter)
right = QLabel("右")
right.setAlignment(Qt.AlignmentFlag.AlignCenter)
splitter.addWidget(left)
splitter.addWidget(right)
splitter.setSizes([300, 150])
tabs.addTab(splitter, "分割")

outer.addWidget(tabs)

window.show()

sys.exit(app.exec())
