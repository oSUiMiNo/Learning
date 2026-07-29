"""QSortFilterProxyModel — 元データを触らずに、並べ替えと絞り込みをする。

    元モデル → プロキシ → ビュー

と、あいだに 1 枚はさむだけ。元モデルには一切手を入れない。

実行:  python ch10_filter.py
"""

import sys

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import (QApplication, QLineEdit, QTableView,
                               QVBoxLayout, QWidget)

from ch10_tableview import FRUITS, FruitModel

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("並べ替えと絞り込み")
window.resize(430, 280)

source = FruitModel(FRUITS)

proxy = QSortFilterProxyModel()
proxy.setSourceModel(source)                       # ① 元モデルを包む
proxy.setFilterKeyColumn(-1)                       # ② -1 = すべての列を検索対象に
proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

view = QTableView()
view.setModel(proxy)                               # ③ ビューにはプロキシを渡す
view.setSortingEnabled(True)                       # 見出しクリックで並べ替え
view.sortByColumn(1, Qt.SortOrder.AscendingOrder)
view.horizontalHeader().setStretchLastSection(True)
view.setAlternatingRowColors(True)

search = QLineEdit()
search.setObjectName("filterEdit")
search.setPlaceholderText("絞り込み（品名・産地で検索）")
search.setClearButtonEnabled(True)
# 入力のたびにフィルタを更新する。
search.textChanged.connect(proxy.setFilterFixedString)

layout = QVBoxLayout(window)
layout.addWidget(search)
layout.addWidget(view)

window.show()

sys.exit(app.exec())
