"""QMainWindow — メニュー・ツールバー・ステータスバーを備えた本格的な窓。

QWidget との違いは「あらかじめ場所が用意されている」こと。
中央には setCentralWidget() で好きなウィジェットを置く。

実行:  python ch06_mainwindow.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence  # ★ Qt6 では QAction は QtGui にある
from PySide6.QtWidgets import (QApplication, QDockWidget, QLabel, QListWidget,
                               QMainWindow, QPlainTextEdit, QToolBar)


class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("メモ帳もどき — QMainWindow の全体像")
        self.resize(620, 380)

        # --- 中央: 主役になるウィジェットをひとつ置く ---------------------
        self.text = QPlainTextEdit()
        self.text.setPlainText(
            "ここが中央ウィジェット（setCentralWidget）。\n"
            "上にメニューとツールバー、左にドック、下にステータスバーがある。"
        )
        self.setCentralWidget(self.text)

        # --- 動作の定義: QAction にまとめる -------------------------------
        # 同じ「開く」をメニューにもツールバーにも置けるのが QAction の利点。
        open_action = QAction("開く", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)  # Ctrl+O / ⌘O
        open_action.setStatusTip("ファイルを開きます")
        open_action.triggered.connect(lambda: self.statusBar().showMessage("「開く」が実行されました", 3000))

        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(lambda: self.statusBar().showMessage("保存しました", 3000))

        quit_action = QAction("終了", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)

        about_action = QAction("このアプリについて", self)
        about_action.setObjectName("aboutAction")   # 教材の自動撮影で使う名前
        about_action.triggered.connect(
            lambda: self.statusBar().showMessage("Qt Widgets で作られたサンプルです", 5000))

        # --- メニューバー -------------------------------------------------
        file_menu = self.menuBar().addMenu("ファイル(&F)")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        help_menu = self.menuBar().addMenu("ヘルプ(&H)")
        help_menu.addAction(about_action)

        # --- ツールバー ---------------------------------------------------
        toolbar = QToolBar("主なツール")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        self.addToolBar(toolbar)

        # --- ドック（切り離せる脇のパネル） -------------------------------
        dock = QDockWidget("最近使ったファイル", self)
        recent = QListWidget()
        recent.addItems(["memo.txt", "日報.md", "買い物メモ.txt"])
        dock.setWidget(recent)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        # --- ステータスバー -----------------------------------------------
        self.statusBar().showMessage("準備完了")
        self.statusBar().addPermanentWidget(QLabel("UTF-8"))  # 右端に常駐する表示


app = QApplication(sys.argv)
window = Editor()
window.show()
sys.exit(app.exec())
