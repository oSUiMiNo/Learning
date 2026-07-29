"""自分でシグナルを作る — Signal と @Slot。

自作のシグナルは「クラス変数」として宣言する。
インスタンス変数（self.xxx = Signal()）にしても動かないので注意。

実行:  python ch03_custom_signal.py
"""

import sys

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
                               QVBoxLayout, QWidget)


class NameForm(QWidget):
    # ★ クラス直下で宣言する。str は「このシグナルが文字列を1つ運ぶ」という意味。
    submitted = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("自作シグナル")
        self.resize(380, 170)

        self.edit = QLineEdit()
        self.edit.setObjectName("nameEdit")
        self.edit.setPlaceholderText("名前を入れて［あいさつ］を押す")

        button = QPushButton("あいさつ")
        button.setObjectName("greetButton")
        button.clicked.connect(self._emit_submitted)

        self.result = QLabel("―")

        layout = QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(button)
        layout.addWidget(self.result)

        # 自分のシグナルを、自分のスロットにつなぐ。
        self.submitted.connect(self.greet)

    def _emit_submitted(self):
        # emit() でシグナルを「発射」する。
        self.submitted.emit(self.edit.text())

    @Slot(str)
    def greet(self, name: str):
        """@Slot を付けると Qt 側に型が伝わり、わずかに速く・安全になる。"""
        self.result.setText(f"こんにちは、{name or 'ななし'} さん！")


app = QApplication(sys.argv)
form = NameForm()
form.show()
sys.exit(app.exec())
