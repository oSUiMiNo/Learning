"""モデル / ビュー — QTableView に自作モデルをつなぐ。

覚えることは 4 つだけ。
    rowCount()    行はいくつ？
    columnCount() 列はいくつ？
    data()        その升目に何を表示する？
    headerData()  見出しに何を表示する？

実行:  python ch10_tableview.py
"""

import sys

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget

# 表示したいデータ。ただの Python のリスト。
FRUITS = [
    ["りんご", 180, "青森"],
    ["みかん", 120, "愛媛"],
    ["ぶどう", 480, "山梨"],
    ["もも", 350, "山梨"],
    ["メロン", 1200, "茨城"],
]
HEADERS = ["品名", "価格", "産地"]


class FruitModel(QAbstractTableModel):
    """リストのリストを、表として見せるための「通訳」。"""

    def __init__(self, rows):
        super().__init__()
        self._rows = rows

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(HEADERS)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        value = self._rows[index.row()][index.column()]

        # role は「何を聞かれているか」。表示文字列かもしれないし、色かもしれない。
        if role == Qt.ItemDataRole.DisplayRole:
            return f"¥{value:,}" if index.column() == 1 else str(value)

        # 価格の列だけ右揃えにする。
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 1:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return HEADERS[section]
        return section + 1        # 行番号


# このファイルは次のサンプル (ch10_filter.py) から import して再利用する。
# import されたときにアプリまで起動してしまわないよう、
# 「直接実行されたときだけ動かす」お決まりの書き方で囲っておく。
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("QTableView + 自作モデル")
    window.resize(430, 230)

    view = QTableView()
    view.setModel(FruitModel(FRUITS))      # ★ ここでデータと見た目がつながる
    view.horizontalHeader().setStretchLastSection(True)
    view.setAlternatingRowColors(True)

    layout = QVBoxLayout(window)
    layout.addWidget(view)

    window.show()

    sys.exit(app.exec())
