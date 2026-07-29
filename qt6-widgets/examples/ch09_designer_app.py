"""Qt Designer で作った .ui を使う（方法 1: pyside6-uic で Python に変換する）。

事前に 1 回だけ実行しておく:
    pyside6-uic ch09_form.ui -o ui_ch09_form.py

生成された Ui_ProfileForm は「画面を組み立てる手順書」であって
ウィジェットそのものではない。QWidget と一緒に継承して使う。

実行:  python ch09_designer_app.py
"""

import sys

from PySide6.QtWidgets import QApplication, QWidget

from ui_ch09_form import Ui_ProfileForm


class ProfileForm(QWidget, Ui_ProfileForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)          # ここで .ui の中身が self の上に組み立てられる

        # .ui で付けた objectName が、そのまま属性名になる。
        self.submitButton.clicked.connect(self.on_submit)
        self.agreeCheck.toggled.connect(self.submitButton.setEnabled)
        self.submitButton.setEnabled(False)

    def on_submit(self):
        name = self.nameEdit.text() or "ななし"
        plan = self.planCombo.currentText()
        self.resultLabel.setText(f"{name} さんを「{plan}」で受け付けました")


app = QApplication(sys.argv)
form = ProfileForm()
form.show()
sys.exit(app.exec())
