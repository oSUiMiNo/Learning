"""「ウィンドウが一瞬で消える」典型例と、その直し方。

関数の中でウィンドウを作って、変数をどこにも残さないと、
関数を抜けた瞬間に Python がそれを回収してしまう。

実行:  python ch07_vanishing_window.py
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("消えないサブウィンドウの作り方")
        self.resize(420, 160)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ボタンを押すと別ウィンドウが開きます。"))

        bad = QPushButton("✗ 消えてしまう開き方")
        bad.clicked.connect(self.open_badly)
        layout.addWidget(bad)

        good = QPushButton("○ ちゃんと残る開き方")
        good.clicked.connect(self.open_properly)
        layout.addWidget(good)

    def open_badly(self):
        # sub はローカル変数。この関数を抜けると参照が誰も居なくなり、
        # Python が回収 → C++ 側のウィンドウも破棄され、一瞬で消える。
        sub = QWidget()
        sub.setWindowTitle("すぐ消える")
        sub.resize(240, 120)
        sub.show()

    def open_properly(self):
        # self に持たせて参照を残す。これで生き続ける。
        # （self を親に指定する QWidget(self) でもよい）
        self.sub = QWidget()
        self.sub.setWindowTitle("ちゃんと残る")
        self.sub.resize(240, 120)
        self.sub.show()


app = QApplication(sys.argv)
window = Main()
window.show()
sys.exit(app.exec())
