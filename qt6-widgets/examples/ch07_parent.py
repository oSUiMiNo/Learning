"""親子関係 — Qt のオブジェクトツリーを目で見る。

親を設定すると、
  ・子は親と同じウィンドウの中に描かれる
  ・親が破棄されるとき、子もまとめて破棄される
  ・Python 側で変数を持っていなくても、親が参照を握るので消えない

実行:  python ch07_parent.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("親子関係")
window.resize(420, 220)
layout = QVBoxLayout(window)

# ① 親を明示して作る。Python 側で変数に残さなくても、親が参照を持つので消えない。
#    ただし親を持たせただけでは位置は決まらないので、レイアウトにも入れる。
layout.addWidget(QLabel("① 親を指定して作ったラベル", parent=window))

# ② レイアウトに追加すると、親は自動的に設定される。
#    addWidget() の中で setParent() 相当のことが行われている。
button = QPushButton("② レイアウトに入れたボタン")
layout.addWidget(button)

# 親子関係を確認してみる。
layout.addWidget(QLabel(f"button の親: {button.parent().__class__.__name__}"))
layout.addWidget(QLabel(f"window の親: {window.parent()}  ← 親なし＝ウィンドウ"))
layout.addWidget(QLabel(f"window の子の数: {len(window.children())}"))

window.show()

sys.exit(app.exec())
