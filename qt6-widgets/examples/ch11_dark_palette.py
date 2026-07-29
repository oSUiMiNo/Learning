"""ダークテーマ — QPalette で「色の役割」をまとめて差し替える。

スタイルシートが「見た目の上書き」なのに対し、
パレットは「この役割の色は何色か」という土台の設定。
Fusion スタイルと組み合わせると、どの OS でも同じダークテーマになる。

実行:  python ch11_dark_palette.py
"""

import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
                               QLineEdit, QProgressBar, QPushButton, QWidget)


def dark_palette() -> QPalette:
    palette = QPalette()
    base = QColor(30, 32, 36)        # 入力欄などの背景
    window = QColor(42, 45, 50)      # ウィンドウの地の色
    text = QColor(228, 231, 235)
    accent = QColor(65, 205, 82)

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, window)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, window)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.ToolTipBase, base)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(6, 52, 15))

    # 「使えない状態」のときの色も指定しておくと仕上がりが良い。
    palette.setColor(QPalette.ColorGroup.Disabled,
                     QPalette.ColorRole.Text, QColor(120, 126, 134))
    palette.setColor(QPalette.ColorGroup.Disabled,
                     QPalette.ColorRole.ButtonText, QColor(120, 126, 134))
    return palette


app = QApplication(sys.argv)
app.setStyle("Fusion")               # パレットを素直に反映してくれるスタイル
app.setPalette(dark_palette())

window = QWidget()
window.setWindowTitle("ダークパレット")
window.resize(400, 230)

form = QFormLayout(window)

name = QLineEdit("入力欄の背景は Base の色")
form.addRow("テキスト", name)

combo = QComboBox()
combo.addItems(["選択肢 A", "選択肢 B", "選択肢 C"])
form.addRow("コンボ", combo)

form.addRow("チェック", QCheckBox("選択中の色は Highlight"))

bar = QProgressBar()
bar.setValue(72)
form.addRow("進捗", bar)

form.addRow("ボタン", QPushButton("押せるボタン"))

off = QPushButton("使えないボタン")
off.setEnabled(False)
form.addRow("", off)

window.show()

sys.exit(app.exec())
