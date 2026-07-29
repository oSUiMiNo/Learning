"""自作ダイアログ — QDialog を継承して、入力を受け取る窓を作る。

QDialogButtonBox を使うと、［OK］［キャンセル］の並び順を
OS の作法に合わせて自動で決めてくれる。

実行:  python ch08_custom_dialog.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
                               QFormLayout, QLabel, QLineEdit, QPushButton,
                               QSpinBox, QVBoxLayout, QWidget)


class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("プロフィールの編集")
        self.setMinimumWidth(320)

        self.name = QLineEdit("山田 太郎")
        self.age = QSpinBox()
        self.age.setRange(0, 120)
        self.age.setValue(28)
        self.age.setSuffix(" 歳")

        form = QFormLayout()
        form.addRow("お名前", self.name)
        form.addRow("年齢", self.age)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # accept() / reject() は QDialog が最初から持っているスロット。
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, int]:
        """呼び出し側が結果を取り出すための窓口。"""
        return self.name.text(), self.age.value()


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自作ダイアログを呼ぶ")
        self.resize(480, 260)

        self.label = QLabel("まだ編集されていません")
        button = QPushButton("プロフィールを編集…")
        button.setObjectName("openButton")
        button.clicked.connect(self.edit_profile)

        layout = QVBoxLayout(self)
        layout.addWidget(button)
        layout.addWidget(self.label)

    def edit_profile(self):
        dialog = ProfileDialog(self)
        # exec() は「閉じられるまでここで待つ」。戻り値で OK かどうかが分かる。
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, age = dialog.values()
            self.label.setText(f"{name}（{age} 歳）に更新しました")
        else:
            self.label.setText("編集はキャンセルされました")


app = QApplication(sys.argv)
main = Main()
main.show()
sys.exit(app.exec())
