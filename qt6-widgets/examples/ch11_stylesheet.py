"""Qt Style Sheets — CSS によく似た書き方で見た目を変える。

セレクタはクラス名 (QPushButton)、id (#saveButton)、
状態 (:hover, :disabled) が使える。

実行:  python ch11_stylesheet.py
"""

import sys

from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
                               QVBoxLayout, QWidget)

STYLE = """
QWidget {
    background: #f4f6f8;
    font-size: 14px;
}

QLabel#heading {
    font-size: 20px;
    font-weight: bold;
    color: #1b3a4b;
    padding-bottom: 4px;
}

QLineEdit {
    background: white;
    border: 1px solid #c3ccd5;
    border-radius: 6px;
    padding: 7px 10px;
    selection-background-color: #41cd52;
}
QLineEdit:focus {
    border-color: #41cd52;
}

QPushButton {
    background: #41cd52;
    color: #06340f;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton:hover   { background: #5adb6a; }
QPushButton:pressed { background: #33a642; }
QPushButton:disabled {
    background: #d7dde3;
    color: #97a3ae;
}

/* id で 1 つだけを狙い撃ちする */
QPushButton#secondary {
    background: transparent;
    color: #2f6f3c;
    border: 1px solid #9fd8a8;
}
"""

app = QApplication(sys.argv)
app.setStyleSheet(STYLE)      # アプリ全体に適用（ウィジェット単位でも設定できる）

window = QWidget()
window.setWindowTitle("Qt Style Sheets")
window.resize(400, 240)

heading = QLabel("ログイン")
heading.setObjectName("heading")

user = QLineEdit()
user.setPlaceholderText("ユーザー名")
password = QLineEdit()
password.setPlaceholderText("パスワード")
password.setEchoMode(QLineEdit.EchoMode.Password)

login = QPushButton("ログイン")

secondary = QPushButton("パスワードを忘れた")
secondary.setObjectName("secondary")

disabled = QPushButton("いまは使えないボタン")
disabled.setEnabled(False)

layout = QVBoxLayout(window)
layout.setContentsMargins(24, 20, 24, 20)
layout.setSpacing(10)
for widget in (heading, user, password, login, secondary, disabled):
    layout.addWidget(widget)

window.show()

sys.exit(app.exec())
