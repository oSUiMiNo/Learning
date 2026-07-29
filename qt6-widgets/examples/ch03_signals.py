"""シグナルとスロット — ボタンが押されたら数を増やす。

「押されたよ」という通知（シグナル）と、
「押されたときにやること」（スロット）をつなぐのが connect。

実行:  python ch03_signals.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("シグナルとスロット")
window.resize(360, 150)

label = QLabel("まだ押されていません")
button = QPushButton("押してください")
button.setObjectName("countButton")  # 教材の自動撮影で使うための名前

layout = QVBoxLayout(window)
layout.addWidget(label)
layout.addWidget(button)

count = 0


def on_clicked():
    """スロット。ただの関数でよい。"""
    global count
    count += 1
    label.setText(f"{count} 回押されました")


# ここが接続。button の clicked シグナルが出たら on_clicked を呼ぶ。
button.clicked.connect(on_clicked)

window.show()

sys.exit(app.exec())
