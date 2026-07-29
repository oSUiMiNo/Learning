"""実践 — 保存できる ToDo アプリ。

この教材で扱ったものが一通り入っている。
    QMainWindow / レイアウト / シグナルとスロット / 自作モデル
    / ダイアログ / メニューとツールバー / ステータスバー / 終了時の保存

実行:  python ch12_todo_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import (QAbstractListModel, QModelIndex, QStandardPaths,
                            Qt, Signal)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
                               QListView, QMainWindow, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget)


def save_path() -> Path:
    """OS ごとの「アプリがデータを置いてよい場所」を Qt に聞く。"""
    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation)
    folder = Path(base) / "qt6-widgets-todo"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "todo.json"


class TodoModel(QAbstractListModel):
    """[{"text": ..., "done": bool}, ...] を、チェック付きリストとして見せる。"""

    changed = Signal()      # 件数表示を更新してもらうための自作シグナル

    def __init__(self, items: list[dict] | None = None):
        super().__init__()
        self._items = items or []

    # --- ビューから聞かれること ------------------------------------------
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._items)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        item = self._items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item["text"]
        if role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked if item["done"] else Qt.CheckState.Unchecked
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """チェックできる・選べる、という「この項目にできること」を宣言する。"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return (Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable)

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        """ビュー側での操作（チェックの付け外し）を受け取る。"""
        if role != Qt.ItemDataRole.CheckStateRole or not index.isValid():
            return False
        # ここに渡ってくる value は int（Checked なら 2）。
        # Qt.CheckState() で包み直してから比較する。
        self._items[index.row()]["done"] = (
            Qt.CheckState(value) == Qt.CheckState.Checked)
        # 「ここが変わった」とビューに知らせる。これを忘れると画面が更新されない。
        self.dataChanged.emit(index, index, [role])
        self.changed.emit()
        return True

    # --- アプリ側から呼ぶ操作 --------------------------------------------
    def add(self, text: str) -> None:
        # 行の増減は begin... / end... で挟む決まり。挟まないと表示が壊れる。
        row = len(self._items)
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append({"text": text, "done": False})
        self.endInsertRows()
        self.changed.emit()

    def remove_done(self) -> int:
        remaining = [i for i in self._items if not i["done"]]
        removed = len(self._items) - len(remaining)
        if removed:
            self.beginResetModel()          # 全面的に作り替えるときはこれ
            self._items = remaining
            self.endResetModel()
            self.changed.emit()
        return removed

    def counts(self) -> tuple[int, int]:
        return sum(1 for i in self._items if i["done"]), len(self._items)

    def to_list(self) -> list[dict]:
        return self._items


class TodoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("やることリスト")
        self.resize(460, 340)

        self.model = TodoModel(self.load())
        self.model.changed.connect(self.update_status)

        # --- 中央: 入力欄 + 一覧 ------------------------------------------
        central = QWidget()
        outer = QVBoxLayout(central)

        self.input = QLineEdit()
        self.input.setObjectName("inputEdit")
        self.input.setPlaceholderText("やることを入力して Enter")
        self.input.returnPressed.connect(self.add_item)

        add_button = QPushButton("追加")
        add_button.setObjectName("addButton")
        add_button.clicked.connect(self.add_item)

        row = QHBoxLayout()
        row.addWidget(self.input, 1)
        row.addWidget(add_button)
        outer.addLayout(row)

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setAlternatingRowColors(True)
        outer.addWidget(self.view, 1)

        self.setCentralWidget(central)

        # --- 操作の定義 ----------------------------------------------------
        clear_action = QAction("完了した項目を削除", self)
        clear_action.setObjectName("clearAction")
        clear_action.triggered.connect(self.clear_done)

        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save)

        quit_action = QAction("終了", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)

        menu = self.menuBar().addMenu("ファイル(&F)")
        menu.addAction(save_action)
        menu.addAction(clear_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        toolbar = self.addToolBar("操作")
        toolbar.addAction(clear_action)

        # --- ステータスバー -------------------------------------------------
        self.counter = QLabel()
        self.statusBar().addPermanentWidget(self.counter)
        self.update_status()

    # --- 動作 ---------------------------------------------------------------
    def add_item(self):
        text = self.input.text().strip()
        if not text:
            return
        self.model.add(text)
        self.input.clear()

    def clear_done(self):
        done, _ = self.model.counts()
        if not done:
            QMessageBox.information(self, "やることリスト", "完了済みの項目はありません。")
            return
        answer = QMessageBox.question(
            self, "確認", f"完了済みの {done} 件を削除します。よろしいですか？")
        if answer == QMessageBox.StandardButton.Yes:
            removed = self.model.remove_done()
            self.statusBar().showMessage(f"{removed} 件を削除しました", 3000)

    def update_status(self):
        done, total = self.model.counts()
        self.counter.setText(f"完了 {done} / 全 {total} 件")

    # --- 保存と読み込み -----------------------------------------------------
    def load(self) -> list[dict]:
        path = save_path()
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []      # 壊れていても起動できなくならないようにする

    def save(self):
        save_path().write_text(
            json.dumps(self.model.to_list(), ensure_ascii=False, indent=2),
            encoding="utf-8")
        self.statusBar().showMessage("保存しました", 2000)

    def closeEvent(self, event):
        """閉じる直前に呼ばれる。ここで保存しておけば取りこぼしがない。"""
        self.save()
        super().closeEvent(event)


app = QApplication(sys.argv)
window = TodoWindow()
window.show()
sys.exit(app.exec())
