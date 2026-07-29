"""QMessageBox と QFileDialog — 1 行で呼べる標準ダイアログ。

実行:  python ch08_messagebox.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QFileDialog, QInputDialog, QLabel,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("標準ダイアログ")
        self.resize(400, 230)

        self.result = QLabel("―")
        layout = QVBoxLayout(self)

        info = QPushButton("お知らせを出す")
        info.clicked.connect(self.show_info)
        layout.addWidget(info)

        ask = QPushButton("はい / いいえ を聞く")
        ask.setObjectName("askButton")
        ask.clicked.connect(self.ask)
        layout.addWidget(ask)

        pick = QPushButton("ファイルを選ばせる")
        pick.clicked.connect(self.pick_file)
        layout.addWidget(pick)

        text = QPushButton("文字列を入力させる")
        text.clicked.connect(self.ask_text)
        layout.addWidget(text)

        layout.addWidget(self.result)

    def show_info(self):
        QMessageBox.information(self, "お知らせ", "処理が完了しました。")
        self.result.setText("お知らせを表示しました")

    def ask(self):
        # 戻り値は「どのボタンが押されたか」。
        answer = QMessageBox.question(
            self,
            "確認",
            "保存していない変更があります。\n本当に閉じますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,      # 既定で選ばれるボタン
        )
        chosen = "はい" if answer == QMessageBox.StandardButton.Yes else "いいえ"
        self.result.setText(f"「{chosen}」が選ばれました")

    def pick_file(self):
        # 戻り値は (選ばれたパス, 選ばれたフィルタ) のタプル。
        path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選ぶ", "", "テキスト (*.txt *.md);;すべて (*)")
        self.result.setText(path or "選択はキャンセルされました")

    def ask_text(self):
        # 戻り値は (入力された文字列, OK が押されたか) のタプル。
        text, ok = QInputDialog.getText(self, "入力", "お名前は？")
        self.result.setText(f"入力: {text}" if ok else "入力はキャンセルされました")


app = QApplication(sys.argv)
demo = Demo()
demo.show()
sys.exit(app.exec())
