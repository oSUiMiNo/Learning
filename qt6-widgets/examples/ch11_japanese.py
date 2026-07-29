"""標準ボタンを日本語にする — Qt 自身の翻訳ファイルを読み込む。

［OK］［Cancel］［Yes］［No］などは Qt が用意している文言なので、
自分で翻訳する必要はない。Qt に同梱されている qtbase_ja.qm を
読み込むだけで日本語になる。

読み込みは QApplication を作った直後、画面を作る前に行うこと。

実行:  python ch11_japanese.py
"""

import sys

from PySide6.QtCore import QLibraryInfo, QTranslator
from PySide6.QtWidgets import (QApplication, QDialogButtonBox, QLabel,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)

app = QApplication(sys.argv)

# --- ここが本題 -----------------------------------------------------------
translator = QTranslator()

# Qt 本体の翻訳ファイルが置かれている場所を、Qt 自身に聞く。
translations = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)

# 日本語に決め打ちする場合（OS の言語設定に関係なく日本語にしたいとき）。
if translator.load("qtbase_ja", translations):
    app.installTranslator(translator)

# OS の言語設定に合わせたいときは、代わりにこちら。
#   from PySide6.QtCore import QLocale
#   translator.load(QLocale.system(), "qtbase", "_", translations)
#
# translator は変数に持ち続けること。捨てると翻訳も一緒に消える。
# --------------------------------------------------------------------------

window = QWidget()
window.setWindowTitle("標準ボタンの日本語化")
window.resize(400, 210)
layout = QVBoxLayout(window)

layout.addWidget(QLabel("Qt が用意している文言は、翻訳ファイルを読むだけで日本語になる。"))

# QDialogButtonBox の標準ボタン。
buttons = QDialogButtonBox(
    QDialogButtonBox.StandardButton.Ok
    | QDialogButtonBox.StandardButton.Cancel
    | QDialogButtonBox.StandardButton.Apply
    | QDialogButtonBox.StandardButton.Help
)
layout.addWidget(buttons)

ask = QPushButton("はい / いいえ のダイアログを出す")
ask.setObjectName("askButton")
ask.clicked.connect(lambda: QMessageBox.question(window, "確認", "この操作を続けますか？"))
layout.addWidget(ask)

layout.addStretch()

window.show()

sys.exit(app.exec())
