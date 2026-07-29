"""ループの中で connect するときの罠と、その回避方法。

ボタンを 3 つ作って「何番のボタンが押されたか」を表示したい。
lambda の中で変数をそのまま使うと、全部同じ値になってしまう。

実行:  python ch03_lambda_trap.py
"""

import sys
from functools import partial

from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("lambda の罠")
window.resize(360, 210)
layout = QVBoxLayout(window)

label = QLabel("どれかを押してください")
layout.addWidget(label)

for i in range(1, 4):
    # ✗ NG: lambda: label.setText(f"{i} 番") と書くと、
    #        呼ばれた時点の i（＝ループ終了後の 3）を見てしまう。
    #
    # ○ OK その1: デフォルト引数で「今の値」を捕まえる
    button = QPushButton(f"{i} 番のボタン")
    button.clicked.connect(lambda checked=False, n=i: label.setText(f"{n} 番が押されました"))
    layout.addWidget(button)

# ○ OK その2: functools.partial を使う（引数の意図がはっきりする）
extra = QPushButton("partial で接続したボタン")
extra.clicked.connect(partial(lambda n: label.setText(f"{n} 番が押されました"), 99))
layout.addWidget(extra)

window.show()

sys.exit(app.exec())
